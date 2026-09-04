"""The book: one new PA per calendar month, every PA trades everything.

The run is a single causal walk. Trades settle at their exit time; at each
calendar month boundary the book pauses to ask the firm for money and then
opens that month's new account. A trade exiting exactly on a boundary settles
before the request, so a payout is never asked out of money that had not yet
been realized.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .account import Account, money
from .config import RunConfig
from .loader import Trade
from .payouts import DenialEvent, PayoutEvent, PendingPayout, run_monthly_decision, settle_pending


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
    payouts: list[PayoutEvent]
    denials: list[DenialEvent]
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

    @property
    def total_withdrawn_usd(self) -> float:
        """Gross out of the accounts, before the firm's split."""

        return money(sum(a.gross_paid_usd for a in self.accounts))

    @property
    def total_received_usd(self) -> float:
        """What actually reached us, after the split."""

        return money(sum(a.received_usd for a in self.accounts))

    @property
    def pocket_usd(self) -> float:
        return money(self.total_received_usd - self.total_purchase_cost_usd)


def _settle_through(
    trades: list[Trade],
    index: int,
    boundary: datetime | None,
    accounts: list[Account],
    *,
    commission: float,
    path_order: str,
) -> tuple[int, int]:
    """Settle every trade exiting at or before ``boundary``. Returns (index, copies)."""

    copies = 0
    while index < len(trades):
        trade = trades[index]
        if boundary is not None and trade.exit_at > boundary:
            break
        for account in accounts:
            if account.activated_at > trade.entry_at:
                break  # accounts are activation-ordered; the rest are younger
            if not account.alive:
                continue
            account.apply(trade, commission_usd=commission, path_order=path_order)
            copies += 1
        index += 1
    return index, copies


def run_book(trades: list[Trade], config: RunConfig) -> BookResult:
    """Walk the tape, opening one account a month and asking the firm monthly."""

    if not trades:
        raise ValueError("no trades to simulate")

    first_entry = min(t.entry_at for t in trades)
    last_exit = max(t.exit_at for t in trades)
    commission = config.commission_per_copy_usd
    asks = config.policy.enabled

    accounts: list[Account] = []
    payouts: list[PayoutEvent] = []
    denials: list[DenialEvent] = []
    pending: list[PendingPayout] = []
    index = 0
    copies = 0

    for opened, (year, month) in enumerate(months_in_span(first_entry, last_exit), start=1):
        boundary = datetime(year, month, 1)
        index, settled = _settle_through(
            trades, index, boundary, accounts,
            commission=commission, path_order=config.path_order,
        )
        copies += settled

        if asks:
            if pending:
                paid, denied = settle_pending(pending, boundary, config)
                payouts.extend(paid)
                denials.extend(denied)
            paid, denied = run_monthly_decision(accounts, boundary, config, pending)
            payouts.extend(paid)
            denials.extend(denied)

        if config.max_accounts is None or opened <= config.max_accounts:
            accounts.append(
                Account(
                    account_id=opened,
                    cohort_month=f"{year:04d}-{month:02d}",
                    activated_at=boundary,
                    purchase_fee_usd=config.purchase_fee_usd,
                    trailing_drawdown_usd=config.trailing_drawdown_usd,
                    frozen_floor_profit_usd=config.frozen_floor_profit_usd,
                    threshold_touch_fails=config.threshold_touch_fails,
                    starting_balance_usd=config.starting_balance_usd,
                )
            )

    index, settled = _settle_through(
        trades, index, None, accounts,
        commission=commission, path_order=config.path_order,
    )
    copies += settled
    if pending:
        paid, denied = settle_pending(pending, last_exit, config)
        payouts.extend(paid)
        denials.extend(denied)

    payouts.sort(key=lambda event: (event.at, event.account_id))
    denials.sort(key=lambda event: (event.at, event.account_id))

    return BookResult(
        accounts=accounts,
        payouts=payouts,
        denials=denials,
        trades_loaded=len(trades),
        copies_filled=copies,
        tape_first_entry=first_entry,
        tape_last_exit=last_exit,
        config=config,
    )
