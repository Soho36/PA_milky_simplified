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
from .acquisition import AcquisitionPolicy, AcquisitionLedger
from .config import RunConfig
from .loader import Trade
from .routing import RoutingPolicy, TradeRouter
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
    acquisition: AcquisitionLedger | None = None
    routing: dict | None = None
    routing_fills: list | None = None

    @property
    def alive(self) -> list[Account]:
        return [a for a in self.accounts if a.alive]

    @property
    def dead(self) -> list[Account]:
        return [a for a in self.accounts if not a.alive]

    @property
    def unused_spares(self) -> int:
        """Funded accounts paid for but still dormant when the tape ends: sunk cost."""

        return self.acquisition.spares if self.acquisition is not None else 0

    @property
    def total_purchase_cost_usd(self) -> float:
        """Everything paid for accounts: seats and spares, or evaluations and activations."""

        if self.acquisition is not None:
            return self.acquisition.spent_usd
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
    settle=None,
    observer=None,
    router=None,
    include_boundary_entries=False,
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
        if (router is not None and trade_at is not None and index not in router.assignments
                and trades[index].entry_at == trades[index].exit_at):
            trade_at = None  # an instantaneous trade must first be offered
        due_at = pending[0].due_at if pending else None
        entry_at = router.next_entry if router is not None else None
        if horizon is not None:
            if trade_at is not None and trade_at > horizon:
                trade_at = None
            if due_at is not None and due_at > horizon:
                due_at = None
            # Entries exactly at a decision boundary follow purchases/payouts.
            if entry_at is not None and (entry_at > horizon or
                                        (entry_at == horizon and not include_boundary_entries)):
                entry_at = None

        if entry_at is not None and (trade_at is None or entry_at < trade_at) and (due_at is None or entry_at < due_at):
            router.enter(accounts)
            continue

        if trade_at is not None and (due_at is None or trade_at <= due_at):
            if observer is not None:
                observer(trade_at, accounts, 'before_trade', trades[index])
            if router is None:
                copies += _apply_trade(
                    trades[index], accounts, commission=commission, path_order=config.path_order
                )
            else:
                copies += router.exit(index, trades[index], commission=commission,
                                      path_order=config.path_order)
            if settle is not None:
                # Evaluations trade the same tape, one position at a time.
                settle(index, trades[index])
            if observer is not None:
                observer(trade_at, accounts, 'trade', trades[index])
            index += 1
            continue
        if due_at is not None:
            paid, denied = settle_pending(pending, due_at, config)
            payouts.extend(paid)
            denials.extend(denied)
            if observer is not None:
                observer(due_at, accounts, 'payout', None)
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


