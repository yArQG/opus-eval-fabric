from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from fnmatch import fnmatch
import hashlib
import json
from typing import Iterable, Sequence


class DependencyScope(str, Enum):
    LOCAL = "LOCAL"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class VerifierContract:
    verifier_id: str
    dependency_patterns: tuple[str, ...]
    scope: DependencyScope
    hard_gate: bool
    method_family: str
    cost_class: str = "UNKNOWN"

    def matches(self, object_id: str) -> bool:
        return any(fnmatch(object_id, p) for p in self.dependency_patterns)


@dataclass(frozen=True)
class VerificationSelection:
    changed_objects: tuple[str, ...]
    selected_verifiers: tuple[str, ...]
    unclassified_objects: tuple[str, ...]
    unknown_scope_matches: tuple[str, ...]
    full_verifier_count: int
    selected_verifier_count: int
    planned_reduction: float
    fail_closed: bool
    fail_closed_reason: str | None
    contract_fingerprint: str


def _payload(c: VerifierContract) -> dict:
    d = asdict(c)
    d["scope"] = c.scope.value
    return d


def contract_fingerprint(contracts: Sequence[VerifierContract]) -> str:
    payload = [_payload(c) for c in sorted(contracts, key=lambda x: x.verifier_id)]
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def validate_contracts(contracts: Sequence[VerifierContract]) -> tuple[str, ...]:
    errors: list[str] = []
    ids = [c.verifier_id for c in contracts]
    duplicates = sorted({x for x in ids if ids.count(x) > 1})
    if duplicates:
        errors.append("duplicate verifier_id: " + ",".join(duplicates))
    for c in contracts:
        if not c.verifier_id.strip():
            errors.append("empty verifier_id")
        if not c.method_family.strip():
            errors.append(f"{c.verifier_id}: empty method_family")
        if c.scope is DependencyScope.LOCAL and not c.dependency_patterns:
            errors.append(f"{c.verifier_id}: LOCAL requires dependency patterns")
        if c.hard_gate and c.scope is DependencyScope.UNKNOWN:
            errors.append(f"{c.verifier_id}: hard gate cannot use UNKNOWN scope")
    return tuple(errors)


def compile_required_verifiers(changed_objects: Iterable[str], contracts: Sequence[VerifierContract]) -> VerificationSelection:
    errors = validate_contracts(contracts)
    if errors:
        raise ValueError("; ".join(errors))

    changed = tuple(dict.fromkeys(str(x) for x in changed_objects))
    full = tuple(c.verifier_id for c in contracts)
    selected: list[str] = [c.verifier_id for c in contracts if c.hard_gate]
    unclassified: list[str] = []
    unknown_scope_matches: list[str] = []

    for object_id in changed:
        matched = [c for c in contracts if c.matches(object_id)]
        mapping = [c for c in matched if not c.hard_gate]
        known = [c for c in mapping if c.scope is not DependencyScope.UNKNOWN]
        unknown = [c for c in mapping if c.scope is DependencyScope.UNKNOWN]
        if unknown:
            unknown_scope_matches.append(object_id)
        if not known and not unknown:
            unclassified.append(object_id)
        for c in matched:
            if c.verifier_id not in selected:
                selected.append(c.verifier_id)

    reason = None
    if unclassified:
        reason = "UNCLASSIFIED_OBJECT"
    elif unknown_scope_matches:
        reason = "UNKNOWN_DEPENDENCY_SCOPE"
    fail_closed = reason is not None
    if fail_closed:
        selected = list(full)

    full_count = len(full)
    selected_count = len(selected)
    reduction = 0.0 if full_count == 0 else 1.0 - selected_count / full_count
    return VerificationSelection(
        changed, tuple(selected), tuple(unclassified), tuple(unknown_scope_matches),
        full_count, selected_count, reduction, fail_closed, reason,
        contract_fingerprint(contracts),
    )


DEFAULT_CONTRACTS = (
    VerifierContract("authority-invariants", ("*",), DependencyScope.GLOBAL, True, "authority-policy", "LOW"),
    VerifierContract("provenance-invariants", ("*",), DependencyScope.GLOBAL, True, "provenance-policy", "LOW"),
    VerifierContract("core-unit-tests", ("src/opus_eval_fabric/*.py", "tests/*.py"), DependencyScope.LOCAL, False, "python-unit", "MEDIUM"),
    VerifierContract("docs-consistency", ("README.md", "docs/*.md", "CHANGELOG.md"), DependencyScope.LOCAL, False, "docs", "LOW"),
    VerifierContract("ci-integrity", (".github/workflows/*.yml", ".github/workflows/*.yaml"), DependencyScope.LOCAL, False, "ci", "LOW"),
    VerifierContract("packaging-install", ("pyproject.toml", "src/opus_eval_fabric/__init__.py"), DependencyScope.LOCAL, False, "packaging", "MEDIUM"),
)
