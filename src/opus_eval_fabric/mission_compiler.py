from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .spectral import SpectralSelection, centralize_spectra


@dataclass(frozen=True)
class ProblemSignature:
    object_type: str
    domain: str
    temporal_scope: str
    uncertainty: str
    evidence_mode: str
    representation: str
    goal: str
    proof_obligation: str


@dataclass(frozen=True)
class MissionPlan:
    mission: str
    signature: ProblemSignature
    spectra: SpectralSelection
    requested_capabilities: tuple[str, ...]


def compile_mission(data: dict[str, Any]) -> MissionPlan:
    """Compile explicit mission metadata into a typed plan.

    The compiler deliberately does not infer a mathematical solver from words
    such as 'quantum', 'spectrum', 'graph', or other display metaphors.
    """
    metadata = data.get("metadata", {})
    model = data.get("model", {})
    evidence = data.get("evidence", {})
    signature_data = metadata.get("problem_signature", {})
    signature = ProblemSignature(
        object_type=str(signature_data.get("object_type", "UNKNOWN")),
        domain=str(signature_data.get("domain", "GENERAL")),
        temporal_scope=str(signature_data.get("temporal_scope", "NOW")),
        uncertainty=str(signature_data.get("uncertainty", evidence.get("uncertainty", "UNKNOWN"))),
        evidence_mode=str(signature_data.get("evidence_mode", "DECLARED")),
        representation=str(signature_data.get("representation", "JSON")),
        goal=str(signature_data.get("goal", data.get("mission", ""))),
        proof_obligation=str(signature_data.get("proof_obligation", model.get("proof_obligation", "empirical"))),
    )
    spectra = centralize_spectra(metadata.get("spectra", ("EVIDENCE", "SEMANTIC", "CONTROL")))
    capabilities = tuple(str(x) for x in metadata.get("requested_capabilities", ()))
    return MissionPlan(
        mission=str(data.get("mission", "")),
        signature=signature,
        spectra=spectra,
        requested_capabilities=capabilities,
    )
