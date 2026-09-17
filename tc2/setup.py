"""Clone a target at its pinned commit and install its dependencies plus Stryker.

Usage: python -m tc2 setup <target> [--skip-install]
"""

from __future__ import annotations

import argparse

from .common import Target, capture, get_target, run, tool


def checkout(target: Target) -> None:
    git = tool("git")
    if not (target.dir / ".git").exists():
        target.dir.mkdir(parents=True, exist_ok=True)
        run([git, "init", "-q"], target.dir)
        run([git, "remote", "add", "origin", target.repo], target.dir)
    head = capture([git, "rev-parse", "HEAD"], target.dir)
    if head == target.commit:
        print(f"{target.name}: already at {target.commit[:10]}")
        return
    # GitHub allows fetching a single commit by SHA, which keeps the clone small.
    run([git, "fetch", "-q", "--depth", "1", "origin", target.commit], target.dir)
    run([git, "checkout", "-q", "--detach", "FETCH_HEAD"], target.dir)


def install_js(target: Target) -> None:
    npm = tool("npm")
    # --ignore-scripts skips the repo's build/husky hooks; tests import from src directly.
    run([npm, "ci", "--ignore-scripts", "--no-audit", "--no-fund"], target.dir)
    # --no-save keeps the target's package.json and lockfile untouched.
    run([npm, "install", "--no-save", "--ignore-scripts", "--no-audit", "--no-fund",
         *target.stryker_packages], target.dir)


def install_csharp(target: Target) -> None:
    dotnet = tool("dotnet")
    # .NET 10 writes the manifest next to the project; older SDKs use .config/.
    manifests = [target.workdir / "dotnet-tools.json", target.workdir / ".config" / "dotnet-tools.json"]
    if not any(m.exists() for m in manifests):
        run([dotnet, "new", "tool-manifest"], target.workdir)
    cmd = [dotnet, "tool", "install", "dotnet-stryker"]
    if target.stryker_tool_version:
        cmd += ["--version", target.stryker_tool_version]
    run(cmd, target.workdir, check=False)  # non-zero when already installed
    run([dotnet, "restore"], target.workdir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tc2 setup", description=__doc__)
    parser.add_argument("target")
    parser.add_argument("--skip-install", action="store_true", help="only clone/checkout")
    args = parser.parse_args(argv)

    target = get_target(args.target)
    checkout(target)
    if not args.skip_install:
        {"js": install_js, "csharp": install_csharp}[target.language](target)
    print(f"{target.name}: ready in {target.workdir}")
    return 0
