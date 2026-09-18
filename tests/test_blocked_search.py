"""Selection and refinement must preserve the declared search contract."""
import importlib.util
from pathlib import Path
import sys
import unittest


SCRIPTS = Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0, str(SCRIPTS))
try:
    spec = importlib.util.spec_from_file_location('blocked_search_under_test', SCRIPTS/'optimize_blocked_copying.py')
    search = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(search)
finally:
    sys.path.pop(0)


def row(seed, h, ongoing, total, *, acq='monthly_one', spend=1000):
    return {'job':[2020,1000,200,acq,seed,'minimum','daily',h,0],
            'acquisition':acq,'initial_accounts':seed,'withdrawal':'minimum','cadence':'daily',
            'headroom':h,'ongoing':ongoing,'total':total,'spend':spend}


class BlockedSearchTests(unittest.TestCase):
    def test_cash_objectives_can_choose_different_policies(self):
        early = row(1,1000,10000,11000)
        closing = row(5,2000,9000,15000)
        self.assertIs(search.best([early,closing],'ongoing'),early)
        self.assertIs(search.best([early,closing],'total'),closing)

    def test_ties_are_deterministic_and_use_other_cash_objective_before_spend(self):
        weak = row(1,1000,10000,11000,spend=1000)
        good = row(5,2000,10000,15000,spend=2000)
        self.assertIs(search.best([weak,good],'ongoing'),good)
        same_cash = row(2,2000,10000,15000,spend=1000)
        self.assertIs(search.best([good,same_cash],'ongoing'),same_cash)
        self.assertEqual(search.best([same_cash,good],'ongoing'),search.best([good,same_cash],'ongoing'))

    def test_refinement_keeps_both_objectives_seeds_and_does_not_cross_budget_or_bounds(self):
        search.SPEC = {'refinement_radius':500,'refinement_step':100,'coarse_headrooms':[0,15000]}
        rows = [row(1,0,10000,11000),row(5,15000,9000,15000),
                row(3,3000,100,100,acq='weekly_one')]
        jobs = search.refined_jobs(rows)
        self.assertTrue(all(j[:3] == (2020,1000,200) and 0 <= j[7] <= 15000 for j in jobs))
        self.assertEqual({j[4] for j in jobs if j[3]=='monthly_one'},{1,5})
        self.assertEqual({j[4] for j in jobs if j[3]=='weekly_one'},{3})
        self.assertIn((2020,1000,200,'monthly_one',5,'minimum','daily',14900,0),jobs)


if __name__ == '__main__':
    unittest.main()
