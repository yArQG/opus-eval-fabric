import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from opus_eval_fabric.assurance_kernel import EditTier, ProjectionStatus, assure
from opus_eval_fabric.io import mission_from_dict
from opus_eval_fabric.model import Verdict


class AssuranceKernelTests(unittest.TestCase):
    def base(self):
        return {
            "mission": "Evaluate a bounded change.",
            "evidence": {
                "source": "fixture",
                "provenance": "local",
                "uncertainty": "LOW",
            },
            "model": {
                "claim": "candidate",
                "model_class": "working_model",
                "proof_obligation": "behavioral",
            },
            "action": {
                "action": "read-only evaluation",
                "authority": "read-only",
                "side_effect": "none",
            },
            "metadata": {},
        }

    def test_pass_is_identity_projection(self):
        receipt = assure(mission_from_dict(self.base()))
        self.assertEqual(receipt.verdict, Verdict.PASS)
        self.assertEqual(receipt.projection_status, ProjectionStatus.IDENTITY)
        self.assertTrue(receipt.hard_boundary_ok)
        self.assertEqual(receipt.projection_hints, ())

    def test_missing_rollback_is_repair_candidate_not_auto_mutation(self):
        data = self.base()
        data["action"] = {
            "action": "write file",
            "authority": "authorized",
            "side_effect": "write",
            "readback": "verify content hash",
        }
        receipt = assure(mission_from_dict(data))
        self.assertEqual(receipt.verdict, Verdict.REPAIR)
        self.assertEqual(receipt.projection_status, ProjectionStatus.REPAIR_CANDIDATE)
        self.assertTrue(receipt.hard_boundary_ok)
        self.assertTrue(any(h.check == "rollback" for h in receipt.projection_hints))
        self.assertTrue(all(not h.auto_apply for h in receipt.projection_hints))

    def test_missing_authority_is_hard_block_and_never_projected(self):
        data = self.base()
        data["action"] = {
            "action": "write file",
            "authority": "none",
            "side_effect": "write",
            "rollback": "restore previous blob",
            "readback": "verify content hash",
        }
        receipt = assure(mission_from_dict(data))
        self.assertEqual(receipt.verdict, Verdict.BLOCK)
        self.assertEqual(receipt.projection_status, ProjectionStatus.HARD_BLOCK)
        self.assertFalse(receipt.hard_boundary_ok)
        authority = [h for h in receipt.projection_hints if h.check == "authority"]
        self.assertEqual(len(authority), 1)
        self.assertEqual(authority[0].tier, EditTier.T4_AUTHORITY_CHANGE_FORBIDDEN)
        self.assertFalse(authority[0].auto_apply)

    def test_unknown_spectrum_turns_pass_into_unknown(self):
        receipt = assure(
            mission_from_dict(self.base()),
            planning_admissible=False,
            rejected_spectra=("quantum-eye",),
        )
        self.assertEqual(receipt.core_verdict, Verdict.PASS)
        self.assertEqual(receipt.verdict, Verdict.UNKNOWN)
        self.assertEqual(receipt.projection_status, ProjectionStatus.UNRESOLVED)
        self.assertTrue(any(h.check == "spectrum_type" for h in receipt.projection_hints))

    def test_model_self_promotion_is_semantic_repair_not_evidence_upgrade(self):
        data = self.base()
        data["model"]["model_class"] = "fact"
        receipt = assure(mission_from_dict(data))
        self.assertEqual(receipt.verdict, Verdict.REPAIR)
        model_hints = [h for h in receipt.projection_hints if h.check == "model_class"]
        self.assertEqual(len(model_hints), 1)
        self.assertEqual(model_hints[0].tier, EditTier.T3_SEMANTIC_CHANGE)
        self.assertFalse(model_hints[0].auto_apply)


if __name__ == "__main__":
    unittest.main()
