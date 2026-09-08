from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .fingerprint import sha256_json
from .model import MissionPacket


@dataclass(frozen=True)
class ProofObligation:
    obligation_id: str
    statement: str
    method_family: str = "unspecified"


@dataclass(frozen=True)
class Postcondition:
    key: str
    expected: Any = None
    comparator: str = "eq"


@dataclass(frozen=True)
class ProofCarryingChange:
    """Generator-independent envelope for one proposed change.

    OPUS does not assume that the producer is an LLM. A human, script, CI bot,
    local model, hosted model, or orchestrator may all produce the same contract.
    """

    change_id: str
    packet: MissionPacket
    obligations: tuple[ProofObligation, ...]
    postconditions: tuple[Postcondition, ...]

    def fingerprint(self) -> str:
        packet = self.packet
        payload = {
            "change_id": self.change_id,
            "mission": packet.mission,
            "evidence": packet.evidence.__dict__,
            "model": packet.model.__dict__,
            "action": packet.action.__dict__,
            "metadata": packet.metadata,
            "obligations": [
                {
                    "obligation_id": x.obligation_id,
                    "statement": x.statement,
                    "method_family": x.method_family,
                }
                for x in self.obligations
            ],
            "postconditions": [
                {"key": x.key, "expected": x.expected, "comparator": x.comparator}
                for x in self.postconditions
            ],
        }
        return sha256_json(payload)


def default_change(packet: MissionPacket, *, change_id: str = "change") -> ProofCarryingChange:
    """Wrap a legacy MissionPacket without inventing new evidence or authority."""
    obligation = ProofObligation(
        obligation_id="model-proof-obligation",
        statement=packet.model.proof_obligation,
        method_family="declared",
    )
    return ProofCarryingChange(change_id, packet, (obligation,), ())
