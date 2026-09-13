from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .evaluator import evaluate
from .model import AuthorityState, Claim, EvalPacket, EvidenceClass
from .snapshot import canonical_hash
from .verifiers import DEFAULT_CONTRACTS, compile_required_verifiers


def _cmd_doctor(_: argparse.Namespace) -> int:
    print(json.dumps({"status": "PASS", "package": "opus-eval-fabric", "mode": "local"}, sort_keys=True))
    return 0


def _cmd_select(ns: argparse.Namespace) -> int:
    result = compile_required_verifiers(ns.paths, DEFAULT_CONTRACTS)
    print(json.dumps(asdict(result), sort_keys=True))
    return 2 if result.fail_closed else 0


def _cmd_eval(ns: argparse.Namespace) -> int:
    evidence_class = EvidenceClass(ns.evidence_class)
    claim = Claim(ns.claim, evidence_class, tuple(ns.source), ns.uncertainty)
    packet = EvalPacket(ns.packet_id, ns.goal, (claim,), AuthorityState(ns.authority), ns.action)
    result = evaluate(packet)
    payload = asdict(result)
    payload["verdict"] = result.verdict.value
    payload["packet_hash"] = canonical_hash(packet)
    print(json.dumps(payload, sort_keys=True))
    return 0 if result.verdict.value == "PASS" else 2


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="opus-eval")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("doctor")
    d.set_defaults(func=_cmd_doctor)

    s = sub.add_parser("select-verifiers")
    s.add_argument("paths", nargs="+")
    s.set_defaults(func=_cmd_select)

    e = sub.add_parser("eval")
    e.add_argument("--packet-id", default="packet-1")
    e.add_argument("--goal", required=True)
    e.add_argument("--claim", required=True)
    e.add_argument("--evidence-class", choices=[x.value for x in EvidenceClass], default="UNKNOWN")
    e.add_argument("--source", action="append", default=[])
    e.add_argument("--uncertainty")
    e.add_argument("--authority", choices=[x.value for x in AuthorityState], default="REVIEW")
    e.add_argument("--action", action="store_true")
    e.set_defaults(func=_cmd_eval)

    ns = p.parse_args(argv)
    return ns.func(ns)


if __name__ == "__main__":
    raise SystemExit(main())
