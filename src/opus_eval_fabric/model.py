from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EvidenceClass(str, Enum):
    FACT = "FACT"
    MEASUREMENT = "MEASUREMENT"
    INFERENCE = "INFERENCE"
    MODEL = "MODEL"
    HYPOTHESIS = "HYPOTHESIS"
    SIMULATION = "SIMULATION"
    UNKNOWN = "UNKNOWN"


class AuthorityState(str, Enum):
    BLOCKED = "BLOCKED"
    REVIEW = "REVIEW"
    AUTHORIZED = "AUTHORIZED"


class Verdict(str, Enum):
    PASS = "PASS"
    REPAIR = "REPAIR"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Claim:
    text: str
    evidence_class: EvidenceClass
    source_refs: tuple[str, ...] = ()
    uncertainty: str | None = None


@dataclass(frozen=True)
class EvalPacket:
    packet_id: str
    goal: str
    claims: tuple[Claim, ...] = ()
    authority: AuthorityState = AuthorityState.REVIEW
    action_requested: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvalResult:
    packet_id: str
    verdict: Verdict
    reasons: tuple[str, ...]
    checks: dict[str, bool]
