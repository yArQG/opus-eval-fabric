import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from opus_eval_fabric.command_center import NanoStage, run_command_center
from opus_eval_fabric.mission_compiler import compile_mission
from opus_eval_fabric.mission_window import dependency_closure
from opus_eval_fabric.router import Capability, ToolLayer, select_capability
from opus_eval_fabric.semantic_index import SemanticEntry, SemanticIndex, SemanticKey
from opus_eval_fabric.snapshot import build_snapshot
from opus_eval_fabric.spectral import SpectrumClass, centralize_spectra
from opus_eval_fabric.trivector import contacts


class CommandCenterTests(unittest.TestCase):
    def base(self):
        return {
            "mission": "Evaluate a bounded change.",
            "evidence": {"source": "fixture", "provenance": "local", "uncertainty": "LOW"},
            "model": {"claim": "candidate", "model_class": "working_model", "proof_obligation": "behavioral"},
            "action": {"action": "read-only evaluation", "authority": "read-only", "side_effect": "none"},
            "metadata": {
                "spectra": ["EVIDENCE", "SEMANTIC", "CONTROL"],
                "problem_signature": {
                    "object_type": "repository-change",
                    "domain": "software",
                    "representation": "JSON",
                    "goal": "release evaluation"
                }
            }
        }

    def test_spectrum_firewall_rejects_unknown_label(self):
        selection = centralize_spectra(["GRAPH", "quantum-eye"])
        self.assertEqual(selection.active, (SpectrumClass.GRAPH,))
        self.assertEqual(selection.rejected, ("quantum-eye",))
        self.assertFalse(selection.admissible)

    def test_mission_compiler_never_promotes_unknown_spectrum(self):
        data = self.base()
        data["metadata"]["spectra"] = ["PHYSICAL", "metaphor-spectrum"]
        plan = compile_mission(data)
        self.assertIn(SpectrumClass.PHYSICAL, plan.spectra.active)
        self.assertIn("metaphor-spectrum", plan.spectra.rejected)

    def test_mission_window_is_dependency_closure_only(self):
        graph = {"release": ["tests", "rollback"], "tests": ["source"], "rollback": [], "source": [], "unrelated": ["release"]}
        window = dependency_closure(graph, ["release"])
        self.assertEqual(set(window.nodes), {"release", "tests", "rollback", "source"})
        self.assertNotIn("unrelated", window.nodes)

    def test_semantic_index_keeps_machine_identity_separate_from_alias(self):
        index = SemanticIndex()
        key_a = SemanticKey("core", "model", "statistical")
        key_b = SemanticKey("core", "model", "software")
        index.add(SemanticEntry(key_a, "model", ("statistical model",)))
        index.add(SemanticEntry(key_b, "model", ("software model",)))
        resolved = index.resolve_label("model")
        self.assertEqual(set(resolved), {key_a, key_b})
        self.assertEqual(index.get(key_a).key, key_a)

    def test_router_prefers_available_deterministic_low_cost_route(self):
        chosen = select_capability([
            Capability("cloud-llm", ToolLayer.CLOUD, deterministic=False, cost_rank=0, risk_rank=0),
            Capability("local-parser", ToolLayer.LOCAL, deterministic=True, cost_rank=1, risk_rank=0),
            Capability("web-service", ToolLayer.WEB, deterministic=True, cost_rank=5, risk_rank=1)
        ])
        self.assertIsNotNone(chosen)
        self.assertEqual(chosen.capability_id, "local-parser")

    def test_snapshot_root_is_order_independent(self):
        a = build_snapshot({"b": {"x": 2}, "a": {"x": 1}})
        b = build_snapshot({"a": {"x": 1}, "b": {"x": 2}})
        self.assertEqual(a.root, b.root)
        self.assertEqual(a.leaves, b.leaves)

    def test_trivector_has_exactly_24_addressable_contacts(self):
        items = contacts()
        self.assertEqual(len(items), 24)
        self.assertEqual(len({x.address for x in items}), 24)

    def test_command_center_returns_bounded_receipt(self):
        _, receipt = run_command_center(self.base())
        self.assertEqual(receipt.verdict, "PASS")
        self.assertEqual(receipt.core_verdict, "PASS")
        self.assertTrue(receipt.planning_admissible)
        self.assertTrue(receipt.integrity_ok)
        self.assertEqual(receipt.tri_vector_contacts, 24)
        self.assertEqual(len(receipt.stages), len(NanoStage))
        self.assertEqual(receipt.stop_state, "STOP_SUFFICIENT_FOR_DECLARED_SCOPE")

    def test_rejected_spectrum_downgrades_to_unknown_not_pass(self):
        data = self.base()
        data["metadata"]["spectra"] = ["EVIDENCE", "mystery-spectrum"]
        _, receipt = run_command_center(data)
        self.assertEqual(receipt.core_verdict, "PASS")
        self.assertEqual(receipt.verdict, "UNKNOWN")
        self.assertFalse(receipt.planning_admissible)
        self.assertEqual(receipt.stop_state, "STOP_UNKNOWN_NEEDS_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
