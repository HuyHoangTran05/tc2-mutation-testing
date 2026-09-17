"""Shared helpers: repository paths, target loading and subprocess wrappers."""

from __future__ import annotations

import os
import shutil
import subprocess
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
REVIEWED_DIR = ROOT / "data" / "reviewed"


@dataclass
class Target:
    name: str
    language: str
    repo: str
    commit: str
    dir: Path
    workdir: Path
    test_workdir: Path
    stryker_config: Path
    business_rule: str = ""
    stryker_packages: list[str] = field(default_factory=list)
    stryker_tool_version: str = ""


def load_targets(path: Path | None = None) -> dict[str, Target]:
    data = tomllib.loads((path or ROOT / "targets.toml").read_text(encoding="utf-8"))
    targets = {}
    for name, raw in data["targets"].items():
        target_dir = ROOT / raw["dir"]
        targets[name] = Target(
            name=name,
            language=raw["language"],
            repo=raw["repo"],
            commit=raw["commit"],
            dir=target_dir,
            workdir=target_dir / raw.get("workdir", "."),
            test_workdir=target_dir / raw.get("test_workdir", raw.get("workdir", ".")),
            stryker_config=ROOT / raw["stryker_config"],
            business_rule=raw.get("business_rule", ""),
            stryker_packages=raw.get("stryker_packages", []),
            stryker_tool_version=raw.get("stryker_tool_version", ""),
        )
    return targets


def get_target(name: str) -> Target:
    targets = load_targets()
    if name not in targets:
        raise SystemExit(f"Unknown target '{name}'. Known: {', '.join(sorted(targets))}")
    return targets[name]


def dotnet_exe() -> str:
    """Prefer dotnet on PATH, then the per-user install used by dotnet-install.ps1."""
    found = shutil.which("dotnet")
    if found:
        return found
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "dotnet" / "dotnet.exe"
    if local.exists():
        return str(local)
    raise SystemExit("dotnet not found. Install the .NET SDK (see README).")


def tool(name: str) -> str:
    """Resolve npm/npx/git to an executable path (npx is npx.cmd on Windows)."""
    if name == "dotnet":
        return dotnet_exe()
    found = shutil.which(name)
    if not found:
        raise SystemExit(f"{name} not found on PATH.")
    return found


def dotnet_env() -> dict[str, str]:
    env = dict(os.environ)
    exe = Path(dotnet_exe())
    env.setdefault("DOTNET_ROOT", str(exe.parent))
    env["PATH"] = f"{exe.parent}{os.pathsep}{env.get('PATH', '')}"
    env["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1"
    env["DOTNET_NOLOGO"] = "1"
    return env


def run(cmd: list[str], cwd: Path, check: bool = True, **kwargs) -> subprocess.CompletedProcess:
    print(f"$ {' '.join(cmd)}  (in {cwd})", flush=True)
    return subprocess.run(cmd, cwd=cwd, check=check, env=dotnet_env_if_needed(cmd), **kwargs)


def capture(cmd: list[str], cwd: Path) -> str:
    """Return stripped stdout, or an 'error: ...' marker so version capture never aborts a run."""
    try:
        out = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
            errors="replace", env=dotnet_env_if_needed(cmd), timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"error: {exc}"
    if out.returncode != 0:
        return f"error: exit {out.returncode}: {out.stderr.strip()[:200]}"
    return out.stdout.strip()


def dotnet_env_if_needed(cmd: list[str]) -> dict[str, str] | None:
    return dotnet_env() if cmd and Path(cmd[0]).stem.lower() == "dotnet" else None
