from opus_eval_fabric.verifiers import (
    DEFAULT_CONTRACTS,
    DependencyScope,
    VerifierContract,
    compile_required_verifiers,
)


def test_local_change_selects_subset():
    result = compile_required_verifiers(["src/opus_eval_fabric/model.py"], DEFAULT_CONTRACTS)
    assert not result.fail_closed
    assert "core-unit-tests" in result.selected_verifiers
    assert result.selected_verifier_count < result.full_verifier_count


def test_unknown_path_fails_closed():
    result = compile_required_verifiers(["mystery.bin"], DEFAULT_CONTRACTS)
    assert result.fail_closed
    assert result.selected_verifier_count == result.full_verifier_count


def test_unknown_scope_fails_closed():
    contracts = DEFAULT_CONTRACTS + (
        VerifierContract("mystery", ("mystery/*",), DependencyScope.UNKNOWN, False, "probe"),
    )
    result = compile_required_verifiers(["mystery/x"], contracts)
    assert result.fail_closed
    assert result.fail_closed_reason == "UNKNOWN_DEPENDENCY_SCOPE"
