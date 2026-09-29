from datetime import date, timedelta
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from study_window_allocation_attribution import drawdown_episodes, interval_attribution, restored_metrics, restoration_dd_only


class AttributionTests(unittest.TestCase):
    def days(self, count):
        return [date(2022, 1, 1) + timedelta(days=i) for i in range(count)]

    def test_initial_drawdown_and_recovery_do_not_omit_first_loss(self):
        daily = np.array([-100., 30., 80., -50.])
        episodes = drawdown_episodes(daily, self.days(4))
        self.assertEqual(episodes[0]["depth_usd"], 100)
        self.assertEqual(episodes[0]["peak_date"], "2021-12-31")
        self.assertEqual(episodes[0]["recovery_date"], "2022-01-03")
        self.assertFalse(episodes[1]["recovered"])

    def test_equal_high_plateau_uses_last_date_without_double_counting_peak(self):
        daily = np.array([100., 0., -40., 40., -20.])
        episodes = drawdown_episodes(daily, self.days(5))
        self.assertEqual(episodes[0]["peak_date"], "2022-01-02")
        self.assertEqual(episodes[0]["depth_usd"], 40)
        self.assertEqual(episodes[1]["depth_usd"], 20)

    def test_fixed_interval_decomposition_when_maxima_have_different_dates(self):
        all_daily = np.array([100., -100., 200., -50.])
        filtered = np.array([100., -20., 100., -80.])
        episode = drawdown_episodes(all_daily, self.days(4))[0]
        a = interval_attribution(all_daily, filtered, episode)
        self.assertEqual(a["all_decline_usd"], 100)
        self.assertEqual(a["filtered_decline_usd"], 20)
        self.assertEqual(a["excluded_loss_avoided_usd"], 80)
        # Max-DD advantage is only 20, despite avoiding 80 on the base interval.
        self.assertEqual(100 - drawdown_episodes(filtered, self.days(4))[0]["depth_usd"], 20)

    def test_restoration_recomputes_changed_peak_and_trough(self):
        filtered = np.array([100., -20., 100., -80.])
        excluded = {"A": np.array([0., -80., 100., 30.])}
        row = restored_metrics(filtered, excluded, ["A"], self.days(4), 100, 80)
        self.assertEqual(row["max_eod_dd_usd"], 100)
        self.assertEqual(row["dd_increase_vs_filter_usd"], 20)
        self.assertEqual(row["dd_advantage_remaining_usd"], 0)

    def test_pair_effect_is_not_sum_of_individual_effects(self):
        filtered = np.array([100., -10., 100., -10.])
        paths = {"A": np.array([0., -90., 90., 0.]), "B": np.array([0., 0., 0., -90.])}
        args = (self.days(4), 100, 10)
        a = restored_metrics(filtered, paths, ["A"], *args)
        b = restored_metrics(filtered, paths, ["B"], *args)
        pair = restored_metrics(filtered, paths, ["A", "B"], *args)
        self.assertEqual(pair["dd_increase_vs_filter_usd"], 90)
        self.assertEqual(a["dd_increase_vs_filter_usd"] + b["dd_increase_vs_filter_usd"], 180)

    def test_fast_pair_restoration_matches_full_path_metrics(self):
        filtered = np.array([100., -10., 100., -10.])
        paths = {"A": np.array([0., -90., 90., 0.]), "B": np.array([0., 0., 0., -90.])}
        full = restored_metrics(filtered, paths, ["A", "B"], self.days(4), 100, 10)
        fast = restoration_dd_only(filtered, paths, ["A", "B"], 100, 10)
        for key in fast:
            self.assertEqual(fast[key], full[key])


if __name__ == "__main__":
    unittest.main()
