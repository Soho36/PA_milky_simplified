"""Legacy 25K Performance Account drawdown state.

Equity is tracked as profit relative to the USD 25,000 starting balance, so the
trailing threshold is a single number that starts at -1,500 and rises with the
peak until it freezes at +100 (a nominal USD 25,100).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


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

    # Withdrawal state. Entitlement accrues monthly whether or not the account
    # can pay; outstanding is what it still owes the owner.
    entitlement_accrued_usd: float = 0.0
    entitlement_outstanding_usd: float = 0.0
    withdrawn_usd: float = 0.0
    withdrawal_count: int = 0
    months_accrued: int = 0
    first_withdrawal_at: datetime | None = None
    last_withdrawal_at: datetime | None = None

    def __post_init__(self) -> None:
        self.floor_profit_usd = money(-self.trailing_drawdown_usd)

    @property
    def balance_usd(self) -> float:
        return money(25_000.0 + self.equity_profit_usd)

    @property
    def headroom_usd(self) -> float:
        return money(self.equity_profit_usd - self.floor_profit_usd)

    def _breached(self, value: float) -> bool:
        return value <= self.floor_profit_usd if self.threshold_touch_fails else value < self.floor_profit_usd

    def _lift_peak(self, value: float) -> None:
        if value > self.peak_profit_usd:
            self.peak_profit_usd = money(value)
        self.floor_profit_usd = money(
            min(
                self.peak_profit_usd - self.trailing_drawdown_usd,
                self.frozen_floor_profit_usd,
            )
        )

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
            self.alive = False
            self.died_at = trade.exit_at
            self.death_trade_key = trade.trade_key
            self.death_reason = "intratrade_excursion"
            self.death_equity_usd = adverse
            self.trades_taken += 1
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

        self._lift_peak(self.equity_profit_usd)
        if self._breached(self.equity_profit_usd):
            self.alive = False
            self.died_at = trade.exit_at
            self.death_trade_key = trade.trade_key
            self.death_reason = "closed_below_threshold"
            self.death_equity_usd = self.equity_profit_usd
            return False
        return True

    def accrue(self, amount_usd: float, *, keep_backlog: bool = True) -> None:
        """Credit one month of entitlement to this account."""

        if not self.alive:
            raise ValueError(f"account {self.account_id} is dead")
        self.months_accrued += 1
        self.entitlement_accrued_usd = money(self.entitlement_accrued_usd + amount_usd)
        if keep_backlog:
            self.entitlement_outstanding_usd = money(
                self.entitlement_outstanding_usd + amount_usd
            )
        else:
            # No backlog: the month is offered once and expires unpaid.
            self.entitlement_outstanding_usd = money(amount_usd)

    def withdraw(self, amount_usd: float, at: datetime) -> bool:
        """Move cash out. Returns True if the account survives the withdrawal.

        The peak is untouched, so the trailing floor does not follow the balance
        down. A withdrawal spends cushion, which is the whole economic point.
        """

        if not self.alive:
            raise ValueError(f"account {self.account_id} is dead")
        if amount_usd <= 0:
            raise ValueError("withdrawal must be positive")
        if amount_usd > self.entitlement_outstanding_usd + 1e-9:
            raise ValueError("withdrawal exceeds the outstanding entitlement")

        self.equity_profit_usd = money(self.equity_profit_usd - amount_usd)
        self.entitlement_outstanding_usd = money(
            self.entitlement_outstanding_usd - amount_usd
        )
        self.withdrawn_usd = money(self.withdrawn_usd + amount_usd)
        self.withdrawal_count += 1
        self.last_withdrawal_at = at
        if self.first_withdrawal_at is None:
            self.first_withdrawal_at = at
        if self.equity_profit_usd < self.min_equity_profit_usd:
            self.min_equity_profit_usd = self.equity_profit_usd

        if self._breached(self.equity_profit_usd):
            self.alive = False
            self.died_at = at
            self.death_reason = "withdrawal_below_threshold"
            self.death_equity_usd = self.equity_profit_usd
            return False
        return True
