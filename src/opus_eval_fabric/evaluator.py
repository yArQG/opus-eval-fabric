from __future__ import annotations
from .guards import action_guard, evidence_guard, model_guard, retorsion_guard
from .model import Check, EvalResult, MissionPacket, Verdict

_PRIORITY = {Verdict.PASS:0, Verdict.UNKNOWN:1, Verdict.REPAIR:2, Verdict.BLOCK:3}

def fold_verdict(checks: list[Check]) -> Verdict:
    return max((c.verdict for c in checks), key=_PRIORITY.__getitem__, default=Verdict.UNKNOWN)

def evaluate(packet: MissionPacket) -> EvalResult:
    checks = [
        evidence_guard(packet.evidence),
        model_guard(packet.model),
        action_guard(packet.action),
        retorsion_guard(list(packet.metadata.get("retorsion_edges", []))),
    ]
    return EvalResult(fold_verdict(checks), tuple(checks))
