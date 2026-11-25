import math
import unittest

from audit.core import did_outcome, log_change, months, verdict, within_slope_perm


class CoreTests(unittest.TestCase):
    def test_months_wraps_year(self):
        self.assertEqual(months(2025, 11, 3), ["2025-11", "2025-12", "2026-01"])

    def test_did_removes_common_pretrend(self):
        s = {"a": 100, "b": 110, "c": 121, "d": 133.1}  # +10%/yr steady trend
        self.assertAlmostEqual(did_outcome(s, ["a"], ["b"], ["c"], ["d"]), 0.0, places=9)
        self.assertIsNone(log_change({"a": 0, "b": 5}, ["a"], ["b"]))

    def test_recovers_planted_within_group_slope(self):
        groups, x, y = {}, {}, {}
        for i in range(30):
            k = f"d{i}"
            groups[k] = "A" if i < 15 else "B"
            x[k] = float(i % 15)
            y[k] = 0.02 * x[k] + (5.0 if groups[k] == "B" else 0.0)  # group offset must be removed
        b, p = within_slope_perm(groups, x, y, n_perm=500)
        self.assertAlmostEqual(b, 0.02, places=9)
        self.assertLess(p, 0.05)

    def test_verdict_lines(self):
        self.assertEqual(verdict(0.01, 0.01, 0.005), "PASS")
        self.assertEqual(verdict(0.01, 0.01, -0.001), "WEAK")
        self.assertEqual(verdict(0.01, 0.2, 0.01), "WEAK")
        self.assertEqual(verdict(-0.01, 0.01, 0.01), "NULL_OR_NEGATIVE")


if __name__ == "__main__":
    unittest.main()
