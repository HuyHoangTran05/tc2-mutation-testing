from __future__ import annotations

import copy
import json

from tc2 import compare
from tests.test_summarize import make_report


def test_changed_mutants_matches_by_position_not_id():
    before = make_report()
    after = copy.deepcopy(before)
    for mutant in after["files"]["src/up.ts"]["mutants"]:
        mutant["id"] = str(100 + int(mutant["id"]))  # renumbered ids
    after["files"]["src/up.ts"]["mutants"][0]["status"] = "Killed"  # the survivor is now killed

    rows = compare.changed_mutants(before, after)

    assert rows == [{
        "file": "src/up.ts", "line": 2, "mutator": "EqualityOperator",
        "id": "101", "before": "Survived", "after": "Killed",
    }]


def test_render_reports_scores_and_changes(tmp_path):
    before_dir, after_dir = tmp_path / "before", tmp_path / "after"
    before_dir.mkdir()
    after_dir.mkdir()
    before = make_report()
    after = copy.deepcopy(before)
    after["files"]["src/up.ts"]["mutants"][2]["status"] = "Killed"  # NoCoverage -> Killed
    (before_dir / "mutation.json").write_text(json.dumps(before), encoding="utf-8")
    (after_dir / "mutation.json").write_text(json.dumps(after), encoding="utf-8")
    (after_dir / "run.json").write_text(json.dumps({"duration_s": 3.5, "added_tests": [{"path": "x"}]}), encoding="utf-8")

    text = compare.render(before_dir, after_dir, None)

    assert "| Score (detected / valid) | 2/4 = 50.0% | 3/4 = 75.0% |" in text
    assert "3.5 s, 1 added test files" in text
    assert "| 3 | `src/up.ts` | 1 | BlockStatement | NoCoverage | Killed |  |" in text


def test_render_without_changes(tmp_path):
    for name in ("a", "b"):
        (tmp_path / name).mkdir()
        (tmp_path / name / "mutation.json").write_text(json.dumps(make_report()), encoding="utf-8")
    assert "None." in compare.render(tmp_path / "a", tmp_path / "b", None)
