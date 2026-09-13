from __future__ import annotations

from .guards import authority_guard, evidence_guard
from .model import EvalPacket, EvalResult, Verdict


def evaluate(packet: EvalPacket) -> EvalResult:
    evidence_ok, evidence_reasons = evidence_guard(packet)
    authority_ok, authority_reasons = authority_guard(packet)
    reasons = evidence_reasons + authority_reasons
    checks = {"evidence": evidence_ok, "authority": authority_ok}

    if not authority_ok:
        verdict = Verdict.BLOCK
    elif not evidence_ok:
        verdict = Verdict.REPAIR
    else:
        verdict = Verdict.PASS

    return EvalResult(packet.packet_id, verdict, reasons, checks)
