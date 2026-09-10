from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

COMMANDS = {
    "validate": ["validate", "examples/mission.json"],
    "run": ["run", "examples/mission.json"],
    "plan": ["plan", "examples/mission.json"],
    "command_center": ["command-center", "examples/mission.json"],
    "code24": ["code24"],
}


def _runner(mode: str) -> tuple[list[str], dict[str, str]]:
    env = os.environ.copy()
    if mode == "source":
        env["PYTHONPATH"] = "src"
        return [sys.executable, "-m", "opus_eval_fabric.cli"], env
    if mode == "installed":
        exe = shutil.which("opus-eval")
        if not exe:
            raise SystemExit("installed lane requires opus-eval on PATH")
        return [exe], env
    raise SystemExit(f"unsupported mode: {mode}")


def capture(mode: str, out_path: Path) -> int:
    prefix, env = _runner(mode)
    results: dict[str, object] = {
        "schema_version": "0.1",
        "mode": mode,
        "python": sys.version.split()[0],
        "commands": {},
    }
    failed = False
    for name, args in COMMANDS.items():
        started = time.perf_counter_ns()
        proc = subprocess.run(
            prefix + args,
            cwd=Path.cwd(),
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        elapsed = time.perf_counter_ns() - started
        results["commands"][name] = {
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "duration_ns": elapsed,
        }
        failed |= proc.returncode != 0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 1 if failed else 0


def compare(source_path: Path, installed_path: Path, out_path: Path) -> int:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    installed = json.loads(installed_path.read_text(encoding="utf-8"))
    comparisons = {}
    equivalent = True
    for name in COMMANDS:
        s = source["commands"][name]
        i = installed["commands"][name]
        same = (
            s["returncode"] == i["returncode"]
            and s["stdout"] == i["stdout"]
            and s["stderr"] == i["stderr"]
        )
        comparisons[name] = {
            "equivalent": same,
            "source_returncode": s["returncode"],
            "installed_returncode": i["returncode"],
            "source_duration_ns": s["duration_ns"],
            "installed_duration_ns": i["duration_ns"],
        }
        equivalent &= same
    report = {
        "schema_version": "0.1",
        "semantic_equivalence": equivalent,
        "scope": "CLI observable stdout/stderr/exit status for deterministic commands only",
        "non_claims": [
            "does not prove wheel reproducibility",
            "does not replace packaging validation",
            "does not prove complete behavioral equivalence",
        ],
        "comparisons": comparisons,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if equivalent else 1


def packaging_check(out_path: Path) -> int:
    import importlib.metadata
    import importlib.resources

    exe = shutil.which("opus-eval")
    resource = importlib.resources.files("opus_eval_fabric").joinpath("code24.json")
    report = {
        "schema_version": "0.1",
        "distribution_version": importlib.metadata.version("opus-eval-fabric"),
        "console_entrypoint_present": bool(exe),
        "console_entrypoint": exe,
        "code24_resource_present": resource.is_file(),
    }
    ok = report["console_entrypoint_present"] and report["code24_resource_present"]
    report["packaging_contract_pass"] = bool(ok)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("capture")
    p.add_argument("--mode", choices=["source", "installed"], required=True)
    p.add_argument("--out", type=Path, required=True)

    p = sub.add_parser("compare")
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--installed", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)

    p = sub.add_parser("packaging-check")
    p.add_argument("--out", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "capture":
        return capture(args.mode, args.out)
    if args.command == "compare":
        return compare(args.source, args.installed, args.out)
    if args.command == "packaging-check":
        return packaging_check(args.out)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
