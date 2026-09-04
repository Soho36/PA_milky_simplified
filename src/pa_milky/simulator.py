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
    requests_unpaid_at_horizon: int
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
        index, settled, paid, denied = _advance(
            trades, index, boundary, accounts, pending, config, commission=commission
        )
        copies += settled
        payouts.extend(paid)
        denials.extend(denied)

        if asks:
            paid, denied = run_monthly_decision(accounts, boundary, config, pending)
            payouts.extend(paid)
            denials.extend(denied)
            pending.sort(key=lambda item: item.due_at)

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

    payouts.sort(key=lambda event: (event.at, event.account_id))
    denials.sort(key=lambda event: (event.at, event.account_id))

    return BookResult(
        accounts=accounts,
        payouts=payouts,
        denials=denials,
        requests_unpaid_at_horizon=unpaid_at_horizon,
        trades_loaded=len(trades),
        copies_filled=copies,
        tape_first_entry=first_entry,
        tape_last_exit=last_exit,
        config=config,
    )
