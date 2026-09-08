from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .model import Check, MissionPacket, Verdict


class Verifier(Protocol):
    name: str

    def verify(self, packet: MissionPacket) -> Check:
        ...


@dataclass(frozen=True)
class ProofObligationVerifier:
    name: str = "proof_obligation"

    def verify(self, packet: MissionPacket) -> Check:
        obligation = packet.model.proof_obligation.strip().lower()
        if not obligation:
            return Check(self.name, Verdict.REPAIR, "proof obligation is empty")
        allowed = {
            "empirical", "behavioral", "formal", "causal",
            "numerical", "provenance", "operational",
        }
        if obligation not in allowed:
            return Check(
                self.name,
                Verdict.UNKNOWN,
                f"unrecognized proof obligation: {packet.model.proof_obligation}",
            )
        return Check(self.name, Verdict.PASS, f"declared obligation: {obligation}")


@dataclass(frozen=True)
class TransactionCompletenessVerifier:
    name: str = "transaction_completeness"

    def verify(self, packet: MissionPacket) -> Check:
        effectful = packet.action.side_effect.lower() not in {
            "", "none", "read-only", "readonly",
        }
        if not effectful:
            return Check(self.name, Verdict.PASS, "read-only/no-side-effect action")
        missing = []
        if not packet.action.rollback:
            missing.append("rollback")
        if not packet.action.readback:
            missing.append("readback")
        if missing:
            return Check(self.name, Verdict.REPAIR, "missing " + ", ".join(missing))
        return Check(self.name, Verdict.PASS, "rollback and readback declared")


def run_verifiers(packet: MissionPacket, verifiers: list[Verifier]) -> tuple[Check, ...]:
    return tuple(v.verify(packet) for v in verifiers)
