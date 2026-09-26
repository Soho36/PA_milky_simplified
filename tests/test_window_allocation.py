from dataclasses import replace
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
from pa_milky.loader import Trade
from window_allocation_support import (allocation_mask, classify, evidence,
    make_decisions, paired_block_bootstrap, path_metrics, portfolio_metrics)


def trade(i, entry, pnl, duration=1, window="1-2"):
    return Trade(str(i), window, 1, i, i, entry, entry + timedelta(hours=duration),
                 min(pnl, 0), max(pnl, 0), pnl, 100)


class AllocationTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads((ROOT / "scripts/window_allocation.json").read_text())

    def test_future_and_open_outcomes_cannot_change_past_decision(self):
        cutoff = datetime(2022, 1, 1)
        tape = [trade(1, datetime(2021, 6, 1), 50),
                trade(2, cutoff - timedelta(hours=2), -500, duration=4),
                trade(3, cutoff + timedelta(days=1), 100)]
        def decision(t):
            return make_decisions(t, ["1-2"], [cutoff], datetime(2020, 1, 1), 24,
                                  self.spec["presets"]["balanced"], self.spec)
        original = decision(tape)
        changed = [tape[0], replace(tape[1], gross_pnl_usd=1e9), replace(tape[2], gross_pnl_usd=-1e9)]
        self.assertEqual(original, decision(changed))
        self.assertEqual(original[0]["trades"], 1)

    def test_exit_at_review_is_not_yet_training_observation(self):
        cutoff = datetime(2022, 1, 1)
        t = trade(1, cutoff - timedelta(hours=1), 100)
        self.assertEqual(evidence([t], cutoff, datetime(2020, 1, 1), 1.05)["trades"], 0)

    def test_entry_controls_allocation_and_positions_survive_review(self):
        a, b = datetime(2022, 1, 1), datetime(2022, 4, 1)
        decisions = [dict(review=a.isoformat(), window="1-2", state="Active"),
                     dict(review=b.isoformat(), window="1-2", state="Watch")]
        tape = [trade(1, a - timedelta(hours=1), 10), trade(2, b - timedelta(hours=1), 20, 3), trade(3, b, 30)]
        np.testing.assert_array_equal(allocation_mask(tape, decisions), [False, True, False])

    def test_shadow_history_allows_reentry(self):
        dates = [datetime(2022, 1, 1), datetime(2022, 4, 1)]
        tape = [trade(1, datetime(2021, 1, 1), -100), trade(2, datetime(2022, 2, 1), 300)]
        rows = make_decisions(tape, ["1-2"], dates, datetime(2020, 1, 1), None,
                              self.spec["presets"]["balanced"], self.spec, mode="positive")
        self.assertEqual([r["state"] for r in rows], ["Watch", "Active"])
        self.assertEqual(rows[1]["trades"], 2)

    def test_rolling_history_excludes_old_entry_even_if_exit_is_recent(self):
        lower, cutoff = datetime(2020, 1, 1), datetime(2022, 1, 1)
        tape = [trade(1, lower - timedelta(hours=1), 10000, 3), trade(2, lower, 10)]
        m = evidence(tape, cutoff, lower, 1.05)
        self.assertEqual(m["trades"], 1)
        self.assertAlmostEqual(m["net_usd"], 8.95)

    def test_rejection_requires_sample_and_negative_evidence(self):
        m = dict(trades=200, history_months=24, expectancy_usd=-1, profit_factor=.8, cluster_score=-2,
                 recovery_factor=-1, positive_block_fraction=0, negative_block_fraction=1,
                 net_without_best_block_usd=-100, recent_trades=100, recent_profit_factor=.8,
                 current_dd_fraction=1)
        args = (self.spec["presets"]["balanced"], self.spec["shared_gates"], 24)
        self.assertEqual(classify(m, *args)[0], "Rejected")
        self.assertEqual(classify({**m, "trades": 20}, *args)[0], "Watch")
        good = {**m, "expectancy_usd": 2, "profit_factor": 1.3, "cluster_score": 2,
                "recovery_factor": 2, "positive_block_fraction": .75, "negative_block_fraction": .25,
                "net_without_best_block_usd": 100, "recent_profit_factor": 1.2, "current_dd_fraction": .2}
        self.assertEqual(classify(good, *args)[0], "Active")

    def test_month_cluster_score_penalizes_a_single_lucky_month(self):
        lower, cutoff = datetime(2020, 1, 1), datetime(2022, 1, 1)
        tape = [trade(i, datetime(2020, 2, 1) + timedelta(hours=i), 100) for i in range(50)]
        tape += [trade(100+i, datetime(2020, 3, 1) + timedelta(hours=i), -10) for i in range(50)]
        m = evidence(tape, cutoff, lower, 0)
        naive_values = np.array([t.gross_pnl_usd for t in tape])
        naive_score = naive_values.mean() / (naive_values.std(ddof=1) / np.sqrt(len(tape)))
        self.assertGreater(naive_score, 5)
        self.assertLess(m["cluster_score"], 2)
        self.assertEqual(m["net_without_best_block_usd"], 0)

    def test_simultaneous_settlements_do_not_create_artificial_drawdown(self):
        day = datetime(2022, 1, 1)
        tape = [trade(1, day, -100), trade(2, day, 100, window="2-3")]
        m, daily = portfolio_metrics(tape, np.array([-100., 100.]), np.array([True, True]), [day.date()])
        self.assertEqual(m["max_closed_dd_usd"], 0)
        self.assertEqual(m["max_concurrent_contracts"], 2)
        self.assertEqual(m["contract_hours"], 2)
        self.assertEqual(daily[0], 0)

    def test_initial_losses_and_unrecovered_drawdown_count(self):
        days = [datetime(2022, 1, 1).date() + timedelta(days=i) for i in range(4)]
        m = path_metrics(np.array([-100., 30., 100., -50.]), days)
        self.assertEqual(m["max_eod_dd_usd"], 100)
        self.assertEqual(m["longest_dd_calendar_days"], 2)
        self.assertEqual(m["ending_dd_usd"], 50)

    def test_paired_bootstrap_preserves_identical_path_difference(self):
        m = paired_block_bootstrap([0.] * 24, 100, 3, np.random.default_rng(1))
        self.assertEqual(m["ci95_low_usd"], 0)
        self.assertEqual(m["ci95_high_usd"], 0)


if __name__ == "__main__":
    unittest.main()
