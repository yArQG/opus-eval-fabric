from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from .assurance_kernel import AssuranceReceipt, assure
from .fingerprint import sha256_json
from .incremental import changed_keys
from .model import Check, Verdict
from .pcc import Postcondition, ProofCarryingChange
from .snapshot import build_snapshot


class LifecycleState(str, Enum):
    PROPOSED = "PROPOSED"
    ADMISSIBLE = "ADMISSIBLE"
    VERIFIED = "VERIFIED"
    ROLLBACK_RECOMMENDED = "ROLLBACK_RECOMMENDED"
    UNKNOWN = "UNKNOWN"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class ObservedOutcome:
    observations: Mapping[str, Any]
    before_state: Mapping[str, Any]
    after_state: Mapping[str, Any]


@dataclass(frozen=True)
class PreExecutionReceipt:
    change_id: str
    verdict: Verdict
    lifecycle_state: LifecycleState
    assurance: AssuranceReceipt
    change_fingerprint: str


@dataclass(frozen=True)
class PostExecutionReceipt:
    change_id: str
    verdict: Verdict
    lifecycle_state: LifecycleState
    checks: tuple[Check, ...]
    observation_fingerprint: str
    before_root: str
    after_root: str
    changed_keys: tuple[str, ...]
    rollback_recommended: bool


def prepare_change(
    change: ProofCarryingChange,
    *,
    planning_admissible: bool = True,
    rejected_spectra: tuple[str, ...] = (),
) -> PreExecutionReceipt:
    assurance = assure(
        change.packet,
        planning_admissible=planning_admissible,
        rejected_spectra=rejected_spectra,
    )
    if assurance.verdict is Verdict.PASS and not change.obligations:
        verdict = Verdict.UNKNOWN
        state = LifecycleState.UNKNOWN
    else:
        verdict = assurance.verdict
        state = {
            Verdict.PASS: LifecycleState.ADMISSIBLE,
            Verdict.REPAIR: LifecycleState.UNKNOWN,
            Verdict.UNKNOWN: LifecycleState.UNKNOWN,
            Verdict.BLOCK: LifecycleState.BLOCKED,
        }[verdict]
    return PreExecutionReceipt(
        change_id=change.change_id,
        verdict=verdict,
        lifecycle_state=state,
        assurance=assurance,
        change_fingerprint=change.fingerprint(),
    )


def _check_postcondition(post: Postcondition, observations: Mapping[str, Any]) -> Check:
    comparator = post.comparator.lower().strip()
    if comparator == "present":
        if post.key in observations:
            return Check(f"post:{post.key}", Verdict.PASS, "observation present")
        return Check(f"post:{post.key}", Verdict.UNKNOWN, "required observation missing")
    if comparator == "eq":
        if post.key not in observations:
            return Check(f"post:{post.key}", Verdict.UNKNOWN, "required observation missing")
        if observations[post.key] == post.expected:
            return Check(f"post:{post.key}", Verdict.PASS, "observed value matches declared postcondition")
        return Check(f"post:{post.key}", Verdict.REPAIR, "observed value violates declared postcondition")
    return Check(f"post:{post.key}", Verdict.UNKNOWN, f"unsupported comparator: {post.comparator}")


def verify_observed_outcome(
    change: ProofCarryingChange,
    pre: PreExecutionReceipt,
    outcome: ObservedOutcome,
) -> PostExecutionReceipt:
    """Verify observed postconditions after an externally performed action.

    This function never executes the action. If the action was not pre-admitted,
    the post receipt is BLOCK even if observations happen to look successful.
    """
    before = build_snapshot(outcome.before_state)
    after = build_snapshot(outcome.after_state)
    delta = changed_keys(outcome.before_state, outcome.after_state)

    checks: list[Check] = []
    if pre.verdict is not Verdict.PASS:
        checks.append(Check("pre_execution_admission", Verdict.BLOCK, "execution lacks a PASS pre-execution receipt"))
    else:
        checks.append(Check("pre_execution_admission", Verdict.PASS, "pre-execution receipt admitted the candidate"))

    if not change.postconditions:
        checks.append(Check("postcondition_coverage", Verdict.UNKNOWN, "no explicit postconditions declared"))
    else:
        checks.extend(_check_postcondition(p, outcome.observations) for p in change.postconditions)

    priority = {Verdict.PASS: 0, Verdict.UNKNOWN: 1, Verdict.REPAIR: 2, Verdict.BLOCK: 3}
    verdict = max((x.verdict for x in checks), key=priority.__getitem__, default=Verdict.UNKNOWN)
    state = {
        Verdict.PASS: LifecycleState.VERIFIED,
        Verdict.REPAIR: LifecycleState.ROLLBACK_RECOMMENDED,
        Verdict.UNKNOWN: LifecycleState.UNKNOWN,
        Verdict.BLOCK: LifecycleState.BLOCKED,
    }[verdict]
    return PostExecutionReceipt(
        change_id=change.change_id,
        verdict=verdict,
        lifecycle_state=state,
        checks=tuple(checks),
        observation_fingerprint=sha256_json(
            {
                "observations": dict(outcome.observations),
                "before_root": before.root,
                "after_root": after.root,
            }
        ),
        before_root=before.root,
        after_root=after.root,
        changed_keys=delta,
        rollback_recommended=verdict is Verdict.REPAIR,
    )
