from __future__ import annotations

import pytest

from tc2.run import apply_test_patch, remove_test_patch


def test_patch_is_added_then_removed(tmp_path):
    patch = tmp_path / "patch"
    target = tmp_path / "target"
    (patch / "src" / "__tests__").mkdir(parents=True)
    (patch / "src" / "__tests__" / "new.test.ts").write_text("it('x', () => {});\n", encoding="utf-8")
    (target / "src").mkdir(parents=True)

    added = apply_test_patch(patch, target)

    assert [a["path"] for a in added] == ["src/__tests__/new.test.ts"]
    assert len(added[0]["sha256"]) == 64
    assert (target / "src" / "__tests__" / "new.test.ts").exists()

    remove_test_patch(added, target)
    assert not (target / "src" / "__tests__" / "new.test.ts").exists()
    assert (target / "src").exists()


def test_patch_refuses_to_overwrite(tmp_path):
    patch = tmp_path / "patch"
    target = tmp_path / "target"
    patch.mkdir()
    target.mkdir()
    (patch / "a.cs").write_text("new", encoding="utf-8")
    (target / "a.cs").write_text("original", encoding="utf-8")

    with pytest.raises(SystemExit):
        apply_test_patch(patch, target)
    assert (target / "a.cs").read_text(encoding="utf-8") == "original"


def test_empty_patch_is_rejected(tmp_path):
    (tmp_path / "patch").mkdir()
    with pytest.raises(SystemExit):
        apply_test_patch(tmp_path / "patch", tmp_path)
