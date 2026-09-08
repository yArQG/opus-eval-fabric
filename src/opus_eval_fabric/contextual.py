from __future__ import annotations


def contextual_variants(text: str) -> dict[str, str]:
    """Cheap deterministic perturbations.

    These variants test formatting/context sensitivity only. They are not
    semantic-equivalence proofs.
    """
    compact = " ".join(text.split())
    return {
        "baseline": text,
        "whitespace_normalized": compact,
        "quoted": f'"{compact}"',
        "explicit_task_prefix": f"Task: {compact}",
        "explicit_evidence_prefix": f"Evidence-grounded task: {compact}",
        "explicit_uncertainty_prefix": f"If evidence is insufficient, return UNKNOWN. Task: {compact}",
        "instruction_suffix": f"{compact}\nPreserve evidence/action boundaries.",
    }
