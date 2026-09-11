"""Evaluation accounts traded on the tape: where funded accounts come from.

An evaluation is a fresh account under the firm's evaluation rules. It trades
the same signals as the book, but one position at a time and at its own size.
Its drawdown trails peak equity, open profit included, and never freezes. It
passes when a closed balance reaches the target. This follows the EODMAE
study's Legacy model, where the evaluation sizes were chosen.

The subscription renews monthly on its start day. A blown evaluation sits
dormant until renewal, which resets it; a live one carries on.
"""

from __future__ import annotations

from bisect import bisect_left
import calendar
from dataclasses import dataclass
from datetime import datetime, timedelta

from .account import money


@dataclass(frozen=True)
class EvaluationSpec:
    profit_target_usd: float
    trailing_drawdown_usd: float
    monthly_fee_usd: float
    activation_fee_usd: float
    contracts: int

    def __post_init__(self):
        if min(self.profit_target_usd, self.trailing_drawdown_usd,
               self.monthly_fee_usd, self.activation_fee_usd) <= 0 or self.contracts < 1:
            raise ValueError('Evaluation target, drawdown, fees and size must be positive')


def add_months(at: datetime, months: int) -> datetime:
    """The same day ``months`` later, clamped to the month's last day."""

    total = at.month - 1 + months
    year, month = at.year + total // 12, total % 12 + 1
    return at.replace(year=year, month=month, day=min(at.day, calendar.monthrange(year, month)[1]))


class Router:
    """One position at a time: the next trade is the first entering at or after a moment.

    ``trades`` is the settlement-ordered tape. Entry ties go to the trade that
    settles first, so the choice is deterministic.
    """

    def __init__(self, trades):
        self.order = sorted(range(len(trades)), key=lambda i: (trades[i].entry_at, i))
        self.entries = [trades[i].entry_at for i in self.order]

    def first(self, at: datetime, settled: int = 0) -> int | None:
        """Tape index of the first trade entering at or after ``at`` that has not yet settled."""

        pos = bisect_left(self.entries, at)
        while pos < len(self.order) and self.order[pos] < settled:
            pos += 1
        return self.order[pos] if pos < len(self.order) else None


@dataclass
class Evaluation:
    eval_id: int
    started_at: datetime
    state: str = 'running'  # running, blown, passed, funded or cancelled
    months_paid: int = 0
    resets: int = 0
    # Bumped by every reset, so a routing entry left over from before is ignored.
    generation: int = 0
    equity_usd: float = 0.0
    peak_usd: float = 0.0
    floor_usd: float = 0.0
    trades_taken: int = 0
    passed_at: datetime | None = None
    ended_at: datetime | None = None

    @property
    def renews_at(self) -> datetime:
        return add_months(self.started_at, self.months_paid)

    def reset(self, spec: EvaluationSpec) -> None:
        self.state = 'running'
        self.generation += 1
        self.equity_usd = self.peak_usd = 0.0
        self.floor_usd = money(-spec.trailing_drawdown_usd)

    def _lift(self, value: float, spec: EvaluationSpec) -> None:
        # Unlike a funded account, the evaluation drawdown never freezes.
        if value > self.peak_usd:
            self.peak_usd = money(value)
        self.floor_usd = money(self.peak_usd - spec.trailing_drawdown_usd)

    def apply(self, trade, spec: EvaluationSpec, *, commission_per_mnq: float, path_order: str) -> str:
        """Settle one trade at the evaluation's size and return its state."""

        size = spec.contracts
        adverse = money(self.equity_usd + size * min(trade.mae_usd, 0.0))
        favorable = money(self.equity_usd + size * max(trade.mfe_usd, 0.0))
        self.trades_taken += 1
        if path_order == 'mfe_first':
            self._lift(favorable, spec)
        if adverse <= self.floor_usd:
            self.state = 'blown'
            return self.state
        if path_order == 'mae_first':
            self._lift(favorable, spec)
        self.equity_usd = money(self.equity_usd + size * (trade.gross_pnl_usd - commission_per_mnq))
        self._lift(self.equity_usd, spec)
        if self.equity_usd <= self.floor_usd:
            self.state = 'blown'
        elif self.equity_usd >= spec.profit_target_usd:
            self.state = 'passed'
            self.passed_at = trade.exit_at
        return self.state


def run_episode(trades, router: Router, spec: EvaluationSpec, start: datetime, *,
                commission_per_mnq: float, path_order: str, horizon_days: int = 180):
    """One evaluation bought at ``start``, renewed until it passes or the horizon ends.

    Returns ``(passed_at or None, months paid)``. This is the single-slot episode
    of the EODMAE study, used to reconcile the two models.
    """

    end = start + timedelta(days=horizon_days)
    evaluation = Evaluation(0, start, months_paid=1)
    evaluation.reset(spec)
    index = router.first(start)
    while True:
        if evaluation.state == 'blown' or index is None:
            renewal = evaluation.renews_at
            if renewal >= end:
                return None, evaluation.months_paid
            evaluation.months_paid += 1
            if evaluation.state == 'blown':
                evaluation.reset(spec)
                evaluation.resets += 1
                index = router.first(renewal)
            continue
        trade = trades[index]
        while evaluation.renews_at <= min(trade.exit_at, end) and evaluation.renews_at < end:
            evaluation.months_paid += 1
        if trade.exit_at > end:
            return None, evaluation.months_paid
        if evaluation.apply(trade, spec, commission_per_mnq=commission_per_mnq,
                            path_order=path_order) == 'passed':
            return trade.exit_at, evaluation.months_paid
        if evaluation.state == 'running':
            index = router.first(trade.exit_at, settled=index + 1)
