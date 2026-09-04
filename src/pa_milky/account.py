"""Legacy 25K Performance Account state.

Equity is tracked as profit relative to the USD 25,000 starting balance, so the
trailing threshold is a single number that starts at -1,500 and rises with the
peak until it freezes at +100 (a nominal USD 25,100).

The account also keeps the bookkeeping the firm's payout rules need: realized
profit per trading day since the last approved payout, how many payouts have
been approved, and how much has cumulatively been paid out.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from .clock import trading_day


def money(value: float) -> float:
    """Round to cents. Every input here is a multiple of a half dollar."""

    return round(value + 0.0, 2)


@dataclass(slots=True)
class Account:
    account_id: int
    cohort_month: str
    activated_at: datetime
    purchase_fee_usd: float
    trailing_drawdown_usd: float
    frozen_floor_profit_usd: float
    threshold_touch_fails: bool
    starting_balance_usd: float = 25_000.0

    equity_profit_usd: float = 0.0
    peak_profit_usd: float = 0.0
    floor_profit_usd: float = field(init=False)
    alive: bool = True
    died_at: datetime | None = None
    death_trade_key: str | None = None
    death_reason: str | None = None
    death_equity_usd: float | None = None

    trades_taken: int = 0
    wins: int = 0
    losses: int = 0
    gross_pnl_usd: float = 0.0
    commission_usd: float = 0.0
    max_equity_profit_usd: float = 0.0
    min_equity_profit_usd: float = 0.0

    # Realized net profit per trading day, cleared at each approved payout.
    # The firm's day-count, profitable-day and consistency rules all read it.
    day_pnl_usd: dict[date, float] = field(default_factory=dict)

    # Withdrawal entitlement: what our own policy says the account owes us.
    entitlement_accrued_usd: float = 0.0
    entitlement_outstanding_usd: float = 0.0
    months_accrued: int = 0

    # Payout state: what the firm has actually approved.
    payout_count: int = 0
    gross_paid_usd: float = 0.0
    received_usd: float = 0.0
    withdrawal_count: int = 0
    first_withdrawal_at: datetime | None = None
    last_withdrawal_at: datetime | None = None
    last_payout_at: datetime | None = None
    requests_blocked: int = 0
    # Months we chose not to ask at all, because our own cushion left
    # nothing spare. Not a firm denial: the firm was never asked.
    requests_withheld: int = 0

    def __post_init__(self) -> None:
        self.floor_profit_usd = money(-self.trailing_drawdown_usd)

    # ------------------------------------------------------------------ views

    @property
    def balance_usd(self) -> float:
        return money(self.starting_balance_usd + self.equity_profit_usd)

    @property
    def headroom_usd(self) -> float:
        return money(self.equity_profit_usd - self.floor_profit_usd)

    @property
    def withdrawn_usd(self) -> float:
        """Gross taken out of the account, before the firm's split."""

        return self.gross_paid_usd

    @property
    def trading_days_since_payout(self) -> int:
        return len(self.day_pnl_usd)

    def profitable_days_since_payout(self, threshold_usd: float) -> int:
        return sum(1 for value in self.day_pnl_usd.values() if value >= threshold_usd)

    @property
    def best_day_since_payout_usd(self) -> float:
        """The largest single-day profit since the last approved payout."""

        return money(max(self.day_pnl_usd.values(), default=0.0))

    # ------------------------------------------------------------------ trades

    def _breached(self, value: float) -> bool:
        if self.threshold_touch_fails:
            return value <= self.floor_profit_usd
        return value < self.floor_profit_usd

    def _lift_peak(self, value: float) -> None:
        if value > self.peak_profit_usd:
            self.peak_profit_usd = money(value)
        self.floor_profit_usd = money(
            min(
                self.peak_profit_usd - self.trailing_drawdown_usd,
                self.frozen_floor_profit_usd,
            )
        )

    def _die(self, at: datetime, reason: str, equity: float, trade_key: str | None) -> None:
        self.alive = False
        self.died_at = at
        self.death_reason = reason
        self.death_equity_usd = equity
        self.death_trade_key = trade_key

    def apply(self, trade, *, commission_usd: float, path_order: str) -> bool:
        """Settle one copy of ``trade``. Returns True if the account survives.

        The excursions are taken gross, as the tester exported them; commission
        is charged only in the closing figure. This mirrors the parent study.
        """

        if not self.alive:
            raise ValueError(f"account {self.account_id} is dead")

        adverse = money(self.equity_profit_usd + min(trade.mae_usd, 0.0))
        favorable = money(self.equity_profit_usd + max(trade.mfe_usd, 0.0))
        net_pnl = money(trade.gross_pnl_usd - commission_usd)

        if path_order == "mfe_first":
            self._lift_peak(favorable)

        if adverse < self.min_equity_profit_usd:
            self.min_equity_profit_usd = adverse
        if self._breached(adverse):
            self.trades_taken += 1
            self._die(trade.exit_at, "intratrade_excursion", adverse, trade.trade_key)
            return False

        if path_order == "mae_first":
            self._lift_peak(favorable)

        self.equity_profit_usd = money(self.equity_profit_usd + net_pnl)
        self.trades_taken += 1
        self.gross_pnl_usd = money(self.gross_pnl_usd + trade.gross_pnl_usd)
        self.commission_usd = money(self.commission_usd + commission_usd)
        if net_pnl >= 0:
            self.wins += 1
        else:
            self.losses += 1
        if self.equity_profit_usd > self.max_equity_profit_usd:
            self.max_equity_profit_usd = self.equity_profit_usd
        if self.equity_profit_usd < self.min_equity_profit_usd:
            self.min_equity_profit_usd = self.equity_profit_usd

        # PA profit and loss is credited on the exit date, per the study clock.
        day = trading_day(trade.exit_at)
        self.day_pnl_usd[day] = money(self.day_pnl_usd.get(day, 0.0) + net_pnl)

        self._lift_peak(self.equity_profit_usd)
        if self._breached(self.equity_profit_usd):
            self._die(
                trade.exit_at, "closed_below_threshold", self.equity_profit_usd, trade.trade_key
            )
            return False
        return True

    # ------------------------------------------------------------- entitlement

    def accrue(self, amount_usd: float, *, keep_backlog: bool = True) -> None:
        """Credit one period of entitlement -- what our policy wants out."""

        if not self.alive:
            raise ValueError(f"account {self.account_id} is dead")
        self.months_accrued += 1
        self.entitlement_accrued_usd = money(self.entitlement_accrued_usd + amount_usd)
        if keep_backlog:
            self.entitlement_outstanding_usd = money(
                self.entitlement_outstanding_usd + amount_usd
            )
        else:
            # No backlog: the period is offered once and expires unpaid.
            self.entitlement_outstanding_usd = money(amount_usd)

    # ----------------------------------------------------------------- payouts

    def pay_out(self, gross_usd: float, received_usd: float, at: datetime) -> bool:
        """Approve a payout. Returns True if the account survives it.

        ``gross_usd`` leaves the account; ``received_usd`` is what reaches our
        pocket after the firm's split. The peak is untouched, so the trailing
        floor does not follow the balance down: a payout spends cushion, which
        is the whole economic point.
        """

        if not self.alive:
            raise ValueError(f"account {self.account_id} is dead")
        if gross_usd <= 0:
            raise ValueError("a payout must be positive")

        self.equity_profit_usd = money(self.equity_profit_usd - gross_usd)
        self.entitlement_outstanding_usd = money(
            max(0.0, self.entitlement_outstanding_usd - gross_usd)
        )
        self.gross_paid_usd = money(self.gross_paid_usd + gross_usd)
        self.received_usd = money(self.received_usd + received_usd)
        self.payout_count += 1
        self.withdrawal_count += 1
        self.last_payout_at = at
        self.last_withdrawal_at = at
        if self.first_withdrawal_at is None:
            self.first_withdrawal_at = at
        if self.equity_profit_usd < self.min_equity_profit_usd:
            self.min_equity_profit_usd = self.equity_profit_usd

        # The firm's day counters run from the last approved payout.
        self.day_pnl_usd.clear()

        if self._breached(self.equity_profit_usd):
            self._die(at, "payout_below_threshold", self.equity_profit_usd, None)
            return False
        return True
