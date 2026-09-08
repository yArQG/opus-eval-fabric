import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from opus_eval_fabric.closed_loop import (
    LifecycleState,
    ObservedOutcome,
    prepare_change,
    verify_observed_outcome,
)
from opus_eval_fabric.incremental import ReceiptDependency, affected_dependents, plan_receipt_reuse
from opus_eval_fabric.model import ActionPacket, EvidencePacket, MissionPacket, ModelPacket, Verdict
from opus_eval_fabric.pcc import Postcondition, ProofCarryingChange, ProofObligation


class ClosedLoopAssuranceTests(unittest.TestCase):
    def packet(self, *, authority="repo-write", side_effect="write", rollback="base-sha", readback="git-readback"):
        return MissionPacket(
            mission="Apply one bounded repository change",
            evidence=EvidencePacket("repo", "git", uncertainty="LOW"),
            model=ModelPacket("the change preserves declared invariants", proof_obligation="tests"),
            action=ActionPacket(
                "update repository branch",
                authority=authority,
                side_effect=side_effect,
                rollback=rollback,
                readback=readback,
            ),
            metadata={},
        )

    def change(self, **packet_kwargs):
        return ProofCarryingChange(
            change_id="chg-1",
            packet=self.packet(**packet_kwargs),
            obligations=(ProofObligation("tests", "declared tests pass", "unit-test"),),
            postconditions=(Postcondition("ci", "success"), Postcondition("head_sha", comparator="present")),
        )

    def test_pre_execution_pass_enters_admissible_state(self):
        pre = prepare_change(self.change())
        self.assertEqual(pre.verdict, Verdict.PASS)
        self.assertEqual(pre.lifecycle_state, LifecycleState.ADMISSIBLE)
        self.assertEqual(len(pre.change_fingerprint), 64)

    def test_missing_explicit_obligations_downgrades_otherwise_pass_to_unknown(self):
        change = ProofCarryingChange("chg-empty", self.packet(), (), ())
        pre = prepare_change(change)
        self.assertEqual(pre.assurance.verdict, Verdict.PASS)
        self.assertEqual(pre.verdict, Verdict.UNKNOWN)
        self.assertEqual(pre.lifecycle_state, LifecycleState.UNKNOWN)

    def test_post_observation_pass_closes_verified_loop(self):
        change = self.change()
        pre = prepare_change(change)
        post = verify_observed_outcome(
            change,
            pre,
            ObservedOutcome(
                observations={"ci": "success", "head_sha": "abc123"},
                before_state={"code": "v1", "docs": "same"},
                after_state={"code": "v2", "docs": "same"},
            ),
        )
        self.assertEqual(post.verdict, Verdict.PASS)
        self.assertEqual(post.lifecycle_state, LifecycleState.VERIFIED)
        self.assertEqual(post.changed_keys, ("code",))
        self.assertFalse(post.rollback_recommended)
        self.assertNotEqual(post.before_root, post.after_root)

    def test_postcondition_violation_recommends_rollback_without_executing_it(self):
        change = self.change()
        pre = prepare_change(change)
        post = verify_observed_outcome(
            change,
            pre,
            ObservedOutcome(
                observations={"ci": "failure", "head_sha": "abc123"},
                before_state={"code": "v1"},
                after_state={"code": "v2"},
            ),
        )
        self.assertEqual(post.verdict, Verdict.REPAIR)
        self.assertEqual(post.lifecycle_state, LifecycleState.ROLLBACK_RECOMMENDED)
        self.assertTrue(post.rollback_recommended)

    def test_missing_readback_observation_stays_unknown(self):
        change = self.change()
        pre = prepare_change(change)
        post = verify_observed_outcome(
            change,
            pre,
            ObservedOutcome(
                observations={"head_sha": "abc123"},
                before_state={"code": "v1"},
                after_state={"code": "v2"},
            ),
        )
        self.assertEqual(post.verdict, Verdict.UNKNOWN)
        self.assertEqual(post.lifecycle_state, LifecycleState.UNKNOWN)
        self.assertFalse(post.rollback_recommended)

    def test_execution_without_pre_pass_is_blocked_even_if_outcome_looks_good(self):
        change = self.change(authority="none")
        pre = prepare_change(change)
        self.assertEqual(pre.verdict, Verdict.BLOCK)
        post = verify_observed_outcome(
            change,
            pre,
            ObservedOutcome(
                observations={"ci": "success", "head_sha": "abc123"},
                before_state={"code": "v1"},
                after_state={"code": "v2"},
            ),
        )
        self.assertEqual(post.verdict, Verdict.BLOCK)
        self.assertEqual(post.lifecycle_state, LifecycleState.BLOCKED)

    def test_incremental_reuse_invalidates_only_affected_receipts(self):
        dependents = {
            "source": ("syntax", "tests"),
            "syntax": ("package",),
            "tests": ("release",),
            "docs": ("docs-check",),
        }
        receipts = (
            ReceiptDependency("syntax-r", ("syntax",)),
            ReceiptDependency("release-r", ("release",)),
            ReceiptDependency("docs-r", ("docs-check",)),
            ReceiptDependency("authority-r", ("authority",)),
        )
        plan = plan_receipt_reuse(
            {"source": "v1", "docs": "same"},
            {"source": "v2", "docs": "same"},
            dependents=dependents,
            receipts=receipts,
        )
        self.assertEqual(plan.changed, ("source",))
        self.assertEqual(set(plan.affected), {"source", "syntax", "tests", "package", "release"})
        self.assertEqual(set(plan.invalidated_receipts), {"syntax-r", "release-r"})
        self.assertEqual(set(plan.reusable_receipts), {"docs-r", "authority-r"})

    def test_incremental_dependency_cycles_terminate(self):
        affected = affected_dependents(("a",), {"a": ("b",), "b": ("a", "c")})
        self.assertEqual(set(affected), {"a", "b", "c"})
        self.assertEqual(len(affected), 3)


if __name__ == "__main__":
    unittest.main()
