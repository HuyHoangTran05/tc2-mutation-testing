"""Run Stryker on a target and store the report with the exact tool versions used.

Output goes to results/<timestamp>-<target>/: mutation.json, mutation.html, run.json, config copy,
stryker.log, summary.md and survivors.csv.

Usage: python -m tc2 run <target> [--label NAME] [--reviewed data/reviewed/<target>.csv]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

from .common import RESULTS_DIR, ROOT, Target, capture, dotnet_env_if_needed, get_target, tool
from .summarize import summarize_dir


def stryker_command(target: Target) -> list[str]:
    if target.language == "js":
        return [tool("npx"), "stryker", "run", str(target.stryker_config)]
    return [tool("dotnet"), "stryker", "--config-file", str(target.stryker_config)]


def js_package_version(target: Target, package: str) -> str:
    path = target.dir / "node_modules" / package / "package.json"
    if not path.exists():
        return "not installed"
    return json.loads(path.read_text(encoding="utf-8"))["version"]


def js_versions(target: Target) -> dict[str, str]:
    return {
        "node": capture([tool("node"), "--version"], target.dir),
        "npm": capture([tool("npm"), "--version"], target.dir),
        "@stryker-mutator/core": js_package_version(target, "@stryker-mutator/core"),
        "@stryker-mutator/vitest-runner": js_package_version(target, "@stryker-mutator/vitest-runner"),
        "vitest": js_package_version(target, "vitest"),
    }


def csharp_versions(target: Target) -> dict[str, str]:
    dotnet = tool("dotnet")
    versions = {"dotnet_sdk": capture([dotnet, "--version"], target.workdir)}
    tools = capture([dotnet, "tool", "list", "--local"], target.workdir)
    versions.update({f"tool:{k}": v for k, v in parse_tool_list(tools).items()})
    # Test framework and runner versions come from the test project's package references.
    for csproj in target.test_workdir.glob("*.csproj"):
        text = csproj.read_text(encoding="utf-8")
        for name, version in re.findall(r'PackageReference\s+Include="([^"]+)"\s+Version="([^"]+)"', text):
            versions[f"package:{name}"] = version
    return versions


def parse_tool_list(output: str) -> dict[str, str]:
    """Package id -> version from `dotnet tool list` (the manifest column holds a local path)."""
    tools = {}
    for line in output.splitlines()[2:]:
        parts = line.split()
        if len(parts) >= 2:
            tools[parts[0]] = parts[1]
    return tools


def js_report_paths(target: Target) -> tuple[Path, Path]:
    config = json.loads(target.stryker_config.read_text(encoding="utf-8"))
    return (target.dir / config["jsonReporter"]["fileName"],
            target.dir / config["htmlReporter"]["fileName"])


def csharp_report_paths(target: Target, started: float) -> tuple[Path, Path]:
    """Stryker.NET writes StrykerOutput/<timestamp>/reports/; take the newest one from this run."""
    reports = [p for p in (target.workdir / "StrykerOutput").glob("*/reports")
               if p.stat().st_mtime >= started - 1]
    if not reports:
        raise SystemExit("No Stryker.NET report found for this run; see stryker.log")
    newest = max(reports, key=lambda p: p.stat().st_mtime)
    return newest / "mutation-report.json", newest / "mutation-report.html"


def strip_local_paths(value, bases: tuple[Path, ...]):
    """Recursively rewrite absolute paths under any of `bases` as relative POSIX paths."""
    if isinstance(value, dict):
        return {k: strip_local_paths(v, bases) for k, v in value.items()}
    if isinstance(value, list):
        return [strip_local_paths(v, bases) for v in value]
    if isinstance(value, str) and Path(value).is_absolute():
        for base in bases:
            if Path(value).is_relative_to(base):
                return Path(value).relative_to(base).as_posix()
    return value


def relativize_report(src: Path, dest: Path, base: Path) -> None:
    """Copy a report, rewriting absolute file keys (Stryker.NET) relative to the target repo."""
    report = json.loads(src.read_text(encoding="utf-8"))
    for section in ("files", "testFiles"):
        files = report.get(section) or {}
        renamed = {}
        for name, info in files.items():
            path = Path(name)
            if path.is_absolute() and path.is_relative_to(base):
                name = path.relative_to(base).as_posix()
            renamed[name] = info
        if files:
            report[section] = renamed
    report.pop("projectRoot", None)
    if "config" in report:
        report["config"] = strip_local_paths(report["config"], (base, ROOT))
    dest.write_text(json.dumps(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tc2 run", description=__doc__)
    parser.add_argument("target")
    parser.add_argument("--label", default="", help="suffix for the results folder, e.g. after-tests")
    parser.add_argument("--reviewed", type=Path, help="reviewed survivors CSV to carry verdicts over")
    args = parser.parse_args(argv)

    target = get_target(args.target)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    name = f"{stamp}-{target.name}" + (f"-{args.label}" if args.label else "")
    out_dir = RESULTS_DIR / name
    out_dir.mkdir(parents=True)

    versions = js_versions(target) if target.language == "js" else csharp_versions(target)
    cmd = stryker_command(target)
    print(f"$ {' '.join(cmd)}  (in {target.workdir})", flush=True)
    started = time.time()
    with (out_dir / "stryker.log").open("w", encoding="utf-8") as log:
        proc = subprocess.run(cmd, cwd=target.workdir, stdout=log, stderr=subprocess.STDOUT,
                              env=dotnet_env_if_needed(cmd))
    duration = round(time.time() - started, 1)

    run_info = {
        "target": target.name,
        "language": target.language,
        "repo": target.repo,
        "commit": capture([tool("git"), "rev-parse", "HEAD"], target.dir),
        "pinned_commit": target.commit,
        "business_rule": target.business_rule,
        "started": datetime.fromtimestamp(started).isoformat(timespec="seconds"),
        "duration_s": duration,
        "exit_code": proc.returncode,
        "command": [Path(cmd[0]).name, *cmd[1:-1], target.stryker_config.name],
        "versions": versions,
    }
    (out_dir / "run.json").write_text(json.dumps(run_info, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(target.stryker_config, out_dir / target.stryker_config.name)

    if proc.returncode != 0:
        print(f"Stryker exited with {proc.returncode}; see {out_dir / 'stryker.log'}")
        return proc.returncode
    if run_info["commit"] != target.commit:
        print(f"WARNING: target is at {run_info['commit'][:10]}, pinned {target.commit[:10]}")

    if target.language == "js":
        json_path, html_path = js_report_paths(target)
    else:
        json_path, html_path = csharp_report_paths(target, started)
    relativize_report(json_path, out_dir / "mutation.json", target.dir)
    if html_path.exists():
        shutil.copy2(html_path, out_dir / "mutation.html")

    stats = summarize_dir(out_dir, args.reviewed)
    print(f"{target.name}: {stats['counts']} in {duration}s -> {out_dir}")
    return 0
