from __future__ import annotations

import csv
import json

import pytest

from tc2 import summarize

SOURCE = "export function up(a, b) {\n  return a > b ? a : b;\n}\n"


def loc(line, start_col, end_col):
    return {"start": {"line": line, "column": start_col}, "end": {"line": line, "column": end_col}}


def make_report():
    mutants = [
        {"id": "1", "mutatorName": "EqualityOperator", "replacement": "a >= b",
         "location": loc(2, 10, 15), "status": "Survived", "coveredBy": ["t1"]},
        {"id": "2", "mutatorName": "ConditionalExpression", "replacement": "true",
         "location": loc(2, 10, 15), "status": "Killed", "coveredBy": ["t1"]},
        {"id": "3", "mutatorName": "BlockStatement", "replacement": "{}",
         "location": loc(1, 26, 27), "status": "NoCoverage"},
        {"id": "4", "mutatorName": "ConditionalExpression", "replacement": "false",
         "location": loc(2, 10, 15), "status": "Timeout"},
        {"id": "5", "mutatorName": "StringLiteral", "replacement": "\"\"",
         "location": loc(2, 3, 9), "status": "CompileError"},
    ]
    return {
        "schemaVersion": "2",
        "files": {"src/up.ts": {"language": "typescript", "source": SOURCE, "mutants": mutants}},
        "testFiles": {"src/up.test.ts": {"tests": [{"id": "t1", "name": "up returns the max"}]}},
    }


def test_counts_separate_invalid_and_timeouts():
    stats = summarize.compute_counts(make_report())
    assert stats["total"] == 5
    assert stats["counts"]["CompileError"] == 1
    assert stats["detected"] == 2  # killed + timeout
    assert stats["valid"] == 4  # compile error excluded
    assert stats["covered"] == 3  # no-coverage excluded
    assert stats["score"] == pytest.approx(0.5)


def test_reviewed_equivalent_is_removed_from_denominator():
    verdicts = {("src/up.ts", "1"): "equivalent"}
    stats = summarize.compute_counts(make_report(), verdicts)
    assert stats["equivalent"] == 1
    assert stats["score_excl_equivalent"] == pytest.approx(2 / 3)


def test_survivor_rows_only_review_statuses_with_source_and_tests():
    rows = summarize.survivor_rows(make_report())
    assert [r["mutant_id"] for r in rows] == ["3", "1"]  # sorted by line
    survived = rows[1]
    assert survived["original"] == "a > b"
    assert survived["replacement"] == "a >= b"
    assert survived["covering_tests"] == "up returns the max"
    assert rows[0]["covering_tests"] == ""


def test_multiline_snippet_is_collapsed():
    location = {"start": {"line": 1, "column": 26}, "end": {"line": 3, "column": 2}}
    assert summarize.source_snippet(SOURCE, location) == "{ return a > b ? a : b; }"


def test_unknown_verdict_is_rejected(tmp_path):
    path = tmp_path / "reviewed.csv"
    path.write_text("mutant_id,file,verdict\n1,src/up.ts,maybe\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        summarize.load_verdicts(path)


def test_summarize_dir_writes_outputs(tmp_path):
    (tmp_path / "mutation.json").write_text(json.dumps(make_report()), encoding="utf-8")
    reviewed = tmp_path / "reviewed.csv"
    reviewed.write_text("mutant_id,file,verdict\n1,src/up.ts,real_gap\n", encoding="utf-8")

    summarize.summarize_dir(tmp_path, reviewed)

    summary = (tmp_path / "summary.md").read_text(encoding="utf-8")
    assert "2/4 = 50.0%" in summary
    assert "| CompileError | 1 |" in summary
    with (tmp_path / "survivors.csv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[1]["verdict"] == "real_gap"
