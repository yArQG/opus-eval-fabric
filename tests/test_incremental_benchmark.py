import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from opus_eval_fabric.incremental_benchmark import run_incremental_benchmark


class IncrementalDogfoodTests(unittest.TestCase):
    def test_pr3_ci_action_pinning_fixture_matches_observed_dependency_plan(self):
        report = run_incremental_benchmark(ROOT / "benchmarks" / "dogfood" / "pr3_ci_action_pinning.json")
        self.assertTrue(report["real_workflow_source"])
        self.assertFalse(report["performance_measured"])
        self.assertTrue(report["structural_pass"])
        self.assertEqual(report["observed"]["changed"], ["file:.github/workflows/ci.yml"])
        self.assertEqual(report["observed"]["reusable_receipts"], ["closed-loop-source-identity-r"])
        self.assertIn("unknown-legacy-r", report["observed"]["invalidated_receipts"])
        self.assertIn("global-release-policy-r", report["observed"]["invalidated_receipts"])


if __name__ == "__main__":
    unittest.main()
