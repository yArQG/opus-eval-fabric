from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evaluator import evaluate, fold_verdict
from .fingerprint import environment_fingerprint, sha256_json
from .io import load_json, mission_from_dict
from .verifiers import ProofObligationVerifier, TransactionCompletenessVerifier, run_verifiers


def _deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = deepcopy(value)
    return out


def run_suite(path: str | Path) -> dict[str, Any]:
    suite = load_json(path)
    results: list[dict[str, Any]] = []
    verifier_set = [ProofObligationVerifier(), TransactionCompletenessVerifier()]

    for case in suite["cases"]:
        base = case["mission"]
        for variant in case["variants"]:
            mission_data = _deep_merge(base, variant.get("patch", {}))
            packet = mission_from_dict(mission_data)
            core = evaluate(packet)
            extra = run_verifiers(packet, verifier_set)
            expected = variant["expected"]
            all_checks = tuple(core.checks) + tuple(extra)
            observed = fold_verdict(list(all_checks)).value
            matched = observed == expected
            results.append(
                {
                    "case_id": case["id"],
                    "variant_id": variant["id"],
                    "description": variant.get("description", ""),
                    "expected": expected,
                    "observed": observed,
                    "matched": matched,
                    "mission_sha256": sha256_json(mission_data),
                    "core_checks": [
                        {"name": c.name, "verdict": c.verdict.value, "detail": c.detail}
                        for c in core.checks
                    ],
                    "auxiliary_verifiers": [
                        {"name": c.name, "verdict": c.verdict.value, "detail": c.detail}
                        for c in extra
                    ],
                    "effective_checks": [
                        {"name": c.name, "verdict": c.verdict.value, "detail": c.detail}
                        for c in all_checks
                    ],
                }
            )

    passed = sum(1 for r in results if r["matched"])
    false_passes = sum(
        1 for r in results
        if r["observed"] == "PASS" and r["expected"] != "PASS"
    )
    total = len(results)
    return {
        "schema_version": "0.2",
        "suite_id": suite["suite_id"],
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "suite_sha256": sha256_json(suite),
        "environment": environment_fingerprint(),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "false_passes": false_passes,
            "fixture_match_rate": (passed / total) if total else 0.0,
        },
        "results": results,
        "scope_note": (
            "Fixture match rate measures this deterministic suite only. "
            "It is not a real-world agent accuracy or safety metric."
        ),
    }
