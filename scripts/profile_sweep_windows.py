"""Standalone profile of every hourly window of one sweep tape.

Each window is traded on its own account: one MNQ per trade, fixed size (no
compounding), a notional starting balance and a round-turn commission. No firm
rules, no withdrawals, no evaluation -- this is the raw strategy, window by
window, measured with the usual retail/CTA gauges.

Writes into results/window_profiles/<name>/:
  <name>__REPORT.html        self-contained interactive report
  <name>__METRICS.csv        one row per window, every gauge
  <name>__YEARLY.csv         net P/L per window per calendar year
  <name>__MONTHLY.csv        net P/L per window per calendar month
  <name>__DAILY_EQUITY.csv   end-of-day balance per window

Usage:
  venv\\Scripts\\python.exe scripts\\profile_sweep_windows.py --strategy RR --risk-reward 1.00
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pa_milky.loader import WINDOWS, load_trades  # noqa: E402

TEMPLATE = Path(__file__).with_suffix(".html")
TRADING_DAYS_PER_YEAR = 252
# Source timestamps are Europe/Tallinn wall clock (ASSUMPTIONS.md). New York is
# seven hours behind for most of the year; the two DST changeovers each leave a
# few weeks at six or eight hours.
TALLINN_MINUS_NEW_YORK = 7
# Verdict thresholds. A t-stat of 2 is the usual "distinguishable from zero"
# bar; profit factor 1.05 separates a thin edge from commission noise.
EDGE_T_STAT = 2.0
FLAT_PROFIT_FACTOR = 1.05
VERDICT_RULE = (
    f"Edge holds: t-stat >= {EDGE_T_STAT:g} and profitable in all calendar years but one. "
    f"Flat or losing: profit factor below {FLAT_PROFIT_FACTOR:g}. "
    "Positive, unproven: everything else."
)


def read_mt5_stats(root: Path, strategy: str, risk_reward: str, window: str) -> dict:
    path = root / f"{strategy}_stats" / window / f"{window}_{risk_reward}_stats.csv"
    with path.open("r", encoding="utf-16", newline="") as handle:
        rows = [r for r in csv.DictReader(handle, delimiter="\t") if any(r.values())]
    return rows[0]


def new_york_label(window: str) -> str:
    start, end = (int(part) for part in window.split("-"))
    return f"{(start - TALLINN_MINUS_NEW_YORK) % 24:02d}-{(end - TALLINN_MINUS_NEW_YORK) % 24:02d}"


def drawdown_paths(balance: float, net: np.ndarray, mae: np.ndarray):
    """Closed-trade balances plus the worst closed and intratrade drawdowns.

    A trade's intratrade low is the balance before it plus its (clamped, gross)
    MAE, measured against the highest closed balance reached before it opened.
    """

    closed = balance + np.cumsum(net)
    before = np.concatenate([[balance], closed[:-1]])
    peak_after = np.maximum.accumulate(np.concatenate([[balance], closed]))[1:]
    peak_before = np.concatenate([[balance], peak_after[:-1]])
    closed_dd = peak_after - closed
    intra_dd = peak_before - (before + mae)
    return closed, closed_dd, np.maximum(closed_dd, intra_dd), peak_after


def verdict(metrics: dict) -> str:
    if metrics["profit_factor"] < FLAT_PROFIT_FACTOR:
        return "flat_or_losing"
    if metrics["t_stat"] >= EDGE_T_STAT and metrics["profitable_years"] >= metrics["years"] - 1:
        return "edge_holds"
    return "positive_unproven"


def expected_best_normal(count: int) -> float:
    """Expected maximum of `count` independent standard normals.

    The t-stat the best of that many zero-edge windows would show by luck.
    """

    x = np.linspace(-8, 8, 16001)
    pdf = np.exp(-x * x / 2) / math.sqrt(2 * math.pi)
    cdf = 0.5 * (1 + np.vectorize(math.erf)(x / math.sqrt(2)))
    return float(np.trapezoid(x * count * pdf * cdf ** (count - 1), x))


def spearman(a, b) -> float:
    rank_a = np.argsort(np.argsort(a)).astype(float)
    rank_b = np.argsort(np.argsort(b)).astype(float)
    return float(np.corrcoef(rank_a, rank_b)[0, 1])


def longest_run(flags) -> int:
    best = run = 0
    for flag in flags:
        run = run + 1 if flag else 0
        best = max(best, run)
    return best


def worst_losing_streak_usd(net: np.ndarray) -> float:
    worst = run = 0.0
    for value in net:
        run = run + value if value <= 0 else 0.0
        worst = min(worst, run)
    return worst


def profile_window(trades, days, day_index, months, balance, commission):
    gross = np.array([t.gross_pnl_usd for t in trades])
    net = gross - commission
    mae = np.minimum(np.array([t.mae_usd for t in trades]), 0.0)
    closed, closed_dd, equity_dd, peak_after = drawdown_paths(balance, net, mae)
    _, gross_closed_dd, gross_equity_dd, _ = drawdown_paths(balance, gross, mae)

    # End-of-day balance on the shared calendar.
    daily_pnl = np.zeros(len(days))
    monthly = defaultdict(float)
    yearly = defaultdict(float)
    for trade, value in zip(trades, net):
        exit_day = trade.exit_at.date()
        daily_pnl[day_index[exit_day]] += value
        monthly[(exit_day.year, exit_day.month)] += value
        yearly[exit_day.year] += value
    equity = balance + np.cumsum(daily_pnl)
    start_equity = np.concatenate([[balance], equity[:-1]])
    returns = daily_pnl / start_equity
    peak = np.maximum.accumulate(np.concatenate([[balance], equity]))[1:]
    underwater = equity < peak - 1e-9
    dd_pct_daily = (peak - equity) / peak * 100

    # Longest spell below a prior high, peak date to recovery (or tape end).
    longest_days, longest_from, longest_to, recovered = 0, None, None, True
    spell_start = None
    for i, below in enumerate(underwater):
        if below and spell_start is None:
            spell_start = i - 1 if i > 0 else 0
        if spell_start is not None and (not below or i == len(days) - 1):
            end = i
            length = (days[end] - days[spell_start]).days
            if length > longest_days:
                longest_days = length
                longest_from, longest_to = days[spell_start], days[end]
                recovered = not below
            spell_start = None

    years = (days[-1] - days[0]).days / 365.25
    total = float(net.sum())
    final = balance + total
    cagr = (final / balance) ** (1 / years) - 1 if final > 0 else -1.0
    wins, losses = net[net > 0], net[net <= 0]
    mean_r = returns.mean()
    std_r = returns.std(ddof=1)
    downside = math.sqrt(np.mean(np.minimum(returns, 0.0) ** 2))
    ulcer = math.sqrt(np.mean(dd_pct_daily ** 2))
    x = np.arange(len(equity))
    slope, intercept = np.polyfit(x, equity, 1)
    fit = slope * x + intercept
    r_squared = 1 - np.sum((equity - fit) ** 2) / np.sum((equity - equity.mean()) ** 2)
    max_dd_i = int(np.argmax(closed_dd))
    max_dd_pct = float(np.max(closed_dd / peak_after) * 100)
    mid = days[0] + (days[-1] - days[0]) / 2
    last_year_from = days[-1] - timedelta(days=365)
    exit_days = [t.exit_at.date() for t in trades]
    first_half = float(sum(v for d, v in zip(exit_days, net) if d <= mid))
    last_12m = float(sum(v for d, v in zip(exit_days, net) if d > last_year_from))
    monthly_values = [monthly.get(m, 0.0) for m in months]
    yearly_values = {year: yearly.get(year, 0.0) for year in range(days[0].year, days[-1].year + 1)}
    hold_minutes = [(t.exit_at - t.entry_at).total_seconds() / 60 for t in trades]
    peak_i = int(np.argmax(peak_after[: max_dd_i + 1] == peak_after[max_dd_i]))
    if peak_after[max_dd_i] == balance:
        peak_date = days[0]  # never above the start before the worst trough
    else:
        peak_date = trades[peak_i].exit_at.date()

    metrics = {
        "trades": len(trades),
        "trades_per_year": len(trades) / years,
        "win_rate_pct": len(wins) / len(net) * 100,
        "avg_win_usd": float(wins.mean()) if len(wins) else 0.0,
        "avg_loss_usd": float(losses.mean()) if len(losses) else 0.0,
        "payoff_ratio": float(wins.mean() / -losses.mean()) if len(wins) and len(losses) else math.nan,
        "profit_factor": float(wins.sum() / -losses.sum()) if len(losses) else math.inf,
        "expectancy_usd": float(net.mean()),
        "t_stat": float(net.mean() / (net.std(ddof=1) / math.sqrt(len(net)))),
        "net_profit_usd": total,
        "gross_profit_usd": float(wins.sum()),
        "gross_loss_usd": float(losses.sum()),
        "commission_usd": commission * len(trades),
        "final_balance_usd": final,
        "total_return_pct": total / balance * 100,
        "cagr_pct": cagr * 100,
        "net_per_year_usd": total / years,
        "max_dd_usd": float(closed_dd.max()),
        "max_dd_pct": max_dd_pct,
        "max_dd_peak_date": peak_date.isoformat(),
        "max_dd_trough_date": trades[max_dd_i].exit_at.date().isoformat(),
        "max_equity_dd_usd": float(equity_dd.max()),
        "lowest_balance_usd": float(min(balance, closed.min())),
        "recovery_factor": total / float(closed_dd.max()) if closed_dd.max() > 0 else math.inf,
        "calmar": (cagr * 100) / max_dd_pct if max_dd_pct > 0 else math.inf,
        "sharpe": float(mean_r / std_r * math.sqrt(TRADING_DAYS_PER_YEAR)),
        "sortino": float(mean_r / downside * math.sqrt(TRADING_DAYS_PER_YEAR)),
        "ulcer_index": ulcer,
        "martin_ratio": cagr * 100 / ulcer if ulcer > 0 else math.inf,
        "longest_dd_days": longest_days,
        "longest_dd_from": longest_from.isoformat() if longest_from else None,
        "longest_dd_to": longest_to.isoformat() if longest_to else None,
        "longest_dd_recovered": recovered,
        "time_underwater_pct": float(underwater.mean() * 100),
        "r_squared": float(r_squared),
        "max_consecutive_wins": longest_run(net > 0),
        "max_consecutive_losses": longest_run(net <= 0),
        "worst_losing_streak_usd": worst_losing_streak_usd(net),
        "best_trade_usd": float(net.max()),
        "worst_trade_usd": float(net.min()),
        "best_day_usd": float(daily_pnl.max()),
        "worst_day_usd": float(daily_pnl.min()),
        "best_month_usd": max(monthly_values),
        "worst_month_usd": min(monthly_values),
        "profitable_months_pct": sum(v > 0 for v in monthly_values) / len(monthly_values) * 100,
        "profitable_years": sum(v > 0 for v in yearly_values.values()),
        "years": len(yearly_values),
        "first_half_usd": first_half,
        "second_half_usd": total - first_half,
        "last_12m_usd": last_12m,
        "avg_hold_minutes": float(np.mean(hold_minutes)),
    }
    metrics["verdict"] = verdict(metrics)
    verification = {
        "gross_net": float(gross.sum()),
        "gross_balance_dd": float(gross_closed_dd.max()),
        "gross_equity_dd": float(gross_equity_dd.max()),
        "gross_profit_factor": float(gross[gross > 0].sum() / -gross[gross < 0].sum()),
    }
    return metrics, verification, equity, monthly_values, yearly_values


def overlapping_trades(trades) -> int:
    ordered = sorted(trades, key=lambda t: t.entry_at)
    return sum(1 for a, b in zip(ordered, ordered[1:]) if b.entry_at < a.exit_at)


def write_csv(path: Path, header, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--strategy", default="RR")
    parser.add_argument("--risk-reward", default="1.00")
    parser.add_argument("--balance", type=float, default=10_000.0)
    parser.add_argument("--commission", type=float, default=1.05,
                        help="USD per MNQ round turn (project default, ASSUMPTIONS.md)")
    parser.add_argument("--sweeps-root", default=str(ROOT / "1_sweeps"))
    args = parser.parse_args()

    sweeps = Path(args.sweeps_root)
    name = f"{args.strategy}__rr_{args.risk_reward}__balance_{int(args.balance / 1000)}k"
    out_dir = ROOT / "results" / "window_profiles" / name
    out_dir.mkdir(parents=True, exist_ok=True)

    # Validated load: row counts and P/L reconcile with every MT5 stats file,
    # and truncated (stopped-out) exports are refused.
    tape = load_trades(sweeps, strategy=args.strategy, risk_reward=args.risk_reward)
    by_window = defaultdict(list)
    for trade in tape:  # already in exit (settlement) order
        by_window[trade.window_id].append(trade)

    first = min(t.entry_at for t in tape).date()
    last = max(t.exit_at for t in tape).date()
    exit_days = {t.exit_at.date() for t in tape}
    days = [first + timedelta(days=i) for i in range((last - first).days + 1)]
    days = [d for d in days if d.weekday() < 5 or d in exit_days]
    day_index = {d: i for i, d in enumerate(days)}
    months = []
    y, m = first.year, first.month
    while (y, m) <= (last.year, last.month):
        months.append((y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)

    windows, checks = [], []
    for window in WINDOWS:
        trades = by_window[window]
        metrics, verify, equity, monthly, yearly = profile_window(
            trades, days, day_index, months, args.balance, args.commission
        )
        stats = read_mt5_stats(sweeps, args.strategy, args.risk_reward, window)
        check = {
            "window": window,
            "trades": (len(trades), int(stats["trades"])),
            "net": (round(verify["gross_net"], 2), float(stats["net_profit"])),
            "balance_dd": (round(verify["gross_balance_dd"], 2), float(stats["balance_dd"])),
            "equity_dd": (round(verify["gross_equity_dd"], 2), float(stats["equity_dd"])),
            "profit_factor": (round(verify["gross_profit_factor"], 6), round(float(stats["profit_factor"]), 6)),
            "overlapping_trades": overlapping_trades(trades),
        }
        checks.append(check)
        windows.append({
            "window": window,
            "new_york": new_york_label(window),
            "metrics": metrics,
            "equity": [round(v, 2) for v in equity],
            "monthly": [round(v, 2) for v in monthly],
            "yearly": {str(k): round(v, 2) for k, v in yearly.items()},
        })

    # Machine-readable tables.
    keys = list(windows[0]["metrics"])
    write_csv(out_dir / f"{name}__METRICS.csv", ["window", "new_york_approx"] + keys,
              [[w["window"], w["new_york"]] + [w["metrics"][k] for k in keys] for w in windows])
    years = list(windows[0]["yearly"])
    write_csv(out_dir / f"{name}__YEARLY.csv", ["window"] + years,
              [[w["window"]] + [w["yearly"][yr] for yr in years] for w in windows])
    write_csv(out_dir / f"{name}__MONTHLY.csv", ["month"] + [w["window"] for w in windows],
              [[f"{yy}-{mm:02d}"] + [w["monthly"][i] for w in windows] for i, (yy, mm) in enumerate(months)])
    write_csv(out_dir / f"{name}__DAILY_EQUITY.csv", ["date"] + [w["window"] for w in windows],
              [[d.isoformat()] + [w["equity"][i] for w in windows] for i, d in enumerate(days)])

    all_net = np.array([t.gross_pnl_usd for t in tape]) - args.commission
    positive = sum(w["metrics"]["net_profit_usd"] > 0 for w in windows)
    summary = {
        "combined_net_usd": float(all_net.sum()),
        "combined_t_stat": float(all_net.mean() / (all_net.std(ddof=1) / math.sqrt(len(all_net)))),
        "positive_windows": positive,
        # Chance of at least this many winners if every window were a coin flip.
        "positive_windows_p": sum(math.comb(len(windows), k) for k in range(positive, len(windows) + 1))
        / 2 ** len(windows),
        "expected_best_t_null": expected_best_normal(len(windows)),
        "halves_rank_correlation": spearman(
            [w["metrics"]["first_half_usd"] for w in windows],
            [w["metrics"]["second_half_usd"] for w in windows],
        ),
        "verdict_rule": VERDICT_RULE,
    }

    payload = {
        "summary": summary,
        "meta": {
            "strategy": args.strategy,
            "risk_reward": args.risk_reward,
            "balance": args.balance,
            "commission": args.commission,
            "first_day": first.isoformat(),
            "last_day": last.isoformat(),
            "years": (days[-1] - days[0]).days / 365.25,
            "trades": len(tape),
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "name": name,
        },
        "day0": days[0].isoformat(),
        "day_offsets": [(d - days[0]).days for d in days],
        "months": [f"{yy}-{mm:02d}" for yy, mm in months],
        "windows": windows,
        "checks": checks,
    }
    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("/*__DATA__*/null", json.dumps(payload, separators=(",", ":"), allow_nan=False, default=lambda o: o.item()))
    html = html.replace("__TITLE__", f"{args.strategy} windows at R:R {args.risk_reward}")
    (out_dir / f"{name}__REPORT.html").write_text(html, encoding="utf-8")

    (out_dir / f"{name}__CHECKS.json").write_text(json.dumps(checks, indent=1, default=lambda o: o.item()), encoding="utf-8")
    print(f"{args.strategy} @ {args.risk_reward}: {len(tape)} trades, {first} -> {last}, {len(days)} days")
    print(json.dumps(summary, indent=1))
    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()
