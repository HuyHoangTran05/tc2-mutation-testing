"""TC2 mutation testing pilot CLI.

Usage: python -m tc2 <command> [args]

Commands:
  setup      clone a target at its pinned commit and install Stryker
  run        run Stryker and store the report with tool versions
  summarize  rebuild summary.md and survivors.csv for a results folder
  compare    before/after table for two runs of the same target
"""

from __future__ import annotations

import importlib
import sys

COMMANDS = ["setup", "run", "summarize", "compare"]


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in COMMANDS:
        print(__doc__)
        return 0 if not argv else 2
    module = importlib.import_module(f"tc2.{argv[0]}")
    return module.main(argv[1:])


if __name__ == "__main__":
    sys.exit(main())
