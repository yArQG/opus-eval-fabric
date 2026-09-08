from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class Verdict(str, Enum):
    PASS = "PASS"
    REPAIR = "REPAIR"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"

@dataclass(frozen=True)
class EvidencePacket:
    source: str
    provenance: str
    observed_at: str | None = None
    uncertainty: str = "UNKNOWN"
    content_hash: str | None = None

@dataclass(frozen=True)
class ModelPacket:
    claim: str
    assumptions: tuple[str, ...] = ()
    proof_obligation: str = "empirical"
    model_class: str = "working_model"

@dataclass(frozen=True)
class ActionPacket:
    action: str
    authority: str = "none"
    side_effect: str = "none"
    rollback: str | None = None
    readback: str | None = None

@dataclass(frozen=True)
class MissionPacket:
    mission: str
    evidence: EvidencePacket
    model: ModelPacket
    action: ActionPacket
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Check:
    name: str
    verdict: Verdict
    detail: str

@dataclass(frozen=True)
class EvalResult:
    verdict: Verdict
    checks: tuple[Check, ...]
