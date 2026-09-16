from dataclasses import replace
from datetime import datetime
import unittest

from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.routing import RoutingPolicy, TradeRouter, capacity_audit
from pa_milky.routing_study import ReplayPlan, reference_run, replay_run, required_topups, fixed_pool_run
from pa_milky.simulator import run_book
from .support import IDEAL, TRADES, make_trade, make_account


class RoutingTests(unittest.TestCase):
    def test_current_tape_capacity(self):
        self.assertEqual(capacity_audit(TRADES)["peak_positions"], 5)

    def test_five_seats_per_copy_cover_actual_tape_without_account_deaths(self):
        for copies in (1, 2):
            plan = ReplayPlan([copies] * len(TRADES), {datetime(2020, 1, 1): 5 * copies})
            # Eliminate account death solely to test the interval-capacity claim.
            config = replace(IDEAL, trailing_drawdown_usd=1e12)
            result = run_book(TRADES, config, routing=RoutingPolicy(), replay=plan)
            self.assertEqual(len(result.accounts), 5 * copies)
            self.assertEqual(result.copies_filled, len(TRADES) * copies)
            self.assertFalse(any(e['emergency'] for e in plan.purchase_events))
            self.assertEqual(result.routing['peak_occupied_accounts'], 5 * copies)

    def test_four_initial_seats_need_a_fifth_on_this_tape(self):
        plan = ReplayPlan([1] * len(TRADES), {datetime(2020, 1, 1): 4})
        result = run_book(TRADES, replace(IDEAL, trailing_drawdown_usd=1e12),
                          routing=RoutingPolicy(), replay=plan)
        self.assertEqual(len(result.accounts), 5)
        self.assertEqual(sum(e['count'] for e in plan.purchase_events if e['emergency']), 1)

    def test_blocked_mode_offers_every_live_account_one_slot(self):
        tape = [make_trade(datetime(2020, 1, 2, 10), datetime(2020, 1, 2, 11), 100, row=2),
                make_trade(datetime(2020, 1, 2, 9), datetime(2020, 1, 2, 12), -50)]
        result = run_book(tape, IDEAL, acquisition=AcquisitionPolicy('monthly_two', 1000),
                          routing=RoutingPolicy(mode='blocked'))
        self.assertEqual(result.copies_filled, 2)
        self.assertEqual(result.routing['copies_missed_busy'], 2)
        self.assertEqual([a.gross_pnl_usd for a in result.accounts], [-50, -50])

    def test_shared_timestamp_frees_slot(self):
        tape = [make_trade(datetime(2020, 1, 2, 9), datetime(2020, 1, 2, 10), 10),
                make_trade(datetime(2020, 1, 2, 10), datetime(2020, 1, 2, 11), 20, row=2)]
        result = run_book(tape, IDEAL, routing=RoutingPolicy())
        self.assertEqual(result.copies_filled, 2)
        self.assertEqual(result.routing["copies_missed_busy"], 0)
        self.assertEqual(result.accounts[0].trades_taken, 2)

    def test_blocking_chooses_entry_order_not_exit_order(self):
        tape = [make_trade(datetime(2020, 1, 2, 10), datetime(2020, 1, 2, 11), 100, row=2),
                make_trade(datetime(2020, 1, 2, 9), datetime(2020, 1, 2, 12), -50)]
        result = run_book(tape, IDEAL, routing=RoutingPolicy())
        self.assertEqual(result.copies_filled, 1)
        self.assertEqual(result.accounts[0].gross_pnl_usd, -50)
        self.assertEqual(result.routing["copies_missed_busy"], 1)

    def test_entry_at_purchase_boundary_sees_new_account(self):
        tape = [make_trade(datetime(2020, 1, 1), datetime(2020, 1, 1, 1), 10)]
        result = run_book(tape, IDEAL, routing=RoutingPolicy())
        self.assertEqual(result.copies_filled, 1)

    def test_does_not_see_later_accounts(self):
        tape = [make_trade(datetime(2020, 1, 31, 9), datetime(2020, 2, 2), 10)]
        result = run_book(tape, IDEAL, routing=RoutingPolicy(copies=2))
        self.assertEqual(result.copies_filled, 1)
        self.assertEqual(result.routing["copies_missed_inventory"], 1)
        self.assertEqual(result.accounts[1].trades_taken, 0)

    def test_known_headroom_and_busy_filter(self):
        accounts = [make_account(), make_account(100)]
        accounts[1].account_id = 2
        tape = [make_trade(datetime(2020, 1, 3), datetime(2020, 1, 4), 100),
                make_trade(datetime(2020, 1, 3, 1), datetime(2020, 1, 5), 200, row=2)]
        # Set known headroom; future excursions must not influence the first pick.
        accounts[1].equity_profit_usd = 200
        router = TradeRouter(tape, RoutingPolicy())
        router.enter(accounts)
        router.enter(accounts)
        self.assertEqual([f["accounts"] for f in router.fills], [[2], [1]])

    def test_capacity_replay_fills_all_copies_and_charges_seats(self):
        tape = [make_trade(datetime(2020, 1, 2), datetime(2020, 1, 3), 100),
                make_trade(datetime(2020, 1, 2, 1), datetime(2020, 1, 4), 200, row=2)]
        ref, demand, peak = reference_run(tape, IDEAL, AcquisitionPolicy('monthly_one', 200))
        arm, plan = replay_run(tape, ref, demand, allocation='round_robin', capacity=2)
        self.assertEqual(arm.copies_filled, ref.copies_filled)
        self.assertEqual(arm.total_purchase_cost_usd, 400)
        self.assertEqual(sum(a.gross_pnl_usd for a in arm.accounts), 300)
        self.assertEqual(plan.peak_live, 2)
        self.assertEqual(required_topups(arm, plan, ref)['additional_external_funding_usd'], 200)

    def test_emergency_replacement_is_counted_when_death_exhausts_pool(self):
        # Synthetic demand continues after reference death to exercise a paid
        # replacement independently of the reference-demand extraction.
        tape = [make_trade(datetime(2020, 1, 2), datetime(2020, 1, 2, 1), 0, mae=-2000),
                make_trade(datetime(2020, 1, 3), datetime(2020, 1, 3, 1), 10, row=2)]
        ref, _, _ = reference_run(tape, IDEAL, AcquisitionPolicy('monthly_one', 200))
        arm, plan = replay_run(tape, ref, [1, 1], allocation='max_headroom', capacity=1,
                               procurement='five_per_purchase')
        self.assertEqual(arm.copies_filled, 2)
        self.assertEqual(sum(e['count'] for e in plan.purchase_events if e['emergency']), 1)
        self.assertEqual(arm.total_purchase_cost_usd, 400)

    def test_zero_duration_enters_then_exits(self):
        moment = datetime(2020, 1, 2)
        tape = [make_trade(moment, moment, 10)]
        result = run_book(tape, IDEAL, routing=RoutingPolicy())
        self.assertEqual(result.copies_filled, 1)

    def test_negative_duration_rejected(self):
        moment = datetime(2020, 1, 2)
        with self.assertRaises(ValueError):
            capacity_audit([make_trade(moment, datetime(2020, 1, 1), 0)])

    def test_reuse_does_not_multiply_reference_purchases(self):
        tape = [make_trade(datetime(2020, 1, 2), datetime(2020, 1, 2, 1), 10),
                make_trade(datetime(2020, 2, 2), datetime(2020, 2, 2, 1), 10, row=2)]
        ref, demand, _ = reference_run(tape, IDEAL, AcquisitionPolicy('monthly_one', 1000))
        result, plan = replay_run(tape, ref, demand, allocation='max_headroom', capacity=5)
        self.assertEqual(demand, [1, 2])
        self.assertEqual(len(result.accounts), 2)
        self.assertEqual([p['count'] for p in plan.purchase_events], [1, 1])
        self.assertEqual(result.routing_fills[1]['free_before_purchase'], 1)
        self.assertEqual(result.routing_fills[1]['purchased'], 1)

    def test_five_usable_seats_and_six_overlaps_buy_only_one(self):
        tape = [make_trade(datetime(2020, 1, 2), datetime(2020, 1, 2, 1), 10, row=i)
                for i in range(6)]
        result, plan = fixed_pool_run(tape, IDEAL, copies=1, allocation='max_headroom', initial_seats=5)
        self.assertEqual(len(result.accounts), 6)
        self.assertEqual([p['count'] for p in plan.purchase_events], [5, 1])
        self.assertEqual(result.copies_filled, 6)

    def test_pool_reuses_five_seats_across_months(self):
        tape = [make_trade(datetime(2020, month, 2), datetime(2020, month, 2, 1), 10, row=month)
                for month in range(1, 7)]
        result, plan = fixed_pool_run(tape, IDEAL, copies=1, allocation='max_headroom', initial_seats=5)
        self.assertEqual(len(result.accounts), 5)
        self.assertEqual(len(plan.purchase_events), 1)

    def test_cap_blocks_instead_of_silently_buying_twenty_first_seat(self):
        tape = [make_trade(datetime(2020, 1, 2), datetime(2020, 1, 2, 1), 10, row=i)
                for i in range(21)]
        result, plan = fixed_pool_run(tape, IDEAL, copies=1, allocation='max_headroom', initial_seats=20)
        self.assertEqual(len(result.accounts), 20)
        self.assertEqual(result.copies_filled, 20)
        self.assertEqual(result.routing['copies_missed_busy'], 1)


if __name__ == '__main__':
    unittest.main()
