import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from opus_eval_fabric.benchmark import run_suite


class BenchmarkVerifierAggregationTests(unittest.TestCase):
    def test_auxiliary_verifier_can_change_effective_verdict(self):
        suite = {
            "suite_id": "aux-verifier-aggregation",
            "cases": [{
                "id": "proof-obligation",
                "mission": {
                    "mission": "aggregation test",
                    "evidence": {"source": "fixture", "provenance": "local", "uncertainty": "LOW"},
                    "model": {"claim": "candidate", "model_class": "working_model", "proof_obligation": "not-a-known-class"},
                    "action": {"action": "read", "authority": "read-only", "side_effect": "none"},
                    "metadata": {"retorsion_edges": []}
                },
                "variants": [{"id": "unknown-obligation", "patch": {}, "expected": "UNKNOWN"}]
            }]
        }
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "suite.json"
            path.write_text(json.dumps(suite), encoding="utf-8")
            report = run_suite(path)
        self.assertEqual(report["summary"]["failed"], 0)
        self.assertEqual(report["results"][0]["observed"], "UNKNOWN")
        self.assertIn("proof_obligation", {c["name"] for c in report["results"][0]["effective_checks"]})


if __name__ == "__main__":
    unittest.main()
