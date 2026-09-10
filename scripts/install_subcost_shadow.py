from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

BUILD_REQUIREMENTS = ["setuptools>=68", "wheel"]


def _run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> dict[str, object]:
    started = time.perf_counter_ns()
    proc = subprocess.run(cmd, cwd=cwd, env=env, text=True, capture_output=True, check=False)
    elapsed = time.perf_counter_ns() - started
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "duration_ns": elapsed,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def _venv_python(root: Path) -> Path:
    return root / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _venv_entrypoint(root: Path) -> Path:
    return root / ("Scripts/opus-eval.exe" if os.name == "nt" else "bin/opus-eval")


def _make_venv(repo: Path, parent: Path, name: str) -> tuple[Path, dict[str, object]]:
    root = parent / name
    result = _run([sys.executable, "-m", "venv", str(root)], repo)
    return root, result


def _verify(repo: Path, venv_root: Path) -> dict[str, object]:
    py = _venv_python(venv_root)
    exe = _venv_entrypoint(venv_root)
    checks = {
        "entrypoint_exists": exe.exists(),
        "validate": _run([str(exe), "validate", "examples/mission.json"], repo) if exe.exists() else None,
        "code24": _run([str(exe), "code24"], repo) if exe.exists() else None,
        "metadata": _run(
            [str(py), "-c", "import importlib.metadata as m; print(m.version('opus-eval-fabric'))"],
            repo,
        ),
        "resource": _run(
            [str(py), "-c", "import importlib.resources as r; print(r.files('opus_eval_fabric').joinpath('code24.json').is_file())"],
            repo,
        ),
    }
    ok = bool(checks["entrypoint_exists"])
    for key in ("validate", "code24", "metadata", "resource"):
        item = checks[key]
        ok = ok and item is not None and item["returncode"] == 0
    checks["pass"] = ok
    return checks


def run_lane(repo: Path, parent: Path, mode: str) -> dict[str, object]:
    venv_root, venv_create = _make_venv(repo, parent, mode)
    py = _venv_python(venv_root)
    base = [str(py), "-m", "pip", "install", "--disable-pip-version-check", "--no-cache-dir"]

    if mode == "default":
        prep = None
        install = _run(base + ["-e", "."], repo)
    elif mode == "no_isolation":
        prep = _run(base + BUILD_REQUIREMENTS, repo)
        install = _run(base + ["--no-build-isolation", "--no-deps", "-e", "."], repo)
    else:
        raise ValueError(mode)

    verify = _verify(repo, venv_root) if install["returncode"] == 0 else {"pass": False}
    total = venv_create["duration_ns"] + install["duration_ns"] + (prep["duration_ns"] if prep else 0)
    return {
        "mode": mode,
        "venv_create": venv_create,
        "build_requirements_prep": prep,
        "editable_install": install,
        "verify": verify,
        "measured_setup_total_ns": total,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--order", choices=["default-first", "no-isolation-first"], required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    repo = Path.cwd()
    sequence = ["default", "no_isolation"] if args.order == "default-first" else ["no_isolation", "default"]
    with tempfile.TemporaryDirectory(prefix="opus-install-shadow-") as td:
        parent = Path(td)
        lanes = [run_lane(repo, parent, mode) for mode in sequence]

    by_mode = {lane["mode"]: lane for lane in lanes}
    default = by_mode["default"]
    noiso = by_mode["no_isolation"]
    both_valid = bool(default["verify"]["pass"] and noiso["verify"]["pass"])
    report = {
        "schema_version": "0.1",
        "python": sys.version.split()[0],
        "order": args.order,
        "build_requirements": BUILD_REQUIREMENTS,
        "cache_policy": "pip --no-cache-dir in isolated venvs; network/runner variance remains possible",
        "lanes": lanes,
        "summary": {
            "both_packaging_contracts_pass": both_valid,
            "default_install_ns": default["editable_install"]["duration_ns"],
            "no_isolation_prep_ns": noiso["build_requirements_prep"]["duration_ns"],
            "no_isolation_install_ns": noiso["editable_install"]["duration_ns"],
            "default_setup_total_ns": default["measured_setup_total_ns"],
            "no_isolation_setup_total_ns": noiso["measured_setup_total_ns"],
            "install_only_delta_ns": default["editable_install"]["duration_ns"] - noiso["editable_install"]["duration_ns"],
            "total_setup_delta_ns": default["measured_setup_total_ns"] - noiso["measured_setup_total_ns"],
        },
        "non_claims": [
            "one paired run does not establish causal attribution",
            "no-build-isolation changes the trust/environment boundary and is not automatically promotable",
            "timings include runner and network effects despite no-cache isolation",
            "this experiment does not justify removing packaging proof",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    return 0 if both_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
