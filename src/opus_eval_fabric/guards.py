from __future__ import annotations
from .model import ActionPacket, Check, EvidencePacket, ModelPacket, Verdict

FORBIDDEN_RETORSIONS = {
    "MODEL->FACT",
    "TOOL->AUTHORITY",
    "SALIENCE->TRUTH",
    "DRIFT->CAUSE",
    "METAPHOR->SOLVER",
}

def evidence_guard(packet: EvidencePacket) -> Check:
    if not packet.source.strip() or not packet.provenance.strip():
        return Check("source_before_claim", Verdict.BLOCK, "source/provenance missing")
    if packet.uncertainty.upper() == "UNKNOWN":
        return Check("epistemic_status", Verdict.UNKNOWN, "uncertainty explicitly UNKNOWN")
    return Check("source_before_claim", Verdict.PASS, "source and provenance present")

def model_guard(packet: ModelPacket) -> Check:
    if not packet.claim.strip():
        return Check("model_claim", Verdict.BLOCK, "empty model/claim")
    if packet.model_class.lower() in {"fact", "truth"}:
        return Check("model_class", Verdict.REPAIR, "working model cannot self-promote to FACT/TRUTH")
    return Check("model_claim", Verdict.PASS, "claim remains a scoped model")

def action_guard(packet: ActionPacket) -> Check:
    effectful = packet.side_effect.lower() not in {"", "none", "read-only", "readonly"}
    if effectful and packet.authority.lower() in {"", "none", "unknown"}:
        return Check("authority", Verdict.BLOCK, "side effect requested without authority")
    if effectful and not packet.rollback:
        return Check("rollback", Verdict.REPAIR, "effectful action lacks rollback")
    if effectful and not packet.readback:
        return Check("readback", Verdict.REPAIR, "effectful action lacks readback")
    return Check("action_admission", Verdict.PASS, "action is bounded for current declaration")

def retorsion_guard(edges: list[str]) -> Check:
    bad = sorted(set(edges) & FORBIDDEN_RETORSIONS)
    if bad:
        return Check("retorsion_semantic_direction", Verdict.BLOCK, "forbidden: " + ", ".join(bad))
    return Check("retorsion_semantic_direction", Verdict.PASS, "no semantic-authority inversion")
