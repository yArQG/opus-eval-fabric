from __future__ import annotations

from dataclasses import dataclass

from .model import EvalResult, Verdict


@dataclass(frozen=True)
class IntegrityFinding:
    name: str
    ok: bool
    detail: str


def audit_result(result: EvalResult) -> tuple[IntegrityFinding, ...]:
    """Check structural contradictions in an evaluation result."""
    findings: list[IntegrityFinding] = []
    if result.verdict is Verdict.PASS:
        bad = [c for c in result.checks if c.verdict is not Verdict.PASS]
        findings.append(
            IntegrityFinding(
                "pass_consistency",
                not bad,
                "PASS has only PASS checks" if not bad else "PASS conflicts with non-PASS checks",
            )
        )
    else:
        findings.append(IntegrityFinding("pass_consistency", True, "non-PASS result does not self-promote"))

    names = [c.name for c in result.checks]
    findings.append(
        IntegrityFinding(
            "check_identity",
            len(names) == len(set(names)),
            "check names are unique" if len(names) == len(set(names)) else "duplicate check identity",
        )
    )
    return tuple(findings)
