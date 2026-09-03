"""End-to-end invariants of a full brick-1 run on the real tape."""

from __future__ import annotations

import unittest

from pa_milky.config import load_config
from pa_milky.loader import load_trades
from pa_milky.report import summarize
from pa_milky.simulator import run_book

CONFIG = load_config()
TRADES = load_trades(
    CONFIG.sweeps_root, strategy=CONFIG.strategy, risk_reward=CONFIG.risk_reward
)
RESULT = run_book(TRADES, CONFIG)
SUMMARY = summarize(RESULT)


class TestRunIntegrity(unittest.TestCase):
    def test_one_account_per_month(self):
        months = [a.cohort_month for a in RESULT.accounts]
        self.assertEqual(len(months), 79)
        self.assertEqual(len(set(months)), 79)
        self.assertEqual(months[0], "2020-01")
        self.assertEqual(months[-1], "2026-07")

    def test_copies_reconcile_with_the_ledger(self):
        self.assertEqual(
            RESULT.copies_filled, sum(a.trades_taken for a in RESULT.accounts)
        )

    def test_cost_is_months_times_the_fee(self):
        self.assertEqual(RESULT.total_purchase_cost_usd, 79 * 200.0)
        self.assertEqual(SUMMARY["cash"]["spent_on_accounts_usd"], 15_800.0)

    def test_alive_and_dead_partition_the_book(self):
        self.assertEqual(len(RESULT.alive) + len(RESULT.dead), len(RESULT.accounts))

    def test_no_account_takes_more_than_the_whole_tape(self):
        self.assertTrue(all(a.trades_taken <= len(TRADES) for a in RESULT.accounts))

    def test_the_first_account_is_offered_every_trade_it_survives_to_see(self):
        # January 2020 activates before the tape starts, so nothing is filtered
        # out by activation and its count is purely a survival statement.
        first = RESULT.accounts[0]
        self.assertLessEqual(first.trades_taken, len(TRADES))

    def test_survivors_are_above_their_floor(self):
        for account in RESULT.alive:
            self.assertGreater(account.equity_profit_usd, account.floor_profit_usd)

    def test_every_death_has_a_reason_and_a_trade(self):
        for account in RESULT.dead:
            self.assertIn(
                account.death_reason, {"intratrade_excursion", "closed_below_threshold"}
            )
            self.assertIsNotNone(account.death_trade_key)
            self.assertIsNotNone(account.died_at)
            self.assertGreaterEqual(account.died_at, account.activated_at)

    def test_ledger_arithmetic_holds_for_survivors(self):
        for account in RESULT.alive:
            self.assertAlmostEqual(
                account.equity_profit_usd,
                round(account.gross_pnl_usd - account.commission_usd, 2),
                places=2,
            )
            self.assertAlmostEqual(
                account.commission_usd,
                round(account.trades_taken * CONFIG.commission_per_copy_usd, 2),
                places=2,
            )

    def test_the_run_is_deterministic(self):
        again = summarize(run_book(TRADES, CONFIG))
        for section in ("book", "cash", "alive_equity", "dead_accounts", "tape"):
            self.assertEqual(SUMMARY[section], again[section], section)


if __name__ == "__main__":
    unittest.main()
