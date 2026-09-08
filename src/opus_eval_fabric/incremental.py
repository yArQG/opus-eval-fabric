from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .fingerprint import sha256_json


@dataclass(frozen=True)
class ReceiptDependency:
    receipt_id: str
    depends_on: tuple[str, ...]


@dataclass(frozen=True)
class ReusePlan:
    changed: tuple[str, ...]
    affected: tuple[str, ...]
    reusable_receipts: tuple[str, ...]
    invalidated_receipts: tuple[str, ...]


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
    changed = changed_keys(before, after)
    affected = affected_dependents(changed, dependents)
    affected_set = set(affected)
    reusable: list[str] = []
    invalidated: list[str] = []
    for receipt in receipts:
        target = invalidated if affected_set.intersection(receipt.depends_on) else reusable
        target.append(receipt.receipt_id)
    return ReusePlan(changed, affected, tuple(reusable), tuple(invalidated))
