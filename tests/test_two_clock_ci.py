from __future__ import annotations

import unittest

from scripts.two_clock_ci import analyze


class TwoClockCITests(unittest.TestCase):
    def test_separates_queue_and_compute(self):
        report = analyze({
            "created_at": "2026-09-09T18:59:09Z",
            "completed_at": "2026-09-09T18:59:37Z",
            "jobs": [
                {
                    "name": "test (3.11)",
                    "started_at": "2026-09-09T18:59:23Z",
                    "completed_at": "2026-09-09T18:59:37Z",
                },
                {
                    "name": "test (3.13)",
                    "started_at": "2026-09-09T18:59:22Z",
                    "completed_at": "2026-09-09T18:59:31Z",
                },
            ],
        })
        self.assertEqual(report["end_to_end_s"], 28.0)
        self.assertEqual(report["max_job_elapsed_s"], 14.0)
        self.assertEqual(report["max_start_offset_s"], 14.0)
        self.assertEqual(report["jobs"][0]["start_offset_s"], 14.0)
        self.assertEqual(report["jobs"][0]["job_elapsed_s"], 14.0)

    def test_negative_intervals_fail_closed(self):
        with self.assertRaises(ValueError):
            analyze({
                "created_at": "2026-09-09T18:59:09Z",
                "completed_at": "2026-09-09T18:59:20Z",
                "jobs": [{
                    "name": "bad",
                    "started_at": "2026-09-09T18:59:08Z",
                    "completed_at": "2026-09-09T18:59:10Z",
                }],
            })


if __name__ == "__main__":
    unittest.main()
