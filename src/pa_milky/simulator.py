"""The brick-1 book: one new PA per calendar month, every PA trades everything."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .account import Account, money
from .config import RunConfig
from .loader import Trade


def month_key(moment: datetime) -> str:
    return f"{moment.year:04d}-{moment.month:02d}"


def months_in_span(first: datetime, last: datetime) -> list[tuple[int, int]]:
    """Every calendar month from ``first`` to ``last`` inclusive."""

    months: list[tuple[int, int]] = []
    year, month = first.year, first.month
    while (year, month) <= (last.year, last.month):
        months.append((year, month))
        month += 1
        if month == 13:
            year, month = year + 1, 1
    return months


@dataclass(frozen=True, slots=True)
class BookResult:
    accounts: list[Account]
    trades_loaded: int
    copies_filled: int
    tape_first_entry: datetime
    tape_last_exit: datetime
    config: RunConfig

    @property
    def alive(self) -> list[Account]:
        return [a for a in self.accounts if a.alive]

    @property
    def dead(self) -> list[Account]:
        return [a for a in self.accounts if not a.alive]

    @property
    def total_purchase_cost_usd(self) -> float:
        return money(len(self.accounts) * self.config.purchase_fee_usd)


def run_book(trades: list[Trade], config: RunConfig) -> BookResult:
    """Open one PA per calendar month and copy every trade to every live PA."""

    if not trades:
        raise ValueError("no trades to simulate")

    first_entry = min(t.entry_at for t in trades)
    last_exit = max(t.exit_at for t in trades)

    accounts: list[Account] = []
    for index, (year, month) in enumerate(months_in_span(first_entry, last_exit), start=1):
        if config.max_accounts is not None and index > config.max_accounts:
            break
        accounts.append(
            Account(
                account_id=index,
                cohort_month=f"{year:04d}-{month:02d}",
                activated_at=datetime(year, month, 1),
                purchase_fee_usd=config.purchase_fee_usd,
                trailing_drawdown_usd=config.trailing_drawdown_usd,
                frozen_floor_profit_usd=config.frozen_floor_profit_usd,
                threshold_touch_fails=config.threshold_touch_fails,
            )
        )

    commission = config.commission_per_copy_usd
    path_order = config.path_order
    copies = 0

    # Trades arrive in settlement (exit) order; an account may only take a trade
    # whose entry is at or after its own activation.
    for trade in trades:
        for account in accounts:
            if account.activated_at > trade.entry_at:
                break  # accounts are activation-ordered; the rest are younger
            if not account.alive:
                continue
            account.apply(trade, commission_usd=commission, path_order=path_order)
            copies += 1

    return BookResult(
        accounts=accounts,
        trades_loaded=len(trades),
        copies_filled=copies,
        tape_first_entry=first_entry,
        tape_last_exit=last_exit,
        config=config,
    )
