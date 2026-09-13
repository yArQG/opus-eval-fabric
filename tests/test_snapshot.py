from opus_eval_fabric import EvidenceClass, EvalPacket, canonical_hash
from opus_eval_fabric.model import Claim


def test_hash_is_deterministic():
    packet = EvalPacket("p", "g", (Claim("c", EvidenceClass.INFERENCE, ("s",)),))
    assert canonical_hash(packet) == canonical_hash(packet)
