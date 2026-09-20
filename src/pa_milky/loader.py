"""Loader for the frozen RR sweep exports.

The sweep files are UTF-16, tab separated, headerless, and carry seven fields
per completed trade. Every dollar figure is stated for one MNQ contract.

Per-window reconciliation against each ``_stats`` file catches a damaged export
but not a *short* one. When an MT5 test ends early -- most often because the
test account was wiped -- the exporter writes a faithful record of the run it
actually had, and its stats are generated from that same short run, so counts
and P&L sums reconcile and nothing looks wrong. That truncation is not neutral:
it removes history at the moment of the worst drawdown, so the setting looks
better than it was. ``config/tape_coverage.json`` pins how far every window
reaches, and ``load_trades`` refuses a tape that falls short of it.
"""

from __future__ import annotations

import csv
import json
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
# Committed alongside the code because 1_sweeps/ is not committed.
COVERAGE_SCHEMA = "pa_milky_simplified.tape_coverage.v1"
COVERAGE_PATH = Path(__file__).resolve().parents[2] / "config" / "tape_coverage.json"


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


def read_coverage(path: Path | None = None) -> dict:
    """Read the required coverage reference; missing pins must not disable checks."""

    if path is None:
        path = COVERAGE_PATH
    if not path.is_file():
        raise FileNotFoundError(f"Missing tape coverage reference: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != COVERAGE_SCHEMA:
        raise ValueError(f"{path}: coverage schema {payload.get('schema')!r} unsupported")
    return payload


def coverage_shortfalls(
    strategy: str, last_exits: dict[str, datetime], coverage: dict | None
) -> list[tuple[str, datetime, datetime, float]]:
    """Windows ending earlier than pinned, as (window, reached, required, days_short).

    A window may legitimately end a little early: a different risk/reward exits
    the same entries at different moments, so the final trade can settle either
    side of the reference. It may not end *months* early. Measured across the
    whole grid, a complete window is never more than a day off its reference and
    a truncated one is at least sixteen days short, so the tolerance separates
    them with room to spare.
    """

    if coverage is None:
        raise ValueError("Missing tape coverage reference")
    windows = coverage.get("strategies", {}).get(strategy)
    if windows is None:
        raise ValueError(f"Missing tape coverage reference for strategy {strategy}")
    missing_pins = [
        window for window in WINDOWS
        if not isinstance(windows.get(window), dict)
        or not windows[window].get("last_exit")
    ]
    if missing_pins:
        raise ValueError(
            f"{strategy}: missing last_exit coverage pins for windows: "
            + ", ".join(missing_pins)
        )
    missing_exits = [window for window in WINDOWS if window not in last_exits]
    if missing_exits:
        raise ValueError(
            f"{strategy}: no trades observed for required windows: "
            + ", ".join(missing_exits)
        )
    tolerance = float(coverage.get("tolerance_days", 0))
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("Coverage tolerance_days must be finite and nonnegative")
    shortfalls = []
    for window in WINDOWS:
        reached = last_exits[window]
        required = datetime.fromisoformat(windows[window]["last_exit"])
        days_short = (required - reached).total_seconds() / 86400
        if days_short > tolerance:
            shortfalls.append((window, reached, required, days_short))
    return shortfalls


def _coverage_error(strategy: str, risk_reward: str, shortfalls, coverage: dict) -> str:
    worst = max(shortfalls, key=lambda row: row[3])
    lines = [
        f"{strategy} @ {risk_reward}: {len(shortfalls)} of {len(WINDOWS)} windows stop "
        f"short of the coverage pinned in {COVERAGE_PATH.name} "
        f"(reference risk/reward {coverage.get('reference_risk_reward')}, "
        f"tolerance {coverage.get('tolerance_days')} days). "
        "A short export is usually an MT5 test that ended early because the test "
        "account was wiped; its stats come from the same short run, so counts and "
        "P&L reconcile and the gap is otherwise invisible. Re-exporting reproduces "
        "it -- raise the test deposit and re-run the backtest.",
        f"  worst: window {worst[0]} reached {worst[1].isoformat()}, "
        f"needs {worst[2].isoformat()} ({worst[3]:.0f} days short)",
    ]
    for window, reached, required, days_short in shortfalls[:8]:
        lines.append(
            f"  {window}: {reached.date()} vs {required.date()} ({days_short:.0f} days short)"
        )
    if len(shortfalls) > 8:
        lines.append(f"  ... and {len(shortfalls) - 8} more")
    return "\n".join(lines)


def load_trades(
    sweeps_root: str | Path,
    *,
    strategy: str = "RR",
    risk_reward: str = "1.00",
    check_coverage: bool = True,
) -> list[Trade]:
    """Load all 23 hourly windows, reconciled against the tester's own stats.

    ``check_coverage`` is for the two callers that must read a tape without
    judging it: the generator that measures the reference, and tests that load a
    deliberately short one.
    """

    root = Path(sweeps_root)
    paths = _window_paths(root, strategy, risk_reward)
    trades: list[Trade] = []
    last_exits: dict[str, datetime] = {}

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
                if window not in last_exits or exit_at > last_exits[window]:
                    last_exits[window] = exit_at
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

    if check_coverage:
        coverage = read_coverage()
        shortfalls = coverage_shortfalls(strategy, last_exits, coverage)
        if shortfalls:
            raise ValueError(_coverage_error(strategy, risk_reward, shortfalls, coverage))

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
