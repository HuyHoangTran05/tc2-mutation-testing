"""Summarize a Stryker mutation report (mutation-testing-elements JSON, used by StrykerJS and Stryker.NET).

Writes summary.md and survivors.csv next to the report. Scores always show their denominators;
invalid mutants (compile/runtime errors), timeouts and reviewed equivalents are reported separately.

Usage: python -m tc2 summarize <results-dir> [--reviewed data/reviewed/<target>.csv]
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

STATUSES = ["Killed", "Survived", "NoCoverage", "Timeout", "CompileError", "RuntimeError", "Ignored"]
INVALID = {"CompileError", "RuntimeError"}
REVIEW_STATUSES = {"Survived", "NoCoverage"}
CSV_FIELDS = [
    "mutant_id", "status", "file", "line", "mutator", "original", "replacement",
    "covering_tests", "verdict", "reason", "mentor_confirmed",
]
VERDICTS = {"real_gap", "equivalent", "not_worth", ""}


def load_report(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_mutants(report: dict):
    for file_name, info in report["files"].items():
        for mutant in info["mutants"]:
            yield file_name, info, mutant


def source_snippet(source: str, location: dict) -> str:
    """Text covered by a mutant location (1-based lines and columns), collapsed to one line."""
    lines = source.splitlines()
    start, end = location["start"], location["end"]
    if start["line"] == end["line"]:
        text = lines[start["line"] - 1][start["column"] - 1:end["column"] - 1]
    else:
        parts = [lines[start["line"] - 1][start["column"] - 1:]]
        parts += lines[start["line"]:end["line"] - 1]
        parts.append(lines[end["line"] - 1][:end["column"] - 1])
        text = "\n".join(parts)
    return " ".join(text.split())


def test_names(report: dict) -> dict[str, str]:
    names = {}
    for info in (report.get("testFiles") or {}).values():
        for test in info.get("tests", []):
            names[test["id"]] = test["name"]
    return names


def load_verdicts(path: Path | None) -> dict[tuple[str, str], str]:
    """Map (file, mutant_id) -> verdict from a reviewed survivors CSV."""
    if not path or not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    verdicts = {}
    for row in rows:
        verdict = row.get("verdict", "").strip()
        if verdict not in VERDICTS:
            raise SystemExit(f"{path}: unknown verdict '{verdict}' for mutant {row['mutant_id']}")
        verdicts[(row["file"], row["mutant_id"])] = verdict
    return verdicts


def compute_counts(report: dict, verdicts: dict[tuple[str, str], str] | None = None) -> dict:
    verdicts = verdicts or {}
    counts = Counter()
    per_file: dict[str, Counter] = {}
    equivalent = 0
    for file_name, _, mutant in iter_mutants(report):
        status = mutant["status"]
        counts[status] += 1
        per_file.setdefault(file_name, Counter())[status] += 1
        if status in REVIEW_STATUSES and verdicts.get((file_name, str(mutant["id"]))) == "equivalent":
            equivalent += 1
    total = sum(counts.values())
    detected = counts["Killed"] + counts["Timeout"]
    valid = total - sum(counts[s] for s in INVALID) - counts["Ignored"]
    covered = valid - counts["NoCoverage"]
    return {
        "total": total,
        "counts": dict(counts),
        "per_file": {f: dict(c) for f, c in sorted(per_file.items())},
        "detected": detected,
        "valid": valid,
        "covered": covered,
        "equivalent": equivalent,
        "score": ratio(detected, valid),
        "score_covered": ratio(detected, covered),
        "score_excl_equivalent": ratio(detected, valid - equivalent),
    }


def ratio(num: int, den: int) -> float | None:
    return num / den if den else None


def fmt_score(num: int, den: int) -> str:
    return f"{num}/{den} = {num / den:.1%}" if den else f"{num}/0 = n/a"


def survivor_rows(report: dict, verdicts: dict[tuple[str, str], str] | None = None) -> list[dict]:
    verdicts = verdicts or {}
    names = test_names(report)
    rows = []
    for file_name, info, mutant in iter_mutants(report):
        if mutant["status"] not in REVIEW_STATUSES:
            continue
        covered_by = mutant.get("coveredBy") or []
        rows.append({
            "mutant_id": str(mutant["id"]),
            "status": mutant["status"],
            "file": file_name,
            "line": mutant["location"]["start"]["line"],
            "mutator": mutant["mutatorName"],
            "original": source_snippet(info["source"], mutant["location"]),
            "replacement": " ".join((mutant.get("replacement") or "").split()),
            "covering_tests": "; ".join(names.get(t, t) for t in covered_by),
            "verdict": verdicts.get((file_name, str(mutant["id"])), ""),
            "reason": "",
            "mentor_confirmed": "",
        })
    rows.sort(key=lambda r: (r["file"], r["line"], r["mutant_id"]))
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def render_summary(stats: dict, run_info: dict | None = None) -> str:
    c = stats["counts"]
    lines = ["# Mutation run summary", ""]
    if run_info:
        lines += [
            f"- Target: `{run_info.get('target')}` @ `{run_info.get('commit', '')[:10]}`",
            f"- Started: {run_info.get('started')}, duration {run_info.get('duration_s')} s, exit code {run_info.get('exit_code')}",
            "",
        ]
    lines += [
        "## Scores",
        "",
        f"- Mutation score (killed + timeout) / valid: {fmt_score(stats['detected'], stats['valid'])}",
        f"- Score on covered code (excludes NoCoverage): {fmt_score(stats['detected'], stats['covered'])}",
        f"- Excluding reviewed equivalents ({stats['equivalent']}): "
        f"{fmt_score(stats['detected'], stats['valid'] - stats['equivalent'])}",
        "",
        "Timeouts count as detected (Stryker's convention) but are listed separately below.",
        "",
        "## Status counts",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    lines += [f"| {s} | {c.get(s, 0)} |" for s in STATUSES]
    lines += [f"| **Total** | **{stats['total']}** |", "", "## Per file", ""]
    lines += ["| File | " + " | ".join(STATUSES) + " |", "| --- |" + " ---: |" * len(STATUSES)]
    for file_name, fc in stats["per_file"].items():
        if set(fc) == {"Ignored"}:
            continue  # outside the mutate scope (Stryker.NET lists every file)
        lines.append(f"| `{file_name}` | " + " | ".join(str(fc.get(s, 0)) for s in STATUSES) + " |")
    return "\n".join(lines) + "\n"


def summarize_dir(results_dir: Path, reviewed: Path | None = None) -> dict:
    report = load_report(results_dir / "mutation.json")
    run_path = results_dir / "run.json"
    run_info = json.loads(run_path.read_text(encoding="utf-8")) if run_path.exists() else None
    verdicts = load_verdicts(reviewed)
    stats = compute_counts(report, verdicts)
    (results_dir / "summary.md").write_text(render_summary(stats, run_info), encoding="utf-8")
    write_csv(survivor_rows(report, verdicts), results_dir / "survivors.csv")
    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tc2 summarize", description=__doc__)
    parser.add_argument("results_dir", type=Path)
    parser.add_argument("--reviewed", type=Path, help="reviewed survivors CSV with verdicts")
    args = parser.parse_args(argv)
    stats = summarize_dir(args.results_dir, args.reviewed)
    print(f"score {fmt_score(stats['detected'], stats['valid'])}; counts {stats['counts']}")
    print(f"wrote {args.results_dir / 'summary.md'} and survivors.csv")
    return 0
