import copy
import unittest
from scripts.two_clock_ci import analyze


def fixture():
    return {'created_at': '2026-09-09T00:00:00Z', 'completed_at': '2026-09-09T00:00:30Z',
            'jobs': [{'name': 'build', 'started_at': '2026-09-09T00:00:02Z', 'completed_at': '2026-09-09T00:00:12Z'},
                     {'name': 'test', 'started_at': '2026-09-09T00:00:15Z', 'completed_at': '2026-09-09T00:00:25Z'}],
            'dependencies': {'build': [], 'test': ['build']}}


class TimingBoundaries(unittest.TestCase):
    def test_chain_is_not_max_job(self):
        r = analyze(fixture())
        self.assertEqual(r['max_job_elapsed_s'], 10)
        self.assertEqual(r['execution_path_elapsed_s'], 20)
        self.assertEqual(r['jobs'][1]['dependency_wait_s'], 12)
        self.assertEqual(r['jobs'][1]['ready_to_start_s'], 3)
        self.assertEqual(r['finalization_s'], 5)

    def test_unknown_topology_is_not_parallel(self):
        p = fixture(); del p['dependencies']
        self.assertIsNone(analyze(p)['execution_path_elapsed_s'])

    def test_rejects_invalid_evidence(self):
        cases = []
        p = fixture(); p['completed_at'] = '2026-09-08T23:59:59Z'; cases.append(p)
        p = fixture(); p['completed_at'] = '2026-09-09T00:00:20Z'; cases.append(p)
        p = fixture(); p['jobs'] = []; cases.append(p)
        p = fixture(); p['jobs'][1]['name'] = 'build'; cases.append(p)
        p = fixture(); p['created_at'] = '2026-09-09T00:00:00'; cases.append(p)
        for deps in ({'build': [], 'test': ['absent']}, {'build': ['test'], 'test': ['build']}, {'build': []}):
            p = fixture(); p['dependencies'] = deps; cases.append(p)
        p = fixture(); p['jobs'][1]['started_at'] = '2026-09-09T00:00:10Z'; cases.append(p)
        for p in cases:
            with self.subTest(payload=p), self.assertRaises(ValueError):
                analyze(p)

    def test_noncoincident_maxima_do_not_add(self):
        p = fixture(); p['dependencies'] = {'build': [], 'test': []}
        p['jobs'][0]['completed_at'] = '2026-09-09T00:00:22Z'
        r = analyze(p)
        self.assertNotEqual(r['end_to_end_s'], r['max_start_offset_s'] + r['max_job_elapsed_s'])
