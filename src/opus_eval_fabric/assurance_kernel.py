from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .evaluator import evaluate
from .fingerprint import sha256_json
from .model import Check, MissionPacket, Verdict


class ProjectionStatus(str, Enum):
    IDENTITY = "IDENTITY"
    REPAIR_CANDIDATE = "REPAIR_CANDIDATE"
    UNRESOLVED = "UNRESOLVED"
    HARD_BLOCK = "HARD_BLOCK"


class EditTier(str, Enum):
    T0_NONE = "T0_NONE"
    T1_LOCAL_STRUCTURAL = "T1_LOCAL_STRUCTURAL"
    T2_CONTRACT_COMPLETION = "T2_CONTRACT_COMPLETION"
    T3_SEMANTIC_CHANGE = "T3_SEMANTIC_CHANGE"
    T4_AUTHORITY_CHANGE_FORBIDDEN = "T4_AUTHORITY_CHANGE_FORBIDDEN"


@dataclass(frozen=True)
class ProjectionHint:
    check: str
    target: str
    operation: str
    tier: EditTier
    rationale: str
    auto_apply: bool = False


@dataclass(frozen=True)
class AssuranceReceipt:
    verdict: Verdict
    core_verdict: Verdict
    projection_status: ProjectionStatus
    hard_boundary_ok: bool
    planning_admissible: bool
    rejected_spectra: tuple[str, ...]
    checks: tuple[Check, ...]
    projection_hints: tuple[ProjectionHint, ...]
    packet_fingerprint: str


_HINTS = {
    "model_class": ProjectionHint(
        "model_class",
        "model.model_class",
        "demote_to_working_model_if_semantics_are_preserved",
        EditTier.T3_SEMANTIC_CHANGE,
        "A generated model cannot self-promote to FACT/TRUTH. Demotion may be proposed but must preserve the intended claim.",
        False,
    ),
    "rollback": ProjectionHint(
        "rollback",
        "action.rollback",
        "supply_real_rollback_target",
        EditTier.T2_CONTRACT_COMPLETION,
        "Rollback metadata must describe a real recovery path; it must never be fabricated.",
        False,
    ),
    "readback": ProjectionHint(
        "readback",
        "action.readback",
        "supply_observable_postcondition",
        EditTier.T2_CONTRACT_COMPLETION,
        "Readback must be an observable postcondition tied to the action; it must never be invented.",
        False,
    ),
    "authority": ProjectionHint(
        "authority",
        "action.authority",
        "require_explicit_authority_or_reduce_side_effect",
        EditTier.T4_AUTHORITY_CHANGE_FORBIDDEN,
        "Authority is a hard boundary. OPUS may not infer, escalate, or manufacture permission.",
        False,
    ),
    "source_before_claim": ProjectionHint(
        "source_before_claim",
        "evidence.source/provenance",
        "supply_real_source_and_provenance",
        EditTier.T2_CONTRACT_COMPLETION,
        "Evidence identity and provenance must be supplied from a real source; OPUS may not synthesize them.",
        False,
    ),
    "retorsion_semantic_direction": ProjectionHint(
        "retorsion_semantic_direction",
        "metadata.retorsion_edges",
        "remove_semantic_authority_inversion",
        EditTier.T3_SEMANTIC_CHANGE,
        "Backward information flow is permitted; backward truth or authority promotion is not.",
        False,
    ),
}


def _projection_status(verdict: Verdict, planning_admissible: bool) -> ProjectionStatus:
    if verdict is Verdict.BLOCK:
        return ProjectionStatus.HARD_BLOCK
    if not planning_admissible or verdict is Verdict.UNKNOWN:
        return ProjectionStatus.UNRESOLVED
    if verdict is Verdict.REPAIR:
        return ProjectionStatus.REPAIR_CANDIDATE
    return ProjectionStatus.IDENTITY


def _hints(checks: Iterable[Check], rejected_spectra: tuple[str, ...]) -> tuple[ProjectionHint, ...]:
    out: list[ProjectionHint] = []
    for check in checks:
        if check.verdict is Verdict.PASS:
            continue
        hint = _HINTS.get(check.name)
        if hint is not None:
            out.append(hint)
    if rejected_spectra:
        out.append(
            ProjectionHint(
                "spectrum_type",
                "metadata.spectra",
                "classify_explicitly_without_metaphor_to_solver_inference",
                EditTier.T2_CONTRACT_COMPLETION,
                "Unknown spectrum labels remain unresolved until explicitly typed; no physical or mathematical solver is inferred from display language.",
                False,
            )
        )
    return tuple(out)


def assure(
    packet: MissionPacket,
    *,
    planning_admissible: bool = True,
    rejected_spectra: tuple[str, ...] = (),
) -> AssuranceReceipt:
    """Evaluate one candidate against the OPUS admissibility boundary.

    Geometric interpretation:
      PASS     -> candidate already belongs to the admissible set (identity projection)
      REPAIR   -> a bounded repair candidate exists, but OPUS does not auto-apply it
      UNKNOWN  -> the admissible set cannot be resolved from available evidence/contracts
      BLOCK    -> reaching the admissible set would cross a hard boundary

    This function does not execute tools, grant authority, or mutate the packet.
    """
    result = evaluate(packet)
    effective = result.verdict
    if effective is Verdict.PASS and not planning_admissible:
        effective = Verdict.UNKNOWN
    status = _projection_status(effective, planning_admissible)
    hard_ok = effective is not Verdict.BLOCK
    packet_payload = {
        "mission": packet.mission,
        "evidence": packet.evidence.__dict__,
        "model": packet.model.__dict__,
        "action": packet.action.__dict__,
        "metadata": packet.metadata,
        "planning_admissible": planning_admissible,
        "rejected_spectra": rejected_spectra,
    }
    return AssuranceReceipt(
        verdict=effective,
        core_verdict=result.verdict,
        projection_status=status,
        hard_boundary_ok=hard_ok,
        planning_admissible=planning_admissible,
        rejected_spectra=rejected_spectra,
        checks=result.checks,
        projection_hints=_hints(result.checks, rejected_spectra),
        packet_fingerprint=sha256_json(packet_payload),
    )
