"""OPUS Eval Fabric public API."""
from .model import AuthorityState, EvidenceClass, EvalPacket, EvalResult, Verdict
from .evaluator import evaluate
from .snapshot import canonical_hash, canonical_json
from .verifiers import DependencyScope, VerifierContract, compile_required_verifiers

__all__ = [
    "AuthorityState",
    "EvidenceClass",
    "EvalPacket",
    "EvalResult",
    "Verdict",
    "DependencyScope",
    "VerifierContract",
    "evaluate",
    "canonical_hash",
    "canonical_json",
    "compile_required_verifiers",
]

__version__ = "0.2.0rc1"
