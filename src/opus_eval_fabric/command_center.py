from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

from .anti_malfunction import audit_result
from .evaluator import evaluate
from .fingerprint import sha256_json
from .io import mission_from_dict, validate_shape
from .mission_compiler import MissionPlan, compile_mission
from .snapshot import build_snapshot
from .trivector import contacts


class NanoStage(str, Enum):
    K0_LOAD_RESUME = "K0_LOAD_RESUME"
    K1_INTENT_CONSTRAINTS = "K1_INTENT_CONSTRAINTS"
    K2_EVIDENCE_STATE = "K2_EVIDENCE_STATE"
    K3_ROUTE = "K3_ROUTE"
    K4_EXECUTE_BOUNDED = "K4_EXECUTE_BOUNDED"
    K5_VERIFY_READBACK = "K5_VERIFY_READBACK"
    K6_LEARN_PRUNE_STOP = "K6_LEARN_PRUNE_STOP"


@dataclass(frozen=True)
class CommandCenterReceipt:
    verdict: str
    core_verdict: str
    planning_admissible: bool
    stages: tuple[str, ...]
    mission_fingerprint: str
    snapshot_root: str
    spectra: tuple[str, ...]
    rejected_spectra: tuple[str, ...]
    tri_vector_contacts: int
    integrity_ok: bool
    stop_state: str


def _stop_state(verdict: str) -> str:
    return {
        "PASS": "STOP_SUFFICIENT_FOR_DECLARED_SCOPE",
        "REPAIR": "STOP_REPAIR_REQUIRED",
        "BLOCK": "STOP_BLOCKED",
        "UNKNOWN": "STOP_UNKNOWN_NEEDS_EVIDENCE",
    }.get(verdict, "STOP_UNKNOWN")


def run_command_center(data: dict[str, Any]) -> tuple[MissionPlan, CommandCenterReceipt]:
    errors = validate_shape(data)
    if errors:
        raise ValueError("; ".join(errors))
    plan = compile_mission(data)
    packet = mission_from_dict(data)
    result = evaluate(packet)
    findings = audit_result(result)
    effective_verdict = result.verdict.value if plan.spectra.admissible else "UNKNOWN"
    checks_payload = [
        {"name": c.name, "verdict": c.verdict.value, "detail": c.detail}
        for c in result.checks
    ]
    snapshot = build_snapshot(
        {
            "mission": data,
            "plan": asdict(plan.signature),
            "planning_admissible": plan.spectra.admissible,
            "core_verdict": result.verdict.value,
            "effective_verdict": effective_verdict,
            "checks": checks_payload,
        }
    )
    receipt = CommandCenterReceipt(
        verdict=effective_verdict,
        core_verdict=result.verdict.value,
        planning_admissible=plan.spectra.admissible,
        stages=tuple(stage.value for stage in NanoStage),
        mission_fingerprint=sha256_json(data),
        snapshot_root=snapshot.root,
        spectra=tuple(x.value for x in plan.spectra.active),
        rejected_spectra=plan.spectra.rejected,
        tri_vector_contacts=len(contacts()),
        integrity_ok=all(x.ok for x in findings),
        stop_state=_stop_state(effective_verdict),
    )
    return plan, receipt
