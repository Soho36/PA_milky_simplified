"""The book: one new PA per calendar month, every PA trades everything.

The run is a single causal walk. Trades settle at their exit time, payouts
land when the firm's processing delay runs out, and at each calendar month
boundary the book asks the firm for money and then opens that month's new
account.

Nothing may see the future. Trades and due payouts are interleaved in true time
order rather than batched to the next boundary, so a payout landing on the 11th
is settled against the balance as it stood on the 11th, not as it stands after
the rest of the month has been traded. A trade exiting exactly when a payout is
due settles first, matching the rule that an exit at T precedes other events
at T.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .account import Account, money
from .config import RunConfig
from .loader import Trade
from .payouts import (
    DenialEvent,
    PayoutEvent,
    PendingPayout,
    run_monthly_decision,
    run_terminal_withdrawal,
    settle_pending,
)


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
    requests_unpaid_at_horizon: int
    terminal_payouts: list[PayoutEvent]
    alive_at_horizon: int
    equity_at_horizon_usd: float
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


def _apply_trade(trade: Trade, accounts: list[Account], *, commission: float, path_order: str) -> int:
    copies = 0
    for account in accounts:
        if account.activated_at > trade.entry_at:
            break  # accounts are activation-ordered; the rest are younger
        if not account.alive:
            continue
        account.apply(trade, commission_usd=commission, path_order=path_order)
        copies += 1
    return copies


def _advance(
    trades: list[Trade],
    index: int,
    horizon: datetime | None,
    accounts: list[Account],
    pending: list[PendingPayout],
    config: RunConfig,
    *,
    commission: float,
) -> tuple[int, int, list[PayoutEvent], list[DenialEvent]]:
    """Run the clock forward to ``horizon``, in true event order.

    Returns the new trade index, copies filled, and any payouts or denials that
    fell due along the way.
    """

    copies = 0
    payouts: list[PayoutEvent] = []
    denials: list[DenialEvent] = []

    while True:
        trade_at = trades[index].exit_at if index < len(trades) else None
        due_at = pending[0].due_at if pending else None
        if horizon is not None:
            if trade_at is not None and trade_at > horizon:
                trade_at = None
            if due_at is not None and due_at > horizon:
                due_at = None

        if trade_at is not None and (due_at is None or trade_at <= due_at):
            copies += _apply_trade(
                trades[index], accounts, commission=commission, path_order=config.path_order
            )
            index += 1
            continue
        if due_at is not None:
            paid, denied = settle_pending(pending, due_at, config)
            payouts.extend(paid)
            denials.extend(denied)
            continue
        break

    return index, copies, payouts, denials


def decision_boundaries(first: datetime, last: datetime, cadence: str):
    """Monthly purchase/accrual boundaries plus midnight request checks."""
    dates = {datetime(y, m, 1) for y, m in months_in_span(first, last)}
    if cadence in {"weekly", "daily"}:
        day = datetime(first.year, first.month, 1)
        while day <= last:
            if cadence == "daily" or day.weekday() == 0:
                dates.add(day)
            day += timedelta(days=1)
    return sorted(dates)


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

    opened = 0
    for boundary in decision_boundaries(first_entry, last_exit, config.policy.cadence):
        year, month = boundary.year, boundary.month
        monthly = boundary.day == 1
        if monthly:
            opened += 1
        index, settled, paid, denied = _advance(
            trades, index, boundary, accounts, pending, config, commission=commission
        )
        copies += settled
        payouts.extend(paid)
        denials.extend(denied)

        if asks:
            request = (config.policy.cadence == "daily" or
                       (config.policy.cadence == "weekly" and boundary.weekday() == 0) or
                       (config.policy.cadence == "calendar_month" and monthly))
            paid, denied = run_monthly_decision(
                accounts, boundary, config, pending, accrue=monthly, request=request)
            payouts.extend(paid)
            denials.extend(denied)
            pending.sort(key=lambda item: item.due_at)

        if monthly and (config.max_accounts is None or opened <= config.max_accounts):
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

    # The horizon is the last exit, not "no limit": a request whose delay runs
    # past the end of the tape must not be settled out of thin air.
    index, settled, paid, denied = _advance(
        trades, index, last_exit, accounts, pending, config, commission=commission
    )
    copies += settled
    payouts.extend(paid)
    denials.extend(denied)
    # Anything still due after the last trade never lands: the tape has run out
    # and there is no evidence about what the account did afterwards.
    unpaid_at_horizon = len(pending)

    # Score the book as it stood before any closing withdrawal: an account
    # emptied at the horizon was alive, and its equity was real.
    alive_at_horizon = sum(1 for a in accounts if a.alive)
    equity_at_horizon = money(sum(a.equity_profit_usd for a in accounts if a.alive))
    terminal_paid, terminal_denied = run_terminal_withdrawal(accounts, last_exit, config)
    payouts.extend(terminal_paid)
    denials.extend(terminal_denied)

    payouts.sort(key=lambda event: (event.at, event.account_id))
    denials.sort(key=lambda event: (event.at, event.account_id))

    return BookResult(
        accounts=accounts,
        payouts=payouts,
        denials=denials,
        requests_unpaid_at_horizon=unpaid_at_horizon,
        terminal_payouts=terminal_paid,
        alive_at_horizon=alive_at_horizon,
        equity_at_horizon_usd=equity_at_horizon,
        trades_loaded=len(trades),
        copies_filled=copies,
        tape_first_entry=first_entry,
        tape_last_exit=last_exit,
        config=config,
    )
