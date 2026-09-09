import unittest
from scripts.paired_install_ci import orders, summarize


class PairingTests(unittest.TestCase):
    def test_balanced_order_and_blocks(self):
        a, b = orders(4, 0), orders(4, 1)
        self.assertEqual(a.count(('baseline', 'explicit')), 2)
        self.assertEqual(b, [tuple(reversed(x)) for x in a])
        for n in (0, 1, 3, 12):
            with self.assertRaises(ValueError): orders(n, 0)

    def test_pairs_preserved_in_descriptive_deltas(self):
        rows = [{'pair': i, 'variant': v, 'status': 'PASS', 'install_total_s': t}
                for i, v, t in [(0, 'baseline', 10), (1, 'explicit', 21), (0, 'explicit', 8), (1, 'baseline', 20)]]
        r = summarize(rows)
        self.assertEqual(r['paired_deltas_s'], [-2, 1])
        self.assertEqual(r['promotion'], 'BLOCKED_PILOT_ONLY')
        with self.assertRaises(ValueError): summarize(rows[:-1])
        with self.assertRaises(ValueError): summarize(rows + rows)
        rows[0]['status'] = 'FAIL'
        with self.assertRaises(ValueError): summarize(rows)
