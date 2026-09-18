"""Build demo/data.json from real results/ and data/reviewed/ files for the local demo page.

Reuses tc2.summarize so the demo never restates numbers by hand. Read-only: it does not
touch results/ or data/reviewed/.

Usage: python3 demo/build_data.py
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tc2.summarize import compute_counts, load_report  # noqa: E402

RUNS = {
    "dinero": {
        "business_rule": "Money arithmetic, comparison, scaling, rounding modes and allocation across ratios",
        "baseline_dir": "20260917-150724-dinero-baseline-repeat1",
        "baseline_label": "Baseline (lần chạy lặp lại, dùng làm mốc ổn định)",
        "after_dir": "20260918-142527-dinero-after-tests",
        "reviewed_csv": "dinero.csv",
    },
    "stateless": {
        "business_rule": "Allowed state transitions: guards, ignored triggers and reentry",
        "baseline_dir": "20260917-145311-stateless-baseline",
        "baseline_label": "Baseline",
        "after_dir": "20260918-142647-stateless-after-tests",
        "reviewed_csv": "stateless.csv",
    },
}

STATUS_GROUPS = [
    ("Killed", "good"),
    ("Timeout", "good"),
    ("Survived", "critical"),
    ("NoCoverage", "serious"),
    ("CompileError", "muted"),
    ("RuntimeError", "muted"),
]


def run_stats(results_dir: Path) -> dict:
    report = load_report(results_dir / "mutation.json")
    run_info = json.loads((results_dir / "run.json").read_text(encoding="utf-8"))
    stats = compute_counts(report)
    return {
        "label": results_dir.name,
        "score": stats["score"],
        "detected": stats["detected"],
        "valid": stats["valid"],
        "counts": stats["counts"],
        "duration_s": run_info["duration_s"],
        "added_tests": len(run_info.get("added_tests") or []),
    }


def verdict_counts(csv_path: Path) -> dict:
    with csv_path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    counts = Counter(r["verdict"] for r in rows if r["verdict"])
    return dict(counts)


def build() -> dict:
    targets = {}
    for name, cfg in RUNS.items():
        baseline = run_stats(ROOT / "results" / cfg["baseline_dir"])
        after = run_stats(ROOT / "results" / cfg["after_dir"])
        baseline["label"] = cfg["baseline_label"]
        after["label"] = "Sau khi thêm test (after-tests, mentor đã xác nhận)"
        targets[name] = {
            "business_rule": cfg["business_rule"],
            "baseline": baseline,
            "after": after,
            "verdicts": verdict_counts(ROOT / "data" / "reviewed" / cfg["reviewed_csv"]),
        }
    return {"generated_from": "results/ and data/reviewed/ in this repo", "targets": targets}


def main() -> int:
    data = build()
    out_path = Path(__file__).resolve().parent / "data.json"
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
