"""Search coverage and scoring must not favor either account product."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from study_legacy_reserve_comparison import refinement_jobs, summaries, matched_deltas


def row(prod, h, ongoing, total):
    return dict(product=prod, initial_cash=1000, monthly_funding=200,
                acquisition='monthly_one', withdrawal='minimum', cadence='daily',
                headroom=h, reserve=(25100 if prod == 'legacy_25k' else 50100)+h,
                ongoing=ongoing, total=total)


class ReserveComparisonTests(unittest.TestCase):
    def test_refinement_uses_both_objectives_and_products_for_each_pair(self):
        rows = [row('legacy_25k', 1000, 100, 110), row('legacy_25k', 2000, 90, 150),
                row('legacy_50k', 3000, 150, 160), row('legacy_50k', 4000, 100, 200)]
        spec = dict(products=['legacy_25k', 'legacy_50k'], refinement_radius=100, refinement_step=100)
        jobs = refinement_jobs(rows, spec)
        a = {j[6] for j in jobs if j[0] == 'legacy_25k'}
        b = {j[6] for j in jobs if j[0] == 'legacy_50k'}
        self.assertEqual(a, b)
        self.assertEqual(a, {900, 1000, 1100, 1900, 2000, 2100, 2900, 3000, 3100, 3900, 4000, 4100})

    def test_ties_and_disconnected_near_best_are_not_hidden(self):
        rows = [row('legacy_25k', 0, 100, 200), row('legacy_25k', 100, 50, 80),
                row('legacy_25k', 200, 100, 210)]
        result = next(r for r in summaries(rows) if r['objective'] == 'ongoing')
        self.assertEqual(result['reserve'], 25300)  # secondary score breaks display tie
        self.assertEqual(result['tied_best_reserves'], [25100, 25300])
        self.assertEqual(result['within_one_percent_reserves'], [25100, 25300])
        self.assertTrue(result['boundary_best'])

    def test_insolvency_plateau_has_no_positive_near_best_band(self):
        rows = [row('legacy_50k', h, -1000, -1000) for h in (0, 1000, 2000)]
        for result in summaries(rows):
            self.assertEqual(result['within_one_percent_reserves'], [])
            self.assertEqual(len(result['tied_best_reserves']), 3)
            self.assertEqual(result['reserve'], 50100)

    def test_missing_product_pair_fails_and_deltas_use_headroom(self):
        a, b = row('legacy_25k', 6800, 100, 200), row('legacy_50k', 6800, 150, 180)
        with self.assertRaises(AssertionError):
            matched_deltas([a])
        delta = matched_deltas([a, b])[0]
        self.assertEqual(delta['ongoing_delta_50k_minus_25k'], 50)
        self.assertEqual(delta['total_delta_50k_minus_25k'], -20)
        self.assertEqual((delta['reserve_25k'], delta['reserve_50k']), (31900, 56900))
