"""Local demo server: lets a browser trigger a real `tc2 run` and watch it execute.

Proves the pipeline actually works, not just a report of past numbers. Binds to
127.0.0.1 only. Only standard library (matches the rest of tc2/).

Usage: python3 demo/server.py [port]   (default port 8000)
Then open http://127.0.0.1:8000
"""

from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
DEMO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from tc2.common import load_targets  # noqa: E402
from tc2.summarize import compute_counts, load_report  # noqa: E402

VALID_TARGETS = set(load_targets().keys())

JOBS: dict[str, dict] = {}
JOBS_LOCK = threading.Lock()


def start_job(target: str, with_tests: bool) -> str:
    job_id = uuid.uuid4().hex[:8]
    label = f"demo-{job_id}"
    cmd = [sys.executable, "-m", "tc2", "run", target, "--label", label]
    if with_tests:
        cmd += ["--with-tests", "--reviewed", str(ROOT / "data" / "reviewed" / f"{target}.csv")]
    popen = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    with JOBS_LOCK:
        JOBS[job_id] = {
            "target": target, "label": label, "popen": popen, "cmd": " ".join(cmd),
            "out_dir": None, "cli_lines": [], "started": time.time(), "stats": None, "error": None,
        }
    threading.Thread(target=_pump_cli_output, args=(job_id,), daemon=True).start()
    threading.Thread(target=_watch_job, args=(job_id, target, label), daemon=True).start()
    return job_id


def _pump_cli_output(job_id: str) -> None:
    """Collect the tc2 CLI's own stdout (the run.py print() calls), not Stryker's internal log."""
    job = JOBS[job_id]
    for line in job["popen"].stdout:
        with JOBS_LOCK:
            job["cli_lines"].append(line.rstrip("\n"))


def _watch_job(job_id: str, target: str, label: str) -> None:
    job = JOBS[job_id]
    deadline = time.time() + 10
    out_dir = None
    while time.time() < deadline and out_dir is None:
        for candidate in sorted((ROOT / "results").glob(f"*-{target}-{label}")):
            out_dir = candidate
            break
        if out_dir is None:
            time.sleep(0.3)
    with JOBS_LOCK:
        job["out_dir"] = out_dir
    job["popen"].wait()
    with JOBS_LOCK:
        if out_dir and (out_dir / "mutation.json").exists():
            report = load_report(out_dir / "mutation.json")
            job["stats"] = compute_counts(report)
        elif job["popen"].returncode != 0:
            job["error"] = f"tc2 run exited with {job['popen'].returncode}"


def tail_log(out_dir: Path | None, offset: int) -> tuple[str, int]:
    if not out_dir:
        return "", offset
    log_path = out_dir / "stryker.log"
    if not log_path.exists():
        return "", offset
    data = log_path.read_bytes()
    return data[offset:].decode("utf-8", errors="replace"), len(data)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # quieter console
        pass

    def _json(self, obj: dict, status: int = 200) -> None:
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            qs = parse_qs(parsed.query)
            job_id = (qs.get("job_id") or [""])[0]
            offset = int((qs.get("offset") or ["0"])[0])
            job = JOBS.get(job_id)
            if not job:
                self._json({"error": "unknown job_id"}, 404)
                return
            running = job["popen"].poll() is None
            log_chunk, new_offset = tail_log(job["out_dir"], offset)
            self._json({
                "running": running,
                "cli_lines": job["cli_lines"],
                "log_chunk": log_chunk,
                "offset": new_offset,
                "out_dir": job["out_dir"].name if job["out_dir"] else None,
                "stats": job["stats"],
                "error": job["error"],
            })
            return
        if parsed.path == "/" or parsed.path == "":
            self._serve_file(DEMO_DIR / "index.html", "text/html")
            return
        safe_name = Path(parsed.path.lstrip("/")).name
        candidate = DEMO_DIR / safe_name
        if candidate.exists() and candidate.parent == DEMO_DIR:
            ctype = "application/json" if candidate.suffix == ".json" else "text/plain"
            self._serve_file(candidate, ctype)
            return
        self.send_error(404)

    def _serve_file(self, path: Path, ctype: str) -> None:
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if urlparse(self.path).path != "/api/run":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._json({"error": "invalid JSON body"}, 400)
            return
        target = payload.get("target", "")
        with_tests = bool(payload.get("with_tests", False))
        if target not in VALID_TARGETS:
            self._json({"error": f"unknown target '{target}'. Known: {sorted(VALID_TARGETS)}"}, 400)
            return
        job_id = start_job(target, with_tests)
        self._json({"job_id": job_id, "cmd": JOBS[job_id]["cmd"]})


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"tc2 demo server: http://127.0.0.1:{port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
