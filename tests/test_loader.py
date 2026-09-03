"""The RR=1.00 tape must load whole and reconcile with the tester's own stats."""

from __future__ import annotations

from datetime import datetime
import unittest

from pa_milky.config import load_config
from pa_milky.loader import WINDOWS, load_trades

CONFIG = load_config()
TRADES = load_trades(
    CONFIG.sweeps_root, strategy=CONFIG.strategy, risk_reward=CONFIG.risk_reward
)


class TestTape(unittest.TestCase):
    def test_all_23_windows_present(self):
        self.assertEqual(len(WINDOWS), 23)
        self.assertEqual({t.window_id for t in TRADES}, set(WINDOWS))

    def test_expected_trade_count(self):
        # load_trades already reconciles each window against its _stats file;
        # this pins the total the parent study also reported.
        self.assertEqual(len(TRADES), CONFIG.expected_trades)

    def test_trade_keys_are_unique(self):
        self.assertEqual(len({t.trade_key for t in TRADES}), len(TRADES))

    def test_sorted_by_settlement_time(self):
        exits = [t.exit_at for t in TRADES]
        self.assertEqual(exits, sorted(exits))

    def test_span(self):
        self.assertEqual(min(t.entry_at for t in TRADES), datetime(2020, 1, 2, 7, 50, 40))
        self.assertEqual(max(t.exit_at for t in TRADES), datetime(2026, 7, 13, 21, 30, 40))

    def test_no_trade_exits_before_it_enters(self):
        self.assertTrue(all(t.exit_at >= t.entry_at for t in TRADES))

    def test_excursions_bracket_the_result(self):
        # mae <= pnl <= mfe holds everywhere, and MFE is never negative.
        for t in TRADES:
            self.assertGreaterEqual(t.mfe_usd, 0.0, t.trade_key)
            self.assertLessEqual(t.mae_usd, t.gross_pnl_usd, t.trade_key)
            self.assertLessEqual(t.gross_pnl_usd, t.mfe_usd, t.trade_key)

    def test_some_trades_never_go_underwater(self):
        # MAE is the worst point reached, not necessarily a loss: 555 trades
        # here have a positive MAE. Account.apply clamps those to zero rather
        # than crediting an account with an excursion it never had.
        never_underwater = [t for t in TRADES if t.mae_usd > 0.0]
        self.assertEqual(len(never_underwater), 555)

    def test_a_missing_strategy_is_an_error(self):
        with self.assertRaises(FileNotFoundError):
            load_trades(CONFIG.sweeps_root, strategy="NOPE", risk_reward="1.00")


if __name__ == "__main__":
    unittest.main()
