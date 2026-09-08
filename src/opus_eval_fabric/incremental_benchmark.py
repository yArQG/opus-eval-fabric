from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .incremental import DependencyScope, ReceiptDependency, plan_receipt_reuse


def _sorted_strings(values: Any) -> list[str]:
    return sorted(str(x) for x in values)


def _scope(value: Any) -> DependencyScope:
    try:
        return DependencyScope(str(value).upper())
    except ValueError:
        return DependencyScope.UNKNOWN


def run_incremental_benchmark(path: str | Path) -> dict[str, Any]:
    """Run a side-effect-free historical/dogfood incremental-reuse fixture."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    receipts = tuple(
        ReceiptDependency(
            receipt_id=str(item["receipt_id"]),
            depends_on=tuple(str(x) for x in item.get("depends_on", ())),
            scope=_scope(item.get("scope", "UNKNOWN")),
            source_snapshot_root=(
                str(item["source_snapshot_root"])
                if item.get("source_snapshot_root")
                else None
            ),
        )
        for item in data.get("receipts", ())
    )
    plan = plan_receipt_reuse(
        data.get("before_state", {}),
        data.get("after_state", {}),
        dependents=data.get("dependents", {}),
        receipts=receipts,
    )
    expected = data.get("expected", {})
    observed = {
        "changed": list(plan.changed),
        "affected": list(plan.affected),
        "before_snapshot_root": plan.before_snapshot_root,
        "invalidated_receipts": list(plan.invalidated_receipts),
        "reusable_receipts": list(plan.reusable_receipts),
        "decisions": [
            {
                "receipt_id": d.receipt_id,
                "scope": d.scope.value,
                "reusable": d.reusable,
                "reason": d.reason,
            }
            for d in plan.decisions
        ],
    }
    comparisons = {
        "changed": _sorted_strings(observed["changed"]) == _sorted_strings(expected.get("changed", ())),
        "affected": _sorted_strings(observed["affected"]) == _sorted_strings(expected.get("affected", ())),
        "before_snapshot_root": observed["before_snapshot_root"] == expected.get("before_snapshot_root"),
        "invalidated_receipts": _sorted_strings(observed["invalidated_receipts"]) == _sorted_strings(expected.get("invalidated_receipts", ())),
        "reusable_receipts": _sorted_strings(observed["reusable_receipts"]) == _sorted_strings(expected.get("reusable_receipts", ())),
    }
    return {
        "schema_version": str(data.get("schema_version", "0.3")),
        "benchmark_id": str(data.get("benchmark_id", "incremental")),
        "real_workflow_source": bool(data.get("real_workflow_source", False)),
        "performance_measured": False,
        "provenance": data.get("provenance", {}),
        "observed": observed,
        "expected": expected,
        "comparisons": comparisons,
        "structural_pass": all(comparisons.values()),
        "scope_note": str(data.get("scope_note", "Structural reuse check only; no performance claim.")),
    }
