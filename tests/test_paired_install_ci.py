import unittest
from scripts.paired_install_ci import orders, summarize


class PairingTests(unittest.TestCase):
    def test_balanced_order_and_blocks(self):
        a, b = orders(4, 0), orders(4, 1)
        self.assertEqual(a.count(('baseline', 'explicit')), 2)
        self.assertEqual(b, [tuple(reversed(x)) for x in a])
        for n in (0, 1, 3, 12):
            with self.assertRaises(ValueError): orders(n, 0)
        with self.assertRaises(ValueError): orders(4, 2)

    def test_pairs_preserved_in_descriptive_deltas(self):
        rows = [{'pair': i, 'position': position, 'variant': v, 'status': 'PASS', 'install_total_s': t}
                for i, position, v, t in [(0, 0, 'baseline', 10), (1, 0, 'explicit', 21), (0, 1, 'explicit', 8), (1, 1, 'baseline', 20)]]
        r = summarize(rows)
        self.assertEqual(r['paired_deltas_s'], [-2, 1])
        self.assertEqual(r['promotion'], 'BLOCKED_PILOT_ONLY')
        with self.assertRaises(ValueError): summarize(rows[:-1])
        with self.assertRaises(ValueError): summarize(rows + rows)
        rows[0]['status'] = 'FAIL'
        with self.assertRaises(ValueError): summarize(rows)

    def test_malformed_pair_receipts_fail_closed(self):
        rows = [
            {'pair': 0, 'position': 0, 'variant': 'baseline', 'status': 'PASS', 'install_total_s': 1},
            {'pair': 0, 'position': 0, 'variant': 'explicit', 'status': 'PASS', 'install_total_s': 1},
        ]
        with self.assertRaises(ValueError): summarize(rows)
        rows[1]['position'] = 1
        rows[1]['install_total_s'] = float('nan')
        with self.assertRaises(ValueError): summarize(rows)
