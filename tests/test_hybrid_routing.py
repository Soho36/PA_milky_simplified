from datetime import datetime, timedelta
import unittest

from pa_milky.routing import RoutingPolicy, TradeRouter
from pa_milky.simulator import run_book
from .support import IDEAL, make_account, make_trade


class HybridRoutingTests(unittest.TestCase):
    def accounts(self, n):
        accounts = [make_account() for _ in range(n)]
        for i, a in enumerate(accounts, 1):
            a.account_id = i
        return accounts

    def cluster(self):
        return [make_trade(datetime(2020, 1, 2, i), datetime(2020, 1, 3), 10, row=i)
                for i in range(5)]

    def test_five_overlaps_match_proposed_allocation(self):
        for minimum, expected in ((1, [8, 8, 2, 1, 1]), (2, [8, 6, 2, 2, 2])):
            result = run_book(self.cluster(), IDEAL, fixed_accounts=20,
                              routing=RoutingPolicy(mode='hybrid', minimum_copies=minimum))
            self.assertEqual([len(f['accounts']) for f in result.routing_fills], expected)
            self.assertEqual([f['active_setups_before'] for f in result.routing_fills], list(range(5)))
            self.assertEqual(result.routing['minimum_copy_shortfall'], 0)

    def test_exit_releases_slots_and_instantaneous_signal_does_not_stay_active(self):
        d = datetime(2020, 1, 2)
        tape = [make_trade(d, d+timedelta(hours=1), 10),
                make_trade(d+timedelta(hours=1), d+timedelta(hours=1), 10, row=2),
                make_trade(d+timedelta(hours=1), d+timedelta(hours=2), 10, row=3)]
        result = run_book(tape, IDEAL, fixed_accounts=20, routing=RoutingPolicy(mode='hybrid'))
        self.assertEqual([len(f['accounts']) for f in result.routing_fills], [8, 8, 8])
        self.assertEqual([f['active_setups_before'] for f in result.routing_fills], [0, 0, 0])

    def test_depleted_inventory_attempts_minimum_instead_of_silently_pausing(self):
        d = datetime(2020, 1, 2)
        tape = [make_trade(d, d+timedelta(hours=1), 0, mae=-2000),
                make_trade(d+timedelta(hours=2), d+timedelta(hours=3), 10, row=2)]
        result = run_book(tape, IDEAL, fixed_accounts=1,
                          routing=RoutingPolicy(mode='hybrid', minimum_copies=2))
        self.assertEqual([f['requested'] for f in result.routing_fills], [2, 2])
        self.assertEqual([len(f['accounts']) for f in result.routing_fills], [1, 0])
        self.assertEqual(result.routing['minimum_copy_shortfall'], 3)
        self.assertEqual(result.routing['signals_with_no_target'], 0)
        self.assertEqual(len(result.accounts), 1)

    def test_headroom_selection_and_decision_do_not_use_future_trade_outcome(self):
        accounts = self.accounts(20)
        accounts[-1] = make_account(profit=2000)
        accounts[-1].account_id = 20
        selected = []
        for pnl, hours in ((100, 2), (-500, 200)):
            d = datetime(2020, 1, 3)
            router = TradeRouter([make_trade(d, d+timedelta(hours=hours), pnl)], RoutingPolicy(mode='hybrid'))
            router.enter(accounts)
            selected.append(router.fills[0]['accounts'])
        self.assertEqual(selected[0], selected[1])
        self.assertEqual(selected[0][0], 20)

    def test_no_death_tape_with_at_most_five_overlaps_preserves_floor(self):
        # Different durations and reuse cycles exercise reservations after exits.
        import random
        rng = random.Random(41)
        d = datetime(2020, 1, 2)
        ends, tape = [], []
        for i in range(150):
            at = d+timedelta(minutes=i*10)
            ends = [e for e in ends if e > at]
            if len(ends) == 5:
                continue
            end = at+timedelta(minutes=rng.randrange(1, 100))
            ends.append(end)
            tape.append(make_trade(at, end, 0, row=i))
        tape.sort(key=lambda t: (t.exit_at, t.entry_at, t.source_row))
        for minimum in (1, 2):
            result = run_book(tape, IDEAL, fixed_accounts=20,
                              routing=RoutingPolicy(mode='hybrid', minimum_copies=minimum, maximum_copies=12))
            self.assertEqual(len(result.dead), 0)
            self.assertTrue(all(minimum <= len(f['accounts']) <= 12 for f in result.routing_fills))

    def test_invalid_bounds_rejected(self):
        for lo, hi in ((0, 8), (2, 1), (1, True), (1.5, 8)):
            with self.assertRaises(ValueError):
                RoutingPolicy(mode='hybrid', minimum_copies=lo, maximum_copies=hi)
