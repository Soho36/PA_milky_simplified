from dataclasses import replace
from datetime import datetime
import unittest

from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.routing import RoutingPolicy
from pa_milky.simulator import run_book
from .support import IDEAL, make_trade


class FixedInventoryTests(unittest.TestCase):
    def test_initial_inventory_does_not_grow_or_replace_deaths(self):
        tape = [make_trade(datetime(2020, 1, 2), datetime(2020, 1, 3), 0, mae=-2000),
                make_trade(datetime(2020, 3, 2), datetime(2020, 3, 3), 100, row=2)]
        for route in (None, RoutingPolicy(mode='blocked')):
            result = run_book(tape, IDEAL, fixed_accounts=20, routing=route)
            self.assertEqual(len(result.accounts), 20)
            self.assertEqual(result.alive_at_horizon, 0)
            self.assertEqual(result.copies_filled, 20)
            self.assertEqual(result.total_purchase_cost_usd, 4000)
            self.assertEqual(len({a.account_id for a in result.accounts}), 20)
            self.assertEqual({a.activated_at for a in result.accounts}, {datetime(2020, 1, 1)})
            self.assertIsNone(result.acquisition)

    def test_fixed_demand_reports_shortfall_without_rescue_or_scaling_down(self):
        tape = [make_trade(datetime(2020, 1, 2), datetime(2020, 1, 3), 0, mae=-2000),
                make_trade(datetime(2020, 1, 4), datetime(2020, 1, 5), 100, row=2),
                make_trade(datetime(2020, 3, 2), datetime(2020, 3, 3), 100, row=3)]
        result = run_book(tape, IDEAL, fixed_accounts=2, routing=RoutingPolicy(copies=2),
                          routing_demand=[1, 2, 0])
        self.assertEqual([f['requested'] for f in result.routing_fills], [1, 2, 0])
        self.assertEqual([len(f['accounts']) for f in result.routing_fills], [1, 1, 0])
        self.assertEqual([f['purchased'] for f in result.routing_fills], [0, 0, 0])
        self.assertEqual(len(result.accounts), 2)

    def test_no_overlap_and_same_timestamp_exit_releases_capacity(self):
        tape = [make_trade(datetime(2020, 1, 2, 1), datetime(2020, 1, 2, 2), 10),
                make_trade(datetime(2020, 1, 2, 1, 30), datetime(2020, 1, 2, 3), 10, row=2),
                make_trade(datetime(2020, 1, 2, 3), datetime(2020, 1, 2, 3), 10, row=3)]
        result = run_book(tape, IDEAL, fixed_accounts=2, routing=RoutingPolicy(copies=2))
        self.assertEqual([len(f['accounts']) for f in result.routing_fills], [2, 0, 2])

    def test_rejects_ambiguous_purchase_and_demand_settings(self):
        tape = [make_trade(datetime(2020, 1, 2), datetime(2020, 1, 3), 10)]
        for count in (True, 0, -1, 1.5):
            with self.assertRaises(ValueError):
                run_book(tape, IDEAL, fixed_accounts=count)
        with self.assertRaises(ValueError):
            run_book(tape, IDEAL, fixed_accounts=2, acquisition=AcquisitionPolicy('monthly_one', 1000))
        with self.assertRaises(ValueError):
            run_book(tape, replace(IDEAL, max_accounts=2), fixed_accounts=2)
        for demand in ([], [True], [-1], [1.5]):
            with self.assertRaises(ValueError):
                run_book(tape, IDEAL, fixed_accounts=2, routing=RoutingPolicy(), routing_demand=demand)
        with self.assertRaises(ValueError):
            run_book(tape, IDEAL, fixed_accounts=2, routing_demand=[1])
