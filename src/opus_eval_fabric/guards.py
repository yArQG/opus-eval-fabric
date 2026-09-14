from __future__ import annotations

from .model import AuthorityState, EvalPacket, EvidenceClass


def evidence_guard(packet: EvalPacket) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    for i, claim in enumerate(packet.claims):
        if claim.evidence_class in {EvidenceClass.FACT, EvidenceClass.MEASUREMENT} and not claim.source_refs:
            reasons.append(f"claim[{i}] {claim.evidence_class.value} requires source_refs")
        if claim.evidence_class is EvidenceClass.UNKNOWN and not claim.uncertainty:
            reasons.append(f"claim[{i}] UNKNOWN requires uncertainty note")
    return (not reasons, tuple(reasons))


def authority_guard(packet: EvalPacket) -> tuple[bool, tuple[str, ...]]:
    if packet.action_requested and packet.authority is not AuthorityState.AUTHORIZED:
        return False, ("effectful action requested without AUTHORIZED authority",)
    return True, ()
