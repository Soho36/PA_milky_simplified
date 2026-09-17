from dataclasses import replace
from datetime import datetime
import unittest

from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.routing import RoutingPolicy, TradeRouter
from pa_milky.simulator import run_book
from .support import IDEAL, make_account, make_trade


class GrowthRoutingTests(unittest.TestCase):
    def test_replication_tracks_live_accounts_including_deaths(self):
        tape = [make_trade(datetime(2020, 1, 2), datetime(2020, 1, 3), 0)]
        for live, expected in ((0, 0), (4, 0), (5, 1), (9, 1), (10, 2), (14, 2),
                               (15, 3), (19, 3), (20, 4)):
            accounts = [make_account() for _ in range(20)]
            for i, account in enumerate(accounts, 1):
                account.account_id = i
                account.alive = i <= live
            router = TradeRouter(tape, RoutingPolicy(mode='adaptive'))
            router.enter(accounts)
            self.assertEqual(router.fills[0]['requested'], expected)
            self.assertEqual(len(router.fills[0]['accounts']), expected)

    def test_busy_accounts_count_toward_capacity_but_cannot_receive_another_trade(self):
        accounts = [make_account() for _ in range(10)]
        for i, a in enumerate(accounts, 1):
            a.account_id = i
        tape = [make_trade(datetime(2020, 1, 2, i), datetime(2020, 1, 3), 0, row=i)
                for i in range(6)]
        router = TradeRouter(tape, RoutingPolicy(mode='adaptive'))
        for _ in tape:
            router.enter(accounts)
        self.assertEqual([f['requested'] for f in router.fills], [2] * 6)
        self.assertEqual(router.summary()['copies_missed_busy'], 2)

    def test_seed_is_paid_and_replaces_first_month_purchase(self):
        tape = [make_trade(datetime(2020, 1, 2), datetime(2020, 1, 3), 10),
                make_trade(datetime(2020, 2, 2), datetime(2020, 2, 3), 10, row=2)]
        result = run_book(tape, IDEAL, acquisition=AcquisitionPolicy('monthly_plus_replacements', 5000),
                          initial_accounts=5, routing=RoutingPolicy(mode='adaptive'))
        self.assertEqual(len(result.accounts), 6)
        self.assertEqual(result.total_purchase_cost_usd, 1200)
        self.assertEqual([f['alive'] for f in result.routing_fills], [5, 6])
        self.assertEqual(result.acquisition.summary()['cash_identity_residual_usd'], 0)

    def test_growth_does_not_get_free_replacements_when_cash_is_empty(self):
        tape = [make_trade(datetime(2020, 1, 2), datetime(2020, 1, 2, 1), 0, mae=-2000),
                make_trade(datetime(2020, 1, 3), datetime(2020, 1, 3, 1), 10, row=2)]
        result = run_book(tape, IDEAL, acquisition=AcquisitionPolicy('monthly_plus_replacements', 1000),
                          initial_accounts=5, routing=RoutingPolicy(mode='adaptive'))
        self.assertEqual(len(result.accounts), 5)
        self.assertEqual([f['requested'] for f in result.routing_fills], [1, 0])
        self.assertEqual(result.routing['signals_with_no_target'], 1)
        self.assertEqual(result.acquisition.cash_usd, 0)

    def test_funded_death_replacement_is_separate_from_monthly_growth(self):
        tape = [make_trade(datetime(2020, 1, 2), datetime(2020, 1, 2, 1), 0, mae=-2000),
                make_trade(datetime(2020, 1, 3), datetime(2020, 1, 3, 1), 10, row=2),
                make_trade(datetime(2020, 2, 2), datetime(2020, 2, 2, 1), 10, row=3)]
        result = run_book(tape, IDEAL, acquisition=AcquisitionPolicy('monthly_plus_replacements', 5000),
                          initial_accounts=5, routing=RoutingPolicy(mode='adaptive'))
        self.assertEqual([f['alive'] for f in result.routing_fills], [5, 5, 6])
        self.assertEqual(len(result.accounts), 7)
        self.assertEqual(result.total_purchase_cost_usd, 1400)

    def test_seed_cannot_bypass_budget_or_cap(self):
        tape = [make_trade(datetime(2020, 1, 2), datetime(2020, 1, 3), 0)]
        for policy in (AcquisitionPolicy('monthly_plus_replacements', 999),
                       AcquisitionPolicy('monthly_plus_replacements', 5000, max_live_accounts=4)):
            with self.assertRaises(ValueError):
                run_book(tape, IDEAL, acquisition=policy, initial_accounts=5)


if __name__ == '__main__':
    unittest.main()
