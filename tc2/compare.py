"""Compare two mutation runs of the same target (for example baseline vs after-tests).

Mutants are matched by file, position, mutator and replacement rather than by id, so the table stays
correct even if ids are renumbered. Writes a Markdown report.

Usage: python -m tc2 compare <before-dir> <after-dir> [--reviewed data/reviewed/<target>.csv] [--out FILE]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .summarize import compute_counts, fmt_score, iter_mutants, load_report, load_verdicts


def mutant_key(file_name: str, mutant: dict) -> tuple:
    start = mutant["location"]["start"]
    return (file_name, start["line"], start["column"], mutant["mutatorName"], mutant.get("replacement") or "")


def statuses(report: dict) -> dict[tuple, tuple[str, str]]:
    """Key -> (mutant id, status), skipping mutants outside the mutate scope."""
    return {
        mutant_key(f, m): (str(m["id"]), m["status"])
        for f, _, m in iter_mutants(report)
        if m["status"] != "Ignored"
    }


def changed_mutants(before: dict, after: dict) -> list[dict]:
    b, a = statuses(before), statuses(after)
    rows = []
    for key in sorted(set(b) | set(a), key=lambda k: (k[0], k[1], k[2], k[3])):
        old, new = b.get(key), a.get(key)
        if old and new and old[1] == new[1]:
            continue
        rows.append({
            "file": key[0], "line": key[1], "mutator": key[3],
            "id": (new or old)[0],
            "before": old[1] if old else "absent",
            "after": new[1] if new else "absent",
        })
    return rows


def run_label(path: Path) -> str:
    info_path = path / "run.json"
    if not info_path.exists():
        return path.name
    info = json.loads(info_path.read_text(encoding="utf-8"))
    added = len(info.get("added_tests") or [])
    return f"{path.name} ({info.get('duration_s')} s, {added} added test files)"


def render(before_dir: Path, after_dir: Path, reviewed: Path | None) -> str:
    before, after = load_report(before_dir / "mutation.json"), load_report(after_dir / "mutation.json")
    verdicts = load_verdicts(reviewed)
    sb, sa = compute_counts(before, verdicts), compute_counts(after, verdicts)
    lines = [
        "# Mutation run comparison", "",
        f"- Before: `{run_label(before_dir)}`",
        f"- After: `{run_label(after_dir)}`", "",
        "| Metric | Before | After |", "| --- | --- | --- |",
        f"| Score (detected / valid) | {fmt_score(sb['detected'], sb['valid'])} | {fmt_score(sa['detected'], sa['valid'])} |",
        f"| Excluding reviewed equivalents | {fmt_score(sb['detected'], sb['valid'] - sb['equivalent'])} "
        f"| {fmt_score(sa['detected'], sa['valid'] - sa['equivalent'])} |",
    ]
    for status in ["Killed", "Timeout", "Survived", "NoCoverage", "CompileError", "RuntimeError"]:
        lines.append(f"| {status} | {sb['counts'].get(status, 0)} | {sa['counts'].get(status, 0)} |")
    lines += ["", "## Mutants that changed status", ""]
    rows = changed_mutants(before, after)
    if not rows:
        lines.append("None.")
    else:
        lines += ["| Id | File | Line | Mutator | Before | After | Verdict |", "| --- | --- | ---: | --- | --- | --- | --- |"]
        for r in rows:
            verdict = verdicts.get((r["file"], r["id"]), "")
            lines.append(f"| {r['id']} | `{r['file']}` | {r['line']} | {r['mutator']} | {r['before']} | {r['after']} | {verdict} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tc2 compare", description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--reviewed", type=Path)
    parser.add_argument("--out", type=Path, help="write the report here instead of stdout")
    args = parser.parse_args(argv)
    text = render(args.before, args.after, args.reviewed)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)
    return 0
