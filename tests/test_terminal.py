"""Closing the book: the two hold-then-withdraw benchmarks.

"Hold everything and withdraw at the end" is the study's original ideal, and it
only means something once the closing withdrawal is explicit. Two readings, and
the gap between them is the whole point:

- ``liquidate_profit`` -- every dollar of profit becomes cash. A counterfactual
  about what the equity was worth.
- ``firm_permitted`` -- one request through the rulebook. What could actually
  have been taken.
"""

from __future__ import annotations

import dataclasses
import unittest

from pa_milky.config import CONFIG_ROOT, load_config
from pa_milky.simulator import run_book

from .support import FULL, IDEAL, RESULT1, TRADES

HOLD_IDEAL = load_config(CONFIG_ROOT / "scenarios" / "hold_then_liquidate.json")
HOLD_FIRM = load_config(CONFIG_ROOT / "scenarios" / "hold_then_firm_permitted.json")

RESULT_HOLD_IDEAL = run_book(TRADES, HOLD_IDEAL)
RESULT_HOLD_FIRM = run_book(TRADES, HOLD_FIRM)


class TestTheHeldBookIsUnchanged(unittest.TestCase):
    """A closing withdrawal must not disturb the trading that preceded it."""

    def test_both_benchmarks_hold_the_same_book_as_brick_one(self):
        for result in (RESULT_HOLD_IDEAL, RESULT_HOLD_FIRM):
            self.assertEqual(result.alive_at_horizon, len(RESULT1.alive))
            self.assertEqual(result.copies_filled, RESULT1.copies_filled)
            self.assertEqual(result.equity_at_horizon_usd, 488_099.10)

    def test_nothing_is_withdrawn_before_the_horizon(self):
        for result in (RESULT_HOLD_IDEAL, RESULT_HOLD_FIRM):
            self.assertEqual(
                [e for e in result.payouts if e not in result.terminal_payouts], []
            )

    def test_the_terminal_payout_lands_on_the_last_exit(self):
        for result in (RESULT_HOLD_IDEAL, RESULT_HOLD_FIRM):
            for event in result.terminal_payouts:
                self.assertEqual(event.at, result.tape_last_exit)


class TestIdealizedLiquidation(unittest.TestCase):
    def test_it_recovers_exactly_brick_ones_paper_profit(self):
        # An independent cross-check on the sealed baseline: the idealized
        # closing withdrawal must equal the equity brick 1 reported holding.
        self.assertEqual(RESULT_HOLD_IDEAL.total_withdrawn_usd, 488_099.10)
        self.assertEqual(len(RESULT_HOLD_IDEAL.terminal_payouts), 22)
        self.assertEqual(RESULT_HOLD_IDEAL.pocket_usd, 472_299.10)

    def test_every_surviving_account_is_emptied_to_its_starting_balance(self):
        for account in RESULT_HOLD_IDEAL.accounts:
            if account.alive:
                self.assertEqual(account.balance_usd, 25_000.0)

    def test_an_emptied_account_is_not_recorded_as_blown(self):
        # It was alive at the horizon and we closed it; that is not a death.
        self.assertEqual(len(RESULT_HOLD_IDEAL.dead), len(RESULT1.dead))


class TestFirmPermittedLiquidation(unittest.TestCase):
    def test_one_request_each_and_the_maximum_binds_on_all_of_them(self):
        self.assertEqual(len(RESULT_HOLD_FIRM.terminal_payouts), 20)
        for event in RESULT_HOLD_FIRM.terminal_payouts:
            self.assertEqual(event.payout_number, 1)
            self.assertEqual(event.gross_usd, 1_500.0)
            self.assertEqual(event.binding_cap, "maximum_payout")

    def test_it_reaches_only_a_fraction_of_the_equity(self):
        self.assertEqual(RESULT_HOLD_FIRM.total_withdrawn_usd, 30_000.0)
        extracted = (
            RESULT_HOLD_FIRM.total_withdrawn_usd / RESULT_HOLD_FIRM.equity_at_horizon_usd
        )
        self.assertLess(extracted, 0.07)

    def test_holding_is_the_worst_arm_in_the_study(self):
        # Worse than taking $500 a month, and far worse than doing so with a
        # cushion. The paper value of a held book is not reachable.
        self.assertLess(RESULT_HOLD_FIRM.pocket_usd, run_book(TRADES, FULL).pocket_usd)
        self.assertLess(RESULT_HOLD_FIRM.pocket_usd, 20_000.0)


class TestPayoutHistoryUnlocksLiquidation(unittest.TestCase):
    """Why the two benchmarks differ so much.

    The safety net expires after payout three and the maximum after payout
    five. A held book's closing request is payout number one, so both bind. A
    book that has been paying monthly has already spent those, and its closing
    request is capped only by the trailing threshold.
    """

    @staticmethod
    def _arm(cushion, terminal):
        return dataclasses.replace(
            FULL,
            policy=dataclasses.replace(
                FULL.policy,
                min_retained_balance_usd=cushion,
                terminal_withdrawal=terminal,
            ),
        )

    def test_a_paying_book_liquidates_far_better_than_a_held_one(self):
        paying = run_book(TRADES, self._arm(30_000.0, "firm_permitted"))
        held_fraction = (
            RESULT_HOLD_FIRM.total_withdrawn_usd / RESULT_HOLD_FIRM.equity_at_horizon_usd
        )
        paying_fraction = (
            sum(e.gross_usd for e in paying.terminal_payouts) / paying.equity_at_horizon_usd
        )
        self.assertLess(held_fraction, 0.07)
        self.assertGreater(paying_fraction, 0.90)

    def test_its_closing_requests_are_past_the_capped_regime(self):
        paying = run_book(TRADES, self._arm(30_000.0, "firm_permitted"))
        for event in paying.terminal_payouts:
            self.assertGreater(event.payout_number, 5)
            self.assertNotEqual(event.binding_cap, "maximum_payout")

    def test_the_rules_barely_bind_once_the_history_exists(self):
        ideal = run_book(TRADES, self._arm(30_000.0, "liquidate_profit"))
        permitted = run_book(TRADES, self._arm(30_000.0, "firm_permitted"))
        self.assertGreater(permitted.pocket_usd, 0.95 * ideal.pocket_usd)


class TestTerminalIsOptIn(unittest.TestCase):
    def test_the_ideal_world_scenario_still_withdraws_nothing(self):
        self.assertFalse(IDEAL.policy.liquidates)
        self.assertEqual(RESULT1.total_withdrawn_usd, 0.0)
        self.assertEqual(RESULT1.terminal_payouts, [])

    def test_an_unknown_terminal_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            dataclasses.replace(
                FULL.policy, terminal_withdrawal="take_the_starting_balance_too"
            )


if __name__ == "__main__":
    unittest.main()
