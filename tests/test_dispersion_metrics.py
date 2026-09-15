from dataclasses import replace
from datetime import datetime, timedelta
from types import SimpleNamespace
import unittest

from pa_milky.dispersion_metrics import DispersionObserver, group_state
from pa_milky.simulator import run_book
from tests import test_evaluation, test_pipeline


def account(profit, floor=100):
    return SimpleNamespace(alive=True, equity_profit_usd=profit,
        headroom_usd=profit-floor, floor_profit_usd=floor, frozen_floor_profit_usd=100)


class TestDispersionMetrics(unittest.TestCase):
    def test_empty_and_singleton_are_not_evidence_of_synchronization(self):
        self.assertEqual(group_state([]), (0,)*5)
        self.assertEqual(group_state([account(500)]), (0,)*5)

    def test_known_population_spread(self):
        self.assertEqual(group_state([account(1000), account(2000)]), (1, 500, 1000, 2, 0))
        self.assertEqual(group_state([account(1000), account(1000)]), (1, 0, 0, 1, 1))

    def test_time_weights_and_frozen_group_exclude_unfrozen_account(self):
        start = datetime(2020, 1, 1)
        o = DispersionObserver(start, start+timedelta(days=2))
        a, b = account(1000), account(2000, -500)
        o(start, [a, b], 'decision', None)
        b.equity_profit_usd = 1000
        b.headroom_usd = 900
        b.floor_profit_usd = 100
        o(start+timedelta(days=1), [a, b], 'trade', None)
        o(start+timedelta(days=2), [a, b], 'horizon', None)
        r = o.summary()
        self.assertEqual(r['live_mean_balance_std_usd'], 250)
        self.assertEqual(r['live_identical_balance_fraction'], .5)
        self.assertEqual(r['frozen_multiple_account_days'], 1)
        self.assertEqual(r['frozen_identical_balance_fraction'], 1)

    def test_counts_emptying_once_and_separates_large_wipes(self):
        start = datetime(2020, 1, 1)
        o = DispersionObserver(start, start+timedelta(days=2))
        group = [account(1000) for _ in range(5)]
        o(start, group, 'decision', None)
        for a in group:
            a.alive = False
        o(start+timedelta(days=1), group, 'trade', None)
        o(start+timedelta(days=2), group, 'horizon', None)
        self.assertEqual(o.summary()['book_empty_transitions'], 1)
        self.assertEqual(o.summary()['book_wipes_from_at_least_five_live'], 1)

    def test_passive_observer_preserves_cash_payouts_and_accounts(self):
        f = test_evaluation.TestEvaluationSupply()
        f.setUp()
        acq = test_pipeline.TestPipeline().ledger().policy
        plain = run_book(f.tape, f.config, acquisition=acq)
        observer = DispersionObserver(plain.tape_first_entry, plain.tape_last_exit)
        observed = run_book(f.tape, f.config, acquisition=acq, observer=observer)
        self.assertEqual(replace(plain, acquisition=None), replace(observed, acquisition=None))
        self.assertEqual(plain.acquisition.summary(), observed.acquisition.summary())


if __name__ == '__main__':
    unittest.main()
