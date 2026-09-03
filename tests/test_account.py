"""Legacy 25K trailing-drawdown mechanics."""

from __future__ import annotations

from datetime import datetime
import unittest

from pa_milky.account import Account
from pa_milky.loader import Trade

ENTRY = datetime(2020, 1, 2, 10, 0, 0)
EXIT = datetime(2020, 1, 2, 11, 0, 0)


def trade(mae: float, mfe: float, pnl: float) -> Trade:
    return Trade(
        trade_key="t",
        window_id="10-11",
        window_order=10,
        source_row=1,
        ticket=1,
        entry_at=ENTRY,
        exit_at=EXIT,
        mae_usd=mae,
        mfe_usd=mfe,
        gross_pnl_usd=pnl,
        candle_range=0.0,
    )


def account(**overrides) -> Account:
    kwargs = {
        "account_id": 1,
        "cohort_month": "2020-01",
        "activated_at": datetime(2020, 1, 1),
        "purchase_fee_usd": 200.0,
        "trailing_drawdown_usd": 1500.0,
        "frozen_floor_profit_usd": 100.0,
        "threshold_touch_fails": True,
    }
    kwargs.update(overrides)
    return Account(**kwargs)


class TestStartingState(unittest.TestCase):
    def test_fresh_account(self):
        pa = account()
        self.assertTrue(pa.alive)
        self.assertEqual(pa.balance_usd, 25_000.0)
        self.assertEqual(pa.floor_profit_usd, -1_500.0)
        self.assertEqual(pa.headroom_usd, 1_500.0)


class TestDrawdownTouch(unittest.TestCase):
    def test_touching_the_threshold_kills(self):
        pa = account()
        self.assertFalse(pa.apply(trade(-1_500.0, 0.0, -1_500.0), commission_usd=0.0, path_order="mae_first"))
        self.assertFalse(pa.alive)
        self.assertEqual(pa.death_reason, "intratrade_excursion")
        self.assertEqual(pa.death_equity_usd, -1_500.0)
        self.assertEqual(pa.died_at, EXIT)

    def test_half_a_dollar_short_survives(self):
        pa = account()
        self.assertTrue(pa.apply(trade(-1_499.5, 0.0, -1_499.5), commission_usd=0.0, path_order="mae_first"))
        self.assertTrue(pa.alive)
        self.assertEqual(pa.equity_profit_usd, -1_499.5)

    def test_touch_can_be_configured_off(self):
        pa = account(threshold_touch_fails=False)
        self.assertTrue(pa.apply(trade(-1_500.0, 0.0, 0.0), commission_usd=0.0, path_order="mae_first"))
        self.assertTrue(pa.alive)

    def test_close_below_threshold_kills(self):
        # A close that lands on the floor without the excursion reaching it
        # first is still a death, reported under its own reason.
        pa = account()
        self.assertFalse(pa.apply(trade(0.0, 0.0, -1_500.0), commission_usd=0.0, path_order="mae_first"))
        self.assertEqual(pa.death_reason, "closed_below_threshold")


class TestTrailingFloor(unittest.TestCase):
    def test_floor_trails_the_peak(self):
        pa = account()
        pa.apply(trade(0.0, 0.0, 1_000.0), commission_usd=0.0, path_order="mae_first")
        self.assertEqual(pa.peak_profit_usd, 1_000.0)
        self.assertEqual(pa.floor_profit_usd, -500.0)

    def test_floor_freezes_at_plus_one_hundred(self):
        pa = account()
        pa.apply(trade(0.0, 0.0, 1_600.0), commission_usd=0.0, path_order="mae_first")
        self.assertEqual(pa.floor_profit_usd, 100.0)
        pa.apply(trade(0.0, 0.0, 10_000.0), commission_usd=0.0, path_order="mae_first")
        self.assertEqual(pa.peak_profit_usd, 11_600.0)
        self.assertEqual(pa.floor_profit_usd, 100.0)

    def test_floor_never_falls_back(self):
        pa = account()
        pa.apply(trade(0.0, 0.0, 1_000.0), commission_usd=0.0, path_order="mae_first")
        pa.apply(trade(0.0, 0.0, -400.0), commission_usd=0.0, path_order="mae_first")
        self.assertEqual(pa.peak_profit_usd, 1_000.0)
        self.assertEqual(pa.floor_profit_usd, -500.0)

    def test_unrealized_peak_lifts_the_floor(self):
        # The floor trails the intratrade high, not just the closed balance.
        pa = account()
        pa.apply(trade(0.0, 900.0, 100.0), commission_usd=0.0, path_order="mae_first")
        self.assertEqual(pa.peak_profit_usd, 900.0)
        self.assertEqual(pa.floor_profit_usd, -600.0)


class TestPathOrder(unittest.TestCase):
    def test_mae_first_is_the_conservative_reading(self):
        # Equity 0, floor -1500. The trade dips 1500 and rallies 3000.
        # Conservatively the dip lands first and the account is gone.
        pa = account()
        survived = pa.apply(trade(-1_500.0, 3_000.0, 500.0), commission_usd=0.0, path_order="mae_first")
        self.assertFalse(survived)

    def test_mfe_first_lifts_the_floor_before_the_dip(self):
        # Same trade, optimistic ordering: the rally lifts the floor to +100
        # first, so the dip to -1500 is still a death -- but a later, smaller
        # dip would not be. Use a survivable dip to show the divergence.
        pa = account()
        survived = pa.apply(trade(-1_400.0, 3_000.0, 500.0), commission_usd=0.0, path_order="mfe_first")
        self.assertFalse(survived)  # floor rose to +100, so -1400 breaches it
        pa = account()
        survived = pa.apply(trade(-1_400.0, 3_000.0, 500.0), commission_usd=0.0, path_order="mae_first")
        self.assertTrue(survived)  # floor still -1500 when the dip is tested


class TestCommission(unittest.TestCase):
    def test_commission_hits_the_close_not_the_excursions(self):
        pa = account()
        pa.apply(trade(-100.0, 100.0, 100.0), commission_usd=1.05, path_order="mae_first")
        self.assertEqual(pa.equity_profit_usd, 98.95)
        self.assertEqual(pa.gross_pnl_usd, 100.0)
        self.assertEqual(pa.commission_usd, 1.05)
        # the peak came from the gross MFE, not the net close
        self.assertEqual(pa.peak_profit_usd, 100.0)

    def test_a_positive_mae_is_clamped_to_no_dip(self):
        # 555 tape trades never trade underwater. Their MAE must not be read as
        # an equity gain that lifts the floor early.
        pa = account()
        pa.apply(trade(4.0, 46.5, 37.5), commission_usd=0.0, path_order="mae_first")
        self.assertEqual(pa.min_equity_profit_usd, 0.0)
        self.assertEqual(pa.peak_profit_usd, 46.5)

    def test_dead_accounts_refuse_further_trades(self):
        pa = account()
        pa.apply(trade(-2_000.0, 0.0, -2_000.0), commission_usd=0.0, path_order="mae_first")
        with self.assertRaises(ValueError):
            pa.apply(trade(0.0, 0.0, 10.0), commission_usd=0.0, path_order="mae_first")


if __name__ == "__main__":
    unittest.main()
