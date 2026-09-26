"""Past-only evidence gates and fixed-size, entry-time window allocation.

All windows supply shadow observations. Scores are descriptive, not adjusted
significance tests. No account lifecycle rules or position-size optimization.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
import math

import numpy as np


def shift_months(at, count):
    month = at.year * 12 + at.month - 1 + count
    return datetime(month // 12, month % 12 + 1, 1)


def review_dates(start, end, step):
    result = []
    while start < end:
        result.append(start)
        start = shift_months(start, step)
    return result


def profit_factor(values):
    wins = sum(v for v in values if v > 0)
    losses = -sum(v for v in values if v < 0)
    return wins / losses if losses else (math.inf if wins else 0.0)


def evidence(trades, cutoff, lower, commission):
    """Only lookback entries already closed strictly before the decision count."""
    known = sorted((t for t in trades if lower <= t.entry_at and t.exit_at < cutoff),
                   key=lambda t: (t.exit_at, t.entry_at, t.trade_key))
    net = np.array([t.gross_pnl_usd - commission for t in known], dtype=float)
    count = len(net)
    total = float(net.sum())
    mean = total / count if count else 0.0
    months = review_dates(lower, cutoff, 1)
    monthly = {d: [0.0, 0] for d in months}
    for t, value in zip(known, net):
        d = datetime(t.exit_at.year, t.exit_at.month, 1)
        monthly[d][0] += float(value)
        monthly[d][1] += 1
    # Cluster-robust SE of mean trade: within-month dependence is allowed;
    # across-month independence remains an assumption of this descriptive score.
    residuals = [pnl - n * mean for pnl, n in monthly.values()]
    g = len(months)
    se = math.sqrt(g / (g - 1) * sum(r * r for r in residuals)) / count if g > 1 and count else 0.0
    score = mean / se if se > 1e-12 else 0.0
    closed = np.r_[0.0, np.cumsum(net)]
    dd = np.maximum.accumulate(closed) - closed
    max_dd, current_dd = float(dd.max()), float(dd[-1])
    blocks = []
    block_end = cutoff
    while shift_months(block_end, -6) >= lower:
        block_start = shift_months(block_end, -6)
        blocks.append(sum(pnl for d, (pnl, _) in monthly.items() if block_start <= d < block_end))
        block_end = block_start
    recent = [t.gross_pnl_usd - commission for t in known if t.exit_at >= shift_months(cutoff, -12)]
    return {
        "history_start": lower.isoformat(), "history_end_exclusive": cutoff.isoformat(),
        "history_months": g, "trades": count, "net_usd": total,
        "expectancy_usd": mean, "profit_factor": profit_factor(net),
        "cluster_score": score, "cluster_se_usd": se,
        "max_closed_dd_usd": max_dd, "current_closed_dd_usd": current_dd,
        "current_dd_fraction": current_dd / max_dd if max_dd else 0.0,
        "recovery_factor": total / max_dd if max_dd else (math.inf if total > 0 else 0.0),
        "six_month_blocks": len(blocks),
        "positive_block_fraction": sum(v > 0 for v in blocks) / len(blocks) if blocks else 0.0,
        "negative_block_fraction": sum(v < 0 for v in blocks) / len(blocks) if blocks else 0.0,
        "net_without_best_block_usd": total - max(blocks) if blocks else 0.0,
        "recent_trades": len(recent), "recent_net_usd": sum(recent),
        "recent_profit_factor": profit_factor(recent),
        "latest_observed_exit": max((t.exit_at for t in known), default=lower).isoformat(),
    }


def classify(m, preset, shared, minimum_months):
    enough = m["trades"] >= preset["min_trades"] and m["history_months"] >= minimum_months
    if (enough and m["profit_factor"] <= shared["reject_max_profit_factor"]
            and m["cluster_score"] <= shared["reject_max_cluster_score"]
            and m["negative_block_fraction"] >= shared["reject_min_negative_block_fraction"]):
        return "Rejected", "negative_expectancy_evidence"
    checks = {
        "trade_count": m["trades"] >= preset["min_trades"],
        "history_length": m["history_months"] >= minimum_months,
        "positive_expectancy": m["expectancy_usd"] > 0,
        "profit_factor": m["profit_factor"] >= preset["min_profit_factor"],
        "cluster_score": m["cluster_score"] >= preset["min_cluster_score"],
        "recovery_factor": m["recovery_factor"] >= preset["min_recovery_factor"],
        "period_consistency": m["positive_block_fraction"] >= preset["min_positive_block_fraction"],
        "best_block_removed": m["net_without_best_block_usd"] > 0,
        "recent_count": m["recent_trades"] >= shared["min_recent_trades"],
        "recent_profit_factor": m["recent_profit_factor"] >= shared["min_recent_profit_factor"],
        "current_drawdown": m["current_dd_fraction"] <= shared["max_current_dd_fraction"],
    }
    failed = [key for key, passed in checks.items() if not passed]
    return ("Watch", "|".join(failed)) if failed else ("Active", "all_gates_pass")


def make_decisions(tape, windows, dates, history_start, lookback, preset, spec, mode="evidence"):
    by_window = defaultdict(list)
    for t in tape:
        by_window[t.window_id].append(t)
    rows = []
    for cutoff in dates:
        lower = max(history_start, shift_months(cutoff, -lookback)) if lookback else history_start
        for w in windows:
            m = evidence(by_window[w], cutoff, lower, spec["commission_usd"])
            if mode == "all":
                state, reason = "Active", "benchmark_all_windows"
            elif mode == "positive":
                state, reason = ("Active", "historical_net_positive") if m["net_usd"] > 0 else ("Watch", "historical_net_nonpositive")
            else:
                state, reason = classify(m, preset, spec["shared_gates"], spec["minimum_history_months"])
            rows.append(dict(review=cutoff.isoformat(), window=w, state=state, reason=reason, **m))
    return rows


def allocation_mask(tape, decisions):
    """Eligibility is fixed at entry; later reviews never liquidate a held trade."""
    dates = sorted({r["review"] for r in decisions})
    indices = {d: i for i, d in enumerate(dates)}
    states = {(indices[r["review"]], r["window"]): r["state"] for r in decisions}
    cutoffs = np.array(dates, dtype="datetime64[us]")
    entries = np.array([t.entry_at for t in tape], dtype="datetime64[us]")
    periods = np.searchsorted(cutoffs, entries, side="right") - 1
    return np.array([p >= 0 and states.get((p, t.window_id)) == "Active" for p, t in zip(periods, tape)])


def daily_pnl(tape, values, mask, days):
    index = {d: i for i, d in enumerate(days)}
    result = np.zeros(len(days))
    for t, value, selected in zip(tape, values, mask):
        if selected:
            result[index[t.exit_at.date()]] += value
    return result


def path_metrics(daily, days):
    equity = np.cumsum(daily)
    peaks = np.maximum.accumulate(np.r_[0.0, equity])[1:]
    dd = peaks - equity
    max_dd = float(dd.max())
    longest, peak_day = 0, days[0]
    for i, day in enumerate(days):
        if dd[i] < 1e-8:
            longest = max(longest, (day - peak_day).days if i and dd[i - 1] > 1e-8 else 0)
            peak_day = day
        else:
            longest = max(longest, (day - peak_day).days)
    active_days = np.array([v for v, d in zip(daily, days) if d.weekday() < 5 or abs(v) > 1e-10])
    sd = float(active_days.std(ddof=1)) if len(active_days) > 1 else 0.0
    monthly = defaultdict(float)
    for d, value in zip(days, daily):
        monthly[d.strftime("%Y-%m")] += float(value)
    return {
        "net_usd": float(equity[-1]), "max_eod_dd_usd": max_dd,
        "recovery_factor": float(equity[-1]) / max_dd if max_dd else None,
        "daily_dollar_sharpe": float(active_days.mean()) / sd * math.sqrt(252) if sd else None,
        "longest_dd_calendar_days": longest, "ending_dd_usd": float(dd[-1]),
        "profitable_months_fraction": sum(v > 1e-8 for v in monthly.values()) / len(monthly),
        "worst_month_usd": min(monthly.values()),
    }


def portfolio_metrics(tape, values, mask, days):
    selected = [(t, v) for t, v, use in zip(tape, values, mask) if use]
    daily = daily_pnl(tape, values, mask, days)
    result = path_metrics(daily, days)
    hours = sum((t.exit_at - t.entry_at).total_seconds() / 3600 for t, _ in selected)
    settlements, events = defaultdict(float), defaultdict(int)
    for t, value in selected:
        settlements[t.exit_at] += value
        if t.exit_at > t.entry_at:
            events[t.entry_at] += 1
            events[t.exit_at] -= 1
    path = np.r_[0.0, np.cumsum([settlements[d] for d in sorted(settlements)])]
    exposure, max_exposure = 0, 0
    for at in sorted(events):
        exposure += events[at]
        max_exposure = max(max_exposure, exposure)
    n = len(selected)
    result.update(trades=n, expectancy_usd=result["net_usd"] / n if n else None,
                  profit_factor=profit_factor([v for _, v in selected]),
                  contract_hours=hours, max_concurrent_contracts=max_exposure,
                  max_closed_dd_usd=float((np.maximum.accumulate(path) - path).max()))
    return result, daily


def paired_block_bootstrap(monthly_difference, runs, block, rng):
    """Circular moving blocks; descriptive intervals conditional on fixed choices."""
    x = np.asarray(monthly_difference)
    n = len(x)
    starts = rng.integers(0, n, size=(runs, math.ceil(n / block)))
    indices = ((starts[:, :, None] + np.arange(block)) % n).reshape(runs, -1)[:, :n]
    totals = x[indices].sum(axis=1)
    low, high = np.quantile(totals, [0.025, 0.975])
    return {"observed_difference_usd": float(x.sum()), "ci95_low_usd": float(low),
            "ci95_high_usd": float(high), "fraction_resamples_positive": float(np.mean(totals > 0))}
