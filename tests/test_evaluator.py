from opus_eval_fabric import AuthorityState, EvidenceClass, EvalPacket, Verdict, evaluate
from opus_eval_fabric.model import Claim


def test_fact_requires_source():
    packet = EvalPacket("p1", "test", (Claim("x", EvidenceClass.FACT),))
    assert evaluate(packet).verdict is Verdict.REPAIR


def test_authorized_action_can_pass():
    packet = EvalPacket(
        "p2",
        "test",
        (Claim("x", EvidenceClass.FACT, ("source:1",)),),
        AuthorityState.AUTHORIZED,
        True,
    )
    assert evaluate(packet).verdict is Verdict.PASS


def test_action_without_authority_blocks():
    packet = EvalPacket("p3", "test", (), AuthorityState.REVIEW, True)
    assert evaluate(packet).verdict is Verdict.BLOCK


def test_unknown_requires_note():
    packet = EvalPacket("p4", "test", (Claim("x", EvidenceClass.UNKNOWN),))
    assert evaluate(packet).verdict is Verdict.REPAIR
