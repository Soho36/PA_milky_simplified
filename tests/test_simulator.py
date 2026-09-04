"""Book construction: one account per calendar month, copied to everything."""

from __future__ import annotations

import dataclasses
from datetime import datetime
import unittest

from pa_milky.simulator import months_in_span, run_book

from .support import BRICK1, make_trade as trade


class TestMonthsInSpan(unittest.TestCase):
    def test_single_month(self):
        self.assertEqual(
            months_in_span(datetime(2020, 3, 4), datetime(2020, 3, 29)), [(2020, 3)]
        )

    def test_crosses_a_year_boundary(self):
        self.assertEqual(
            months_in_span(datetime(2020, 11, 4), datetime(2021, 2, 1)),
            [(2020, 11), (2020, 12), (2021, 1), (2021, 2)],
        )

    def test_length_matches_the_real_tape(self):
        # 2020-01 through 2026-07 inclusive.
        self.assertEqual(
            len(months_in_span(datetime(2020, 1, 2), datetime(2026, 7, 13))), 79
        )


class TestBook(unittest.TestCase):
    def setUp(self):
        # Book construction only: no commission, and brick 1's empty
        # withdrawal policy, so nothing leaves an account here.
        self.config = dataclasses.replace(BRICK1, commission_usd_per_mnq_round_turn=0.0)

    def test_one_account_per_month_activated_at_month_start(self):
        trades = [
            trade(datetime(2020, 1, 10, 9), datetime(2020, 1, 10, 10), 10.0, row=1),
            trade(datetime(2020, 3, 10, 9), datetime(2020, 3, 10, 10), 10.0, row=2),
        ]
        result = run_book(trades, self.config)
        self.assertEqual([a.cohort_month for a in result.accounts], ["2020-01", "2020-02", "2020-03"])
        self.assertEqual(result.accounts[0].activated_at, datetime(2020, 1, 1))

    def test_an_account_never_takes_a_trade_older_than_itself(self):
        trades = [
            trade(datetime(2020, 1, 10, 9), datetime(2020, 1, 10, 10), 10.0, row=1),
            trade(datetime(2020, 2, 10, 9), datetime(2020, 2, 10, 10), 20.0, row=2),
        ]
        result = run_book(trades, self.config)
        january, february = result.accounts
        self.assertEqual(january.trades_taken, 2)
        self.assertEqual(january.equity_profit_usd, 30.0)
        self.assertEqual(february.trades_taken, 1)
        self.assertEqual(february.equity_profit_usd, 20.0)

    def test_a_trade_entered_before_activation_is_skipped_even_if_it_exits_after(self):
        trades = [trade(datetime(2020, 1, 31, 23), datetime(2020, 2, 1, 3), 10.0)]
        result = run_book(trades, self.config)
        self.assertEqual(result.accounts[0].trades_taken, 1)
        self.assertEqual(result.accounts[1].trades_taken, 0)

    def test_concurrency_is_unlimited(self):
        # Three overlapping entries; nothing is blocked by an open position.
        trades = [
            trade(datetime(2020, 1, 6, 9), datetime(2020, 1, 6, 12), 10.0, row=1),
            trade(datetime(2020, 1, 6, 10), datetime(2020, 1, 6, 13), 10.0, row=2),
            trade(datetime(2020, 1, 6, 11), datetime(2020, 1, 6, 14), 10.0, row=3),
        ]
        result = run_book(trades, self.config)
        self.assertEqual(result.accounts[0].trades_taken, 3)
        self.assertEqual(result.copies_filled, 3)

    def test_a_dead_account_stops_taking_copies(self):
        trades = [
            trade(datetime(2020, 1, 6, 9), datetime(2020, 1, 6, 10), -2_000.0, mae=-2_000.0, row=1),
            trade(datetime(2020, 1, 7, 9), datetime(2020, 1, 7, 10), 10.0, row=2),
        ]
        result = run_book(trades, self.config)
        account = result.accounts[0]
        self.assertFalse(account.alive)
        self.assertEqual(account.trades_taken, 1)
        self.assertEqual(result.copies_filled, 1)

    def test_a_dead_account_is_not_replaced(self):
        trades = [
            trade(datetime(2020, 1, 6, 9), datetime(2020, 1, 6, 10), -2_000.0, mae=-2_000.0, row=1),
            trade(datetime(2020, 2, 6, 9), datetime(2020, 2, 6, 10), 10.0, row=2),
        ]
        result = run_book(trades, self.config)
        self.assertEqual(len(result.accounts), 2)
        self.assertEqual(len(result.dead), 1)
        self.assertEqual(len(result.alive), 1)

    def test_cost_is_two_hundred_per_month(self):
        trades = [trade(datetime(2020, 1, 6, 9), datetime(2020, 3, 6, 10), 10.0)]
        result = run_book(trades, self.config)
        self.assertEqual(result.total_purchase_cost_usd, 600.0)

    def test_empty_tape_is_rejected(self):
        with self.assertRaises(ValueError):
            run_book([], self.config)


if __name__ == "__main__":
    unittest.main()