def run_book(trades: list[Trade], config: RunConfig, *, acquisition: AcquisitionPolicy | None = None,
             observer=None, routing: RoutingPolicy | None = None, replay=None,
             initial_accounts: int | None = None, fixed_accounts: int | None = None,
             routing_demand: list[int] | None = None, router_factory=None,
             evaluation_tape: list[Trade] | None = None) -> BookResult:
    """Walk the tape, opening one account a month and asking the firm monthly."""

    if not trades:
        raise ValueError("no trades to simulate")
    if router_factory is not None and routing is None:
        raise ValueError("A custom router requires an explicit routing policy")
    if evaluation_tape is not None and (acquisition is None or acquisition.evaluation is None):
        raise ValueError("A separate evaluation tape requires evaluation supply")
    if fixed_accounts is not None:
        if (not isinstance(fixed_accounts, int) or isinstance(fixed_accounts, bool)
                or fixed_accounts < 1):
            raise ValueError('Fixed inventory must be a positive integer')
        if acquisition is not None or replay is not None or initial_accounts is not None or config.max_accounts is not None:
            raise ValueError('Fixed inventory cannot be combined with another purchase policy')
    if routing_demand is not None:
        if routing is None or fixed_accounts is None or replay is not None:
            raise ValueError('Routing demand requires routed fixed inventory')
        if len(routing_demand) != len(trades) or any(
                not isinstance(n, int) or isinstance(n, bool) or n < 0 for n in routing_demand):
            raise ValueError('Routing demand must contain one nonnegative integer per trade')
    if replay is not None and (acquisition is not None or routing is None):
        raise ValueError("A matched replay requires routing and its own frozen purchase schedule")
    if initial_accounts is not None:
        if (not isinstance(initial_accounts, int) or isinstance(initial_accounts, bool)
                or initial_accounts < 1 or acquisition is None or replay is not None
                or acquisition.spare_capacity is not None):
            raise ValueError('Initial accounts require a positive count and direct funded acquisition')
        if (initial_accounts > acquisition.max_live_accounts
                or initial_accounts * config.purchase_fee_usd > acquisition.initial_cash_usd):
            raise ValueError('Initial accounts exceed the live cap or initial cash')

    if acquisition is not None and config.max_accounts is not None:
        raise ValueError("Budgeted acquisition uses its own live-account cap; max_accounts must be unset")
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

    def provision(at, count):
        if replay is not None and replay.max_live_accounts is not None:
            count = min(count, max(0, replay.max_live_accounts - sum(a.alive for a in accounts)))
        for _ in range(count):
            accounts.append(Account(
                account_id=len(accounts) + 1, cohort_month=month_key(at), activated_at=at,
                purchase_fee_usd=config.purchase_fee_usd,
                trailing_drawdown_usd=config.trailing_drawdown_usd,
                frozen_floor_profit_usd=config.frozen_floor_profit_usd,
                threshold_touch_fails=config.threshold_touch_fails,
                starting_balance_usd=config.starting_balance_usd))
        if count and replay is not None:
            replay.record_purchase(at, count, accounts, emergency=True)

    router_type = router_factory or TradeRouter
    router = (router_type(trades, routing,
                          demand=replay.demand if replay is not None else routing_demand,
                          provision=provision if replay is not None else None)
              if routing is not None else None)

    purchasing = AcquisitionLedger(acquisition) if acquisition is not None else None
    settle = None
    if purchasing is not None and purchasing.evaluating:
        evaluation_trades = trades if evaluation_tape is None else evaluation_tape
        purchasing.attach_tape(evaluation_trades, commission_per_mnq=config.commission_usd_per_mnq_round_turn,
                               path_order=config.path_order)
        settle = purchasing.settle
        if evaluation_tape is not None:
            # PA variants share a clock and cash ledger, but evaluations keep
            # their fixed reference strategy rather than trading duplicate RR offers.
            reference = {t.trade_key: (i, t) for i, t in enumerate(evaluation_trades)}
            if len(reference) != len(evaluation_trades):
                raise ValueError("Duplicate evaluation trade keys")
            matched = [t for t in trades if t.trade_key in reference]
            if matched != evaluation_trades:
                raise ValueError("Evaluation tape must be an ordered subset of the event tape")

            def settle(index, trade):
                selected = reference.get(trade.trade_key)
                if selected is not None:
                    purchasing.settle(selected[0], trade)
    opened = 0
    for boundary in decision_boundaries(first_entry, last_exit, "daily" if purchasing or replay is not None else config.policy.cadence):
        year, month = boundary.year, boundary.month
        monthly = boundary.day == 1
        if monthly:
            opened += 1
        index, settled, paid, denied = _advance(
            trades, index, boundary, accounts, pending, config, commission=commission, settle=settle,
            observer=observer, router=router
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

        if fixed_accounts is not None:
            # A single paid initial inventory; deaths never trigger purchases.
            count = fixed_accounts if monthly and opened == 1 else 0
        elif replay is not None:
            count = replay.purchases.get(boundary, 0)
            if replay.max_live_accounts is not None and count + sum(a.alive for a in accounts) > replay.max_live_accounts:
                raise ValueError('Scheduled pool purchase exceeds the live-account cap')
        elif purchasing:
            purchasing.receive(payouts)
            if monthly:
                purchasing.fund(boundary)
            if initial_accounts is not None and monthly and opened == 1:
                # This replaces the first month's ordinary purchase; growth
                # starts next month, with replacements at the usual daily check.
                count = initial_accounts
                purchasing.deploy(boundary, count, config.purchase_fee_usd)
                purchasing.seed_bought = True
                purchasing.filled_month_slots.add((year, month))
                purchasing.decisions.append({'at': boundary.isoformat(), 'wanted': count,
                    'bought': count, 'alive_before': 0, 'initial_inventory': True,
                    'cash_limited': False, 'capacity_limited': False})
            else:
                count = purchasing.decide(boundary, opened-1, sum(a.alive for a in accounts),
                                          len(accounts), config.purchase_fee_usd)
        else:
            count = int(monthly and (config.max_accounts is None or opened <= config.max_accounts))
        for _ in range(count):
            accounts.append(
                Account(
                    account_id=len(accounts)+1 if purchasing or replay is not None or fixed_accounts is not None else opened,
                    cohort_month=f"{year:04d}-{month:02d}",
                    activated_at=boundary,
                    purchase_fee_usd=config.purchase_fee_usd,
                    trailing_drawdown_usd=config.trailing_drawdown_usd,
                    frozen_floor_profit_usd=config.frozen_floor_profit_usd,
                    threshold_touch_fails=config.threshold_touch_fails,
                    starting_balance_usd=config.starting_balance_usd,
                )
            )
        if replay is not None and count:
            replay.record_purchase(boundary, count, accounts, emergency=False)

        if observer is not None:
            observer(boundary, accounts, 'decision', None)

    # The horizon is the last exit, not "no limit": a request whose delay runs
    # past the end of the tape must not be settled out of thin air.
    index, settled, paid, denied = _advance(
        trades, index, last_exit, accounts, pending, config, commission=commission, settle=settle,
        observer=observer, router=router, include_boundary_entries=True
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
    if observer is not None:
        observer(last_exit, accounts, 'horizon', None)
    terminal_paid, terminal_denied = run_terminal_withdrawal(accounts, last_exit, config)
    payouts.extend(terminal_paid)
    denials.extend(terminal_denied)

    if purchasing:
        purchasing.receive(payouts)
        if purchasing.summary()["cash_identity_residual_usd"] != 0:
            raise ValueError("Acquisition cash ledger failed to reconcile")
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
        acquisition=purchasing,
        routing=router.summary() if router is not None else None,
        routing_fills=router.fills if router is not None else None,
    )
