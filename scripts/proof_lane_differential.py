from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: list[str], *, source_mode: bool) -> tuple[int, str, float]:
    env = os.environ.copy()
    if source_mode:
        env["PYTHONPATH"] = str(ROOT / "src")
    started = time.perf_counter()
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    elapsed = time.perf_counter() - started
    return proc.returncode, proc.stdout, elapsed


def _json_command(args: list[str], *, source_mode: bool) -> dict:
    prefix = [sys.executable, "-m", "opus_eval_fabric.cli"] if source_mode else ["opus-eval"]
    rc, out, elapsed = _run(prefix + args, source_mode=source_mode)
    if rc not in (0, 1):
        raise SystemExit(f"command failed rc={rc}: {' '.join(prefix + args)}\n{out}")
    try:
        payload = json.loads(out)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"non-JSON output from {' '.join(prefix + args)}: {exc}\n{out}") from exc
    return {"returncode": rc, "elapsed_s": elapsed, "payload": payload}


def _normalize(name: str, item: dict) -> dict:
    payload = json.loads(json.dumps(item["payload"]))
    if name == "doctor":
        payload.pop("python", None)
        payload.pop("platform", None)
    if name == "adapter-python":
        status = payload.get("status", {})
        status.pop("executable", None)
    return {"returncode": item["returncode"], "payload": payload}


def collect(lane: str, output: Path) -> None:
    source_mode = lane == "source"
    commands = {
        "doctor": ["doctor"],
        "validate": ["validate", "examples/mission.json"],
        "run": ["run", "examples/mission.json"],
        "plan": ["plan", "examples/mission.json"],
        "command-center": ["command-center", "examples/mission.json"],
        "adapter-python": ["adapter-python", "--source", "src/opus_eval_fabric/evaluator.py"],
        "code24": ["code24"],
    }
    results = {name: _json_command(args, source_mode=source_mode) for name, args in commands.items()}
    total = sum(x["elapsed_s"] for x in results.values())
    report = {
        "schema_version": "0.1",
        "lane": lane,
        "python": sys.version.split()[0],
        "command_elapsed_s": {k: v["elapsed_s"] for k, v in results.items()},
        "command_total_s": total,
        "normalized": {k: _normalize(k, v) for k, v in results.items()},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


def compare(source_path: Path, installed_path: Path, output: Path) -> int:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    installed = json.loads(installed_path.read_text(encoding="utf-8"))
    keys = sorted(set(source["normalized"]) | set(installed["normalized"]))
    comparisons = {key: source["normalized"].get(key) == installed["normalized"].get(key) for key in keys}
    equivalent = all(comparisons.values())
    report = {
        "schema_version": "0.1",
        "equivalent_on_declared_surface": equivalent,
        "comparisons": comparisons,
        "source_command_total_s": source["command_total_s"],
        "installed_command_total_s": installed["command_total_s"],
        "scope_note": (
            "Equivalence is limited to the explicitly compared CLI JSON surface on one runner. "
            "It does not prove wheel/build reproducibility, packaging completeness, dependency completeness, or release equivalence."
        ),
    }
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if equivalent else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("collect")
    p.add_argument("--lane", choices=["source", "installed"], required=True)
    p.add_argument("--output", type=Path, required=True)

    p = sub.add_parser("compare")
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--installed", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    if args.cmd == "collect":
        collect(args.lane, args.output)
        return 0
    return compare(args.source, args.installed, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
