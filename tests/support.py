"""Shared fixtures. The tape and every scenario arm are loaded once per run."""

from __future__ import annotations

from datetime import datetime

from pa_milky.account import Account
from pa_milky.config import CONFIG_ROOT, load_config
from pa_milky.loader import Trade, load_trades
from pa_milky.simulator import run_book

# The two sealed bricks, still on the flat runtime.v1 payload they were sealed
# with. Loading them here is itself a check that the legacy path survives.
BRICK1 = load_config(CONFIG_ROOT / "bricks" / "brick1_ideal_world.json")
BRICK2 = load_config(CONFIG_ROOT / "bricks" / "brick2_monthly_100.json")

IDEAL = load_config(CONFIG_ROOT / "scenarios" / "ideal_world.json")
FULL = load_config(CONFIG_ROOT / "scenarios" / "full_rulebook_monthly_500.json")
NO_RULES_500 = load_config(CONFIG_ROOT / "scenarios" / "no_rules_monthly_500.json")

TRADES = load_trades(
    BRICK1.sweeps_root, strategy=BRICK1.strategy, risk_reward=BRICK1.risk_reward
)

RESULT1 = run_book(TRADES, BRICK1)
RESULT2 = run_book(TRADES, BRICK2)
RESULT_FULL = run_book(TRADES, FULL)
RESULT_NO_RULES = run_book(TRADES, NO_RULES_500)


def make_trade(
    entry: datetime, exit_at: datetime, pnl: float, *, mae=0.0, mfe=0.0, row=1
) -> Trade:
    return Trade(
        trade_key=f"t{row}:{entry:%Y%m%d%H%M%S}",
        window_id="10-11",
        window_order=10,
        source_row=row,
        ticket=row,
        entry_at=entry,
        exit_at=exit_at,
        mae_usd=mae,
        mfe_usd=mfe,
        gross_pnl_usd=pnl,
        candle_range=0.0,
    )


def make_account(profit: float = 0.0, activated=datetime(2020, 1, 1)) -> Account:
    """A live account carrying ``profit``, banked as one trade on its first day."""

    account = Account(
        account_id=1,
        cohort_month=f"{activated:%Y-%m}",
        activated_at=activated,
        purchase_fee_usd=200.0,
        trailing_drawdown_usd=1500.0,
        frozen_floor_profit_usd=100.0,
        threshold_touch_fails=True,
    )
    if profit:
        account.apply(
            make_trade(
                datetime(2020, 1, 2, 9), datetime(2020, 1, 2, 10), profit
            ),
            commission_usd=0.0,
            path_order="mae_first",
        )
    return account


def bank_days(account: Account, days: list[float], *, start_day: int = 3) -> None:
    """Bank one trade per calendar day so day-based rules have something to read."""

    for offset, pnl in enumerate(days):
        day = start_day + offset
        account.apply(
            make_trade(
                datetime(2020, 1, day, 9), datetime(2020, 1, day, 10), pnl, row=100 + offset
            ),
            commission_usd=0.0,
            path_order="mae_first",
        )
