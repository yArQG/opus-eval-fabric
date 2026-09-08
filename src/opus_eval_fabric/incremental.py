from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Mapping

from .fingerprint import sha256_json
from .snapshot import build_snapshot


class DependencyScope(str, Enum):
    LOCAL = "LOCAL"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ReceiptDependency:
    receipt_id: str
    depends_on: tuple[str, ...]
    scope: DependencyScope = DependencyScope.UNKNOWN
    source_snapshot_root: str | None = None


@dataclass(frozen=True)
class ReuseDecision:
    receipt_id: str
    scope: DependencyScope
    reusable: bool
    reason: str


@dataclass(frozen=True)
class ReusePlan:
    changed: tuple[str, ...]
    affected: tuple[str, ...]
    before_snapshot_root: str
    reusable_receipts: tuple[str, ...]
    invalidated_receipts: tuple[str, ...]
    decisions: tuple[ReuseDecision, ...]


def changed_keys(before: Mapping[str, Any], after: Mapping[str, Any]) -> tuple[str, ...]:
    """Return shallow state keys whose canonical values changed."""
    keys = sorted(set(before) | set(after))
    return tuple(
        str(key)
        for key in keys
        if key not in before
        or key not in after
        or sha256_json(before[key]) != sha256_json(after[key])
    )


def affected_dependents(
    changed: Iterable[str],
    dependents: Mapping[str, Iterable[str]],
) -> tuple[str, ...]:
    """Propagate a typed delta through a source->dependent DAG/graph.

    Cycles are tolerated defensively through a visited set; they are not treated
    as causal evidence and do not authorize any action.
    """
    roots = tuple(dict.fromkeys(str(x) for x in changed))
    seen: set[str] = set()
    stack = list(reversed(roots))
    ordered: list[str] = []
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        ordered.append(node)
        for child in reversed(tuple(str(x) for x in dependents.get(node, ()))):
            if child not in seen:
                stack.append(child)
    return tuple(ordered)


def plan_receipt_reuse(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    dependents: Mapping[str, Iterable[str]],
    receipts: Iterable[ReceiptDependency],
) -> ReusePlan:
    """Plan receipt reuse with fail-closed scope and issuance binding.

    A receipt may be reused only if it is bound to the exact supplied `before`
    snapshot. UNKNOWN scope is never reused automatically. LOCAL reuse requires
    at least one explicit dependency and none may be affected. GLOBAL receipts
    are reusable only when there is no observed delta.
    """
    changed = changed_keys(before, after)
    affected = affected_dependents(changed, dependents)
    affected_set = set(affected)
    before_root = build_snapshot(before).root
    reusable: list[str] = []
    invalidated: list[str] = []
    decisions: list[ReuseDecision] = []

    for receipt in receipts:
        if receipt.scope is DependencyScope.UNKNOWN:
            can_reuse = False
            reason = "unknown_dependency_scope_requires_reverification"
        elif not receipt.source_snapshot_root:
            can_reuse = False
            reason = "missing_receipt_source_snapshot"
        elif receipt.source_snapshot_root != before_root:
            can_reuse = False
            reason = "receipt_not_bound_to_current_before_snapshot"
        elif receipt.scope is DependencyScope.LOCAL and not receipt.depends_on:
            can_reuse = False
            reason = "local_scope_without_declared_dependencies"
        elif not changed:
            can_reuse = True
            reason = "bound_snapshot_has_no_observed_delta"
        elif receipt.scope is DependencyScope.GLOBAL:
            can_reuse = False
            reason = "global_dependency_scope_changed"
        elif affected_set.intersection(receipt.depends_on):
            can_reuse = False
            reason = "declared_dependency_affected"
        else:
            can_reuse = True
            reason = "bound_local_dependencies_unaffected"

        (reusable if can_reuse else invalidated).append(receipt.receipt_id)
        decisions.append(ReuseDecision(receipt.receipt_id, receipt.scope, can_reuse, reason))

    return ReusePlan(
        changed,
        affected,
        before_root,
        tuple(reusable),
        tuple(invalidated),
        tuple(decisions),
    )
