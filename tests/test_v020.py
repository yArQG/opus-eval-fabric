import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from opus_eval_fabric.adapters.python import PythonAdapter
from opus_eval_fabric.benchmark import run_suite
from opus_eval_fabric.fingerprint import sha256_json
from opus_eval_fabric.reporting import write_junit_report


class BenchmarkTests(unittest.TestCase):
    def test_foundation_suite_matches_all_expected_verdicts(self):
        report = run_suite(ROOT / "benchmarks" / "suite.json")
        self.assertEqual(report["summary"]["failed"], 0)
        self.assertEqual(report["summary"]["passed"], 7)
        self.assertEqual(report["summary"]["false_passes"], 0)
        self.assertEqual(report["summary"]["fixture_match_rate"], 1.0)

    def test_suite_has_three_distinct_workflow_families(self):
        data = json.loads((ROOT / "benchmarks" / "suite.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["cases"]), 3)
        self.assertEqual(len({case["id"] for case in data["cases"]}), 3)

    def test_junit_report_is_written(self):
        report = run_suite(ROOT / "benchmarks" / "suite.json")
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "report.xml"
            write_junit_report(report, out)
            text = out.read_text(encoding="utf-8")
            self.assertIn("testsuite", text)
            self.assertIn('failures="0"', text)


class FingerprintTests(unittest.TestCase):
    def test_canonical_hash_ignores_dict_key_order(self):
        self.assertEqual(sha256_json({"a": 1, "b": 2}), sha256_json({"b": 2, "a": 1}))


class PythonAdapterTests(unittest.TestCase):
    def test_python_adapter_detects_current_runtime(self):
        status = PythonAdapter().detect()
        self.assertTrue(status.available)
        self.assertTrue(status.version)

    def test_python_adapter_checks_syntax_without_execution(self):
        adapter = PythonAdapter()
        ok, _ = adapter.check_syntax("x = 1 + 2")
        bad, _ = adapter.check_syntax("def broken(:\n    pass")
        self.assertTrue(ok)
        self.assertFalse(bad)


if __name__ == "__main__":
    unittest.main()
