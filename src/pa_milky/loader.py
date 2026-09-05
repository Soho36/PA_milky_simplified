"""Loader for the frozen RR sweep exports.

The sweep files are UTF-16, tab separated, headerless, and carry seven fields
per completed trade. Every dollar figure is stated for one MNQ contract.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import math
from pathlib import Path

RAW_COLUMNS = ("ticket", "entry_time", "exit_time", "mae", "mfe", "pnl", "candle_range")
STATS_COLUMNS = (
    "run_tag",
    "risk_reward",
    "trades",
    "net_profit",
    "gross_profit",
    "gross_loss",
    "equity_dd",
    "balance_dd",
    "profit_factor",
    "expected_payoff",
    "recovery_factor",
    "sharpe",
)
SOURCE_TIME_FORMAT = "%Y.%m.%d %H:%M:%S"
WINDOWS = tuple(f"{hour}-{hour + 1}" for hour in range(1, 24))


@dataclass(frozen=True, slots=True)
class Trade:
    """One completed trade offered to every eligible account."""

    trade_key: str
    window_id: str
    window_order: int
    source_row: int
    ticket: int
    entry_at: datetime
    exit_at: datetime
    mae_usd: float
    mfe_usd: float
    gross_pnl_usd: float
    candle_range: float


def _window_paths(root: Path, strategy: str, risk_reward: str) -> dict[str, tuple[Path, Path]]:
    """Locate the (trades, stats) pair for every hourly window."""

    found: dict[str, tuple[Path, Path]] = {}
    for window in WINDOWS:
        trades = root / strategy / window / f"{window}_{risk_reward}.csv"
        stats = root / f"{strategy}_stats" / window / f"{window}_{risk_reward}_stats.csv"
        if not trades.is_file():
            raise FileNotFoundError(f"Missing trade export: {trades}")
        if not stats.is_file():
            raise FileNotFoundError(f"Missing stats export: {stats}")
        found[window] = (trades, stats)
    return found


def _read_stats(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-16", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != STATS_COLUMNS:
            raise ValueError(f"{path}: stats schema mismatch")
        rows = [row for row in reader if any(field for field in row.values())]
    if len(rows) != 1:
        raise ValueError(f"{path}: expected one stats row, got {len(rows)}")
    return rows[0]


def load_trades(
    sweeps_root: str | Path,
    *,
    strategy: str = "RR",
    risk_reward: str = "1.00",
) -> list[Trade]:
    """Load all 23 hourly windows, reconciled against the tester's own stats."""

    root = Path(sweeps_root)
    paths = _window_paths(root, strategy, risk_reward)
    trades: list[Trade] = []

    for order, window in enumerate(WINDOWS, start=1):
        trades_path, stats_path = paths[window]
        row_count = 0
        pnl_sum = Decimal("0")
        seen_tickets: set[int] = set()

        with trades_path.open("r", encoding="utf-16", newline="") as handle:
            for source_row, row in enumerate(csv.reader(handle, delimiter="\t"), start=1):
                if not any(field.strip() for field in row):
                    continue  # the exporter leaves a trailing blank line
                if len(row) != len(RAW_COLUMNS):
                    raise ValueError(
                        f"{trades_path}:{source_row}: expected {len(RAW_COLUMNS)} "
                        f"fields, got {len(row)}"
                    )
                ticket_text, entry_text, exit_text, mae_text, mfe_text, pnl_text, range_text = row
                try:
                    ticket = int(ticket_text)
                    mae, mfe, pnl, candle_range = (
                        float(mae_text),
                        float(mfe_text),
                        float(pnl_text),
                        float(range_text),
                    )
                except ValueError as exc:
                    raise ValueError(f"{trades_path}:{source_row}: bad numeric field") from exc
                if not all(math.isfinite(v) for v in (mae, mfe, pnl, candle_range)):
                    raise ValueError(f"{trades_path}:{source_row}: non-finite value")
                if ticket in seen_tickets:
                    raise ValueError(f"{trades_path}:{source_row}: duplicate ticket {ticket}")
                seen_tickets.add(ticket)

                entry_at = datetime.strptime(entry_text, SOURCE_TIME_FORMAT)
                exit_at = datetime.strptime(exit_text, SOURCE_TIME_FORMAT)
                if exit_at < entry_at:
                    raise ValueError(f"{trades_path}:{source_row}: exit precedes entry")

                pnl_sum += Decimal(pnl_text)
                row_count += 1
                trades.append(
                    Trade(
                        trade_key=f"{strategy}{risk_reward}:{window}:{source_row}:{ticket}",
                        window_id=window,
                        window_order=order,
                        source_row=source_row,
                        ticket=ticket,
                        entry_at=entry_at,
                        exit_at=exit_at,
                        mae_usd=mae,
                        mfe_usd=mfe,
                        gross_pnl_usd=pnl,
                        candle_range=candle_range,
                    )
                )

        stats = _read_stats(stats_path)
        if stats["run_tag"] != window:
            raise ValueError(f"{stats_path}: run_tag {stats['run_tag']!r} is not {window!r}")
        if not math.isclose(float(stats["risk_reward"]), float(risk_reward)):
            raise ValueError(f"{stats_path}: risk_reward is not {risk_reward}")
        if int(stats["trades"]) != row_count:
            raise ValueError(
                f"{trades_path}: {row_count} rows disagree with tester stats {stats['trades']}"
            )
        if Decimal(stats["net_profit"]) != pnl_sum:
            raise ValueError(
                f"{trades_path}: P&L sum {pnl_sum} disagrees with tester stats "
                f"{stats['net_profit']}"
            )

    # Settlement order. Realized P&L lands at the exit, so the book is walked by
    # exit time; the remaining keys only make ties deterministic.
    trades.sort(key=lambda t: (t.exit_at, t.entry_at, t.window_order, t.source_row, t.ticket))
    return trades


def load_tape(config) -> list[Trade]:
    """Load the tape a config names, and check it is the tape it claims.

    ``expected_trades`` and ``expected_windows`` are recorded in every sealed
    manifest, so they have to mean something. A run that overrides the strategy
    or the risk/reward sets them to None rather than carrying a count that
    belongs to a different tape.
    """

    trades = load_trades(
        config.sweeps_root, strategy=config.strategy, risk_reward=config.risk_reward
    )
    if config.expected_windows is not None:
        windows = {trade.window_id for trade in trades}
        if len(windows) != config.expected_windows:
            raise ValueError(
                f"{config.strategy} @ {config.risk_reward}: config declares "
                f"{config.expected_windows} windows, tape has {len(windows)}"
            )
    if config.expected_trades is not None and len(trades) != config.expected_trades:
        raise ValueError(
            f"{config.strategy} @ {config.risk_reward}: config declares "
            f"{config.expected_trades} trades, tape has {len(trades)}. If the tape "
            "was overridden on purpose, clear the declared size instead of "
            "carrying one that belongs to another strategy."
        )
    return trades
