import math

import pytest

from opus_eval_fabric import EvidenceClass, EvalPacket, canonical_hash
from opus_eval_fabric.model import Claim


def test_hash_is_deterministic():
    packet = EvalPacket("p", "g", (Claim("c", EvidenceClass.INFERENCE, ("s",)),))
    assert canonical_hash(packet) == canonical_hash(packet)


def test_mapping_order_does_not_change_hash():
    left = EvalPacket("p", "g", metadata={"b": 2, "a": 1})
    right = EvalPacket("p", "g", metadata={"a": 1, "b": 2})
    assert canonical_hash(left) == canonical_hash(right)


def test_non_string_mapping_keys_fail_closed():
    with pytest.raises(TypeError, match="string keys"):
        canonical_hash({"1": "string", 1: "integer"})


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_non_finite_floats_fail_closed(value):
    with pytest.raises(ValueError, match="Out of range float values"):
        canonical_hash({"value": value})


def test_hash_reflects_current_mutable_metadata_state():
    metadata = {"phase": "before"}
    packet = EvalPacket("p", "g", metadata=metadata)
    before = canonical_hash(packet)
    metadata["phase"] = "after"
    after = canonical_hash(packet)
    assert before != after
