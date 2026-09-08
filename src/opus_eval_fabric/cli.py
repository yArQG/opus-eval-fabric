from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

from .adapters.python import PythonAdapter
from .benchmark import run_suite
from .contextual import contextual_variants
from .evaluator import evaluate
from .fingerprint import sha256_file
from .io import load_json, mission_from_dict, validate_shape
from .reporting import write_json_report, write_junit_report


def cmd_doctor(_):
    print(json.dumps({
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "core_dependencies": "stdlib-only",
        "status": "OK",
    }, indent=2))
    return 0


def cmd_validate(args):
    data = load_json(args.path)
    errors = validate_shape(data)
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    return 0 if not errors else 2


def cmd_run(args):
    data = load_json(args.path)
    errors = validate_shape(data)
    if errors:
        print(json.dumps({"verdict": "BLOCK", "errors": errors}, indent=2))
        return 2
    result = evaluate(mission_from_dict(data))
    print(json.dumps({
        "verdict": result.verdict.value,
        "checks": [
            {"name": c.name, "verdict": c.verdict.value, "detail": c.detail}
            for c in result.checks
        ],
    }, indent=2))
    return 0 if result.verdict.value == "PASS" else 1


def cmd_code24(_):
    p = Path(__file__).with_name("code24.json")
    print(p.read_text(encoding="utf-8"))
    return 0


def cmd_perturb(args):
    print(json.dumps(contextual_variants(args.text), indent=2, ensure_ascii=False))
    return 0


def cmd_fingerprint(args):
    print(json.dumps({"path": args.path, "sha256": sha256_file(args.path)}, indent=2))
    return 0


def cmd_adapter_python(args):
    adapter = PythonAdapter()
    out = {"status": adapter.detect().__dict__}
    if args.source:
        source = Path(args.source).read_text(encoding="utf-8")
        ok, detail = adapter.check_syntax(source)
        out["syntax"] = {"ok": ok, "detail": detail}
    print(json.dumps(out, indent=2))
    return 0 if out.get("syntax", {"ok": True})["ok"] else 1


def cmd_benchmark(args):
    report = run_suite(args.path)
    if args.json_out:
        write_json_report(report, args.json_out)
    if args.junit_out:
        write_junit_report(report, args.junit_out)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["summary"]["failed"] == 0 else 1


def build_parser():
    p = argparse.ArgumentParser(prog="opus-eval")
    s = p.add_subparsers(required=True)

    x = s.add_parser("doctor"); x.set_defaults(func=cmd_doctor)
    x = s.add_parser("validate"); x.add_argument("path"); x.set_defaults(func=cmd_validate)
    x = s.add_parser("run"); x.add_argument("path"); x.set_defaults(func=cmd_run)
    x = s.add_parser("code24"); x.set_defaults(func=cmd_code24)
    x = s.add_parser("perturb"); x.add_argument("text"); x.set_defaults(func=cmd_perturb)
    x = s.add_parser("fingerprint"); x.add_argument("path"); x.set_defaults(func=cmd_fingerprint)

    x = s.add_parser("adapter-python")
    x.add_argument("--source")
    x.set_defaults(func=cmd_adapter_python)

    x = s.add_parser("benchmark")
    x.add_argument("path")
    x.add_argument("--json-out")
    x.add_argument("--junit-out")
    x.set_defaults(func=cmd_benchmark)

    return p


def main():
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
