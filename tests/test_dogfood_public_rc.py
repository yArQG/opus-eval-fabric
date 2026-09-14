from opus_eval_fabric import (
    AuthorityState,
    EvidenceClass,
    EvalPacket,
    Verdict,
    canonical_hash,
    evaluate,
)
from opus_eval_fabric.model import Claim
from opus_eval_fabric.verifiers import DEFAULT_CONTRACTS, compile_required_verifiers


def test_public_rc_ci_claim_has_provenance_and_passes_without_effect():
    packet = EvalPacket(
        packet_id="dogfood-public-rc-ci",
        goal="Evaluate a measured CI claim without authorizing any external action",
        claims=(
            Claim(
                text="The release-candidate CI run completed successfully",
                evidence_class=EvidenceClass.MEASUREMENT,
                source_refs=("github-actions:run-34787234105",),
            ),
        ),
        authority=AuthorityState.REVIEW,
        action_requested=False,
    )
    result = evaluate(packet)
    assert result.verdict is Verdict.PASS
    assert len(canonical_hash(packet)) == 64


def test_same_claim_cannot_authorize_an_effectful_action():
    packet = EvalPacket(
        packet_id="dogfood-public-rc-authority",
        goal="Prove technical evidence does not grant action authority",
        claims=(
            Claim(
                text="The release-candidate CI run completed successfully",
                evidence_class=EvidenceClass.MEASUREMENT,
                source_refs=("github-actions:run-34787234105",),
            ),
        ),
        authority=AuthorityState.REVIEW,
        action_requested=True,
    )
    assert evaluate(packet).verdict is Verdict.BLOCK


def test_real_changed_model_path_selects_only_required_verifiers():
    result = compile_required_verifiers(
        ["src/opus_eval_fabric/model.py"],
        DEFAULT_CONTRACTS,
    )
    assert result.fail_closed is False
    assert result.selected_verifiers == (
        "authority-invariants",
        "provenance-invariants",
        "core-unit-tests",
    )
    assert result.full_verifier_count == 6
    assert result.selected_verifier_count == 3
    assert result.planned_reduction == 0.5


def test_real_unclassified_change_fails_closed_to_full_verification():
    result = compile_required_verifiers(["unmapped/new-format.bin"], DEFAULT_CONTRACTS)
    assert result.fail_closed is True
    assert result.fail_closed_reason == "UNCLASSIFIED_OBJECT"
    assert result.selected_verifier_count == result.full_verifier_count
