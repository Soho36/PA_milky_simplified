"""Chronological three-state allocation from sweep trades, without firm rules.

Run: .\\venv\\Scripts\\python.exe scripts\\study_window_allocation.py
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pa_milky.loader import WINDOWS, load_trades
from window_allocation_support import (
    allocation_mask, make_decisions, paired_block_bootstrap, path_metrics,
    portfolio_metrics, review_dates,
)
from window_allocation_report import write_report


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def arms(spec):
    yield "all_windows", "all", None, "balanced", 3
    for step, cadence in [(3, "quarterly"), (12, "annual")]:
        yield f"positive_expanding_{cadence}", "positive", None, "balanced", step
    for months in spec["lookbacks_months"]:
        horizon = f"{months}m" if months else "expanding"
        for preset in spec["presets"]:
            yield f"evidence_{horizon}_{preset}_quarterly", "evidence", months, preset, 3
    yield "evidence_24m_balanced_annual", "evidence", 24, "balanced", 12


def monthly_values(daily, days):
    result = defaultdict(float)
    for d, value in zip(days, daily):
        result[d.strftime("%Y-%m")] += float(value)
    return result


def random_subsets(tape, values, days, decisions, runs, rng):
    reviews = sorted({r["review"] for r in decisions})
    ks = [sum(r["state"] == "Active" for r in decisions if r["review"] == d) for d in reviews]
    periods = np.searchsorted(np.array(reviews, dtype="datetime64[us]"),
                              np.array([t.entry_at for t in tape], dtype="datetime64[us]"), side="right") - 1
    widx = np.array([WINDOWS.index(t.window_id) for t in tape])
    day_index = {d: i for i, d in enumerate(days)}
    exit_days = np.array([day_index[t.exit_at.date()] for t in tape])
    rows = []
    for trial in range(runs):
        selected = np.zeros((len(reviews), len(WINDOWS)), dtype=bool)
        for i, k in enumerate(ks):
            selected[i, rng.choice(len(WINDOWS), size=k, replace=False)] = True
        mask = selected[periods, widx]
        daily = np.bincount(exit_days[mask], weights=values[mask], minlength=len(days))
        rows.append(dict(trial=trial, **path_metrics(daily, days), trades=int(mask.sum())))
    return rows


def run(spec, sweeps_root, out):
    tape = load_trades(sweeps_root, strategy=spec["strategy"], risk_reward=spec["risk_reward"])
    first = min(t.entry_at for t in tape)
    history_start = datetime(first.year, first.month, 1)
    start = datetime.fromisoformat(spec["evaluation_start"])
    end = max(t.exit_at for t in tape) + timedelta(microseconds=1)
    if start <= history_start or start >= end:
        raise ValueError("Evaluation start must follow training data and precede tape end")
    evaluation = [t for t in tape if start <= t.entry_at < end]
    days = [start.date() + timedelta(days=i) for i in range((end.date() - start.date()).days + 1)]
    values = np.array([t.gross_pnl_usd - spec["commission_usd"] for t in evaluation])
    out.mkdir(parents=True, exist_ok=True)
    metrics, all_decisions, decision_sets, masks, paths, year_rows, stress = [], [], {}, {}, {}, [], []
    for name, mode, months, preset_name, step in arms(spec):
        dates = review_dates(start, end, step)
        decisions = make_decisions(tape, WINDOWS, dates, history_start, months,
                                  spec["presets"][preset_name], spec, mode)
        assert all(r["latest_observed_exit"] < r["review"] for r in decisions)
        decision_sets[name] = decisions
        all_decisions.extend(dict(arm=name, **r) for r in decisions)
        mask = allocation_mask(evaluation, decisions)
        masks[name] = mask
        m, daily = portfolio_metrics(evaluation, values, mask, days)
        duration_total = (end - start).total_seconds()
        counts = Counter(r["review"] for r in decisions if r["state"] == "Active")
        average_active = sum(counts[d.isoformat()] * (min(dates[i + 1], end) - d).total_seconds()
                             if i + 1 < len(dates) else counts[d.isoformat()] * (end - d).total_seconds()
                             for i, d in enumerate(dates)) / duration_total
        transitions = sum(a["state"] != b["state"] for w in WINDOWS
                          for a, b in zip([r for r in decisions if r["window"] == w],
                                          [r for r in decisions if r["window"] == w][1:]))
        metrics.append(dict(arm=name, average_active_windows=average_active, state_transitions=transitions, **m))
        paths[name] = daily
        for year in sorted({d.year for d in days}):
            year_rows.append(dict(arm=name, year=year,
                                  partial_year=year == end.year and end.date() < datetime(year, 12, 31).date(),
                                  net_usd=float(sum(v for d, v in zip(days, daily) if d.year == year))))
        for extra in spec["extra_round_trip_cost_usd"]:
            sm, _ = portfolio_metrics(evaluation, values - extra, mask, days)
            stress.append(dict(arm=name, extra_round_trip_cost_usd=extra, **sm))

    primary = spec["primary"]
    indexed = {m["arm"]: m for m in metrics}
    base = indexed["all_windows"]
    exposure_matches = []
    for name, m in indexed.items():
        fraction = m["contract_hours"] / base["contract_hours"]
        reference = path_metrics(paths["all_windows"] * fraction, days)
        exposure_matches.append(dict(arm=name, all_windows_fraction=fraction,
                                     scaled_all_net_usd=reference["net_usd"],
                                     scaled_all_max_eod_dd_usd=reference["max_eod_dd_usd"],
                                     selected_minus_scaled_all_net_usd=m["net_usd"] - reference["net_usd"]))

    month_paths = {name: monthly_values(daily, days) for name, daily in paths.items()}
    months = list(month_paths[primary])
    # Keep the incomplete last month in descriptive results; bootstrap only
    # complete calendar months, to avoid treating a stub as a full observation.
    complete_months = [m for m in months if m < end.strftime("%Y-%m")]
    intervals = []
    for block in [1, spec["bootstrap_block_months"], 6]:
        for reference in ["all_windows", "positive_expanding_quarterly"]:
            difference = [month_paths[primary][m] - month_paths[reference][m] for m in complete_months]
            ci = paired_block_bootstrap(difference, spec["bootstrap_runs"], block,
                                        np.random.default_rng(spec["seed"] + block))
            intervals.append(dict(reference=reference, block_months=block,
                                  first_month=complete_months[0], last_month=complete_months[-1], **ci))

    print("Running count-matched random subsets...", flush=True)
    random_rows = random_subsets(evaluation, values, days, decision_sets[primary],
                                 spec["random_subset_runs"], np.random.default_rng(spec["seed"]))
    random_summary = {}
    for key in ["net_usd", "recovery_factor", "daily_dollar_sharpe", "max_eod_dd_usd"]:
        vals = [r[key] for r in random_rows if r[key] is not None]
        obs = indexed[primary][key]
        random_summary[key] = dict(primary=obs, p05=float(np.quantile(vals, .05)),
                                   median=float(np.median(vals)), p95=float(np.quantile(vals, .95)),
                                   fraction_random_below_primary=float(np.mean(np.array(vals) < obs)))

    # Attribute every future trade to its state at entry, including shadows.
    states = {}
    for state in ["Active", "Watch", "Rejected"]:
        rows = [{**r, "state": "Active" if r["state"] == state else "Watch"} for r in decision_sets[primary]]
        mask = allocation_mask(evaluation, rows)
        states[state], _ = portfolio_metrics(evaluation, values, mask, days)
    assert abs(sum(m["net_usd"] for m in states.values()) - base["net_usd"]) < 1e-6
    assert sum(m["trades"] for m in states.values()) == base["trades"]

    primary_decisions = decision_sets[primary]
    window_rows, failure_rows = [], []
    for w in WINDOWS:
        decisions_w = [r for r in primary_decisions if r["window"] == w]
        in_window = np.array([t.window_id == w for t in evaluation])
        chosen = in_window & masks[primary]
        failures = Counter(k for r in decisions_w if r["state"] == "Watch" for k in r["reason"].split("|"))
        window_rows.append(dict(window=w, reviews=len(decisions_w),
                                active_reviews=sum(r["state"] == "Active" for r in decisions_w),
                                minimum_history_trades=min(r["trades"] for r in decisions_w),
                                maximum_history_trades=max(r["trades"] for r in decisions_w),
                                all_trades=int(in_window.sum()), selected_trades=int(chosen.sum()),
                                all_net_usd=float(values[in_window].sum()),
                                selected_net_usd=float(values[chosen].sum()),
                                missed_net_usd=float(values[in_window & ~masks[primary]].sum())))
        failure_rows.extend(dict(window=w, gate=k, failed_reviews=n) for k, n in sorted(failures.items()))
    reviews = sorted({r["review"] for r in primary_decisions})
    review_rows = []
    for review in reviews:
        subset = [r for r in primary_decisions if r["review"] == review]
        review_rows.append(dict(review=review, **{state.lower(): " ".join(r["window"] for r in subset if r["state"] == state)
                                                  for state in states}))
    fills = []
    for i, t in enumerate(evaluation):
        fills.append(dict(trade_key=t.trade_key, window=t.window_id, entry=t.entry_at.isoformat(),
                          exit=t.exit_at.isoformat(), net_usd=values[i],
                          **{name: int(mask[i]) for name, mask in masks.items()}))
    write_csv(out / "metrics.csv", metrics)
    write_csv(out / "decisions.csv", all_decisions)
    write_csv(out / "primary_reviews.csv", review_rows)
    write_csv(out / "window_outcomes.csv", window_rows)
    write_csv(out / "gate_failures.csv", failure_rows)
    write_csv(out / "yearly.csv", year_rows)
    write_csv(out / "cost_stress.csv", stress)
    write_csv(out / "exposure_matched.csv", exposure_matches)
    write_csv(out / "bootstrap.csv", intervals)
    write_csv(out / "random_subsets.csv", random_rows)
    write_csv(out / "state_outcomes.csv", [dict(state=s, **m) for s, m in states.items()])
    write_csv(out / "trade_assignments.csv", fills)
    write_csv(out / "monthly.csv", [dict(month=m, **{name: mp[m] for name, mp in month_paths.items()}) for m in months])
    curves = {name: np.cumsum(v) for name, v in paths.items()}
    write_csv(out / "daily_equity.csv", [dict(date=d.isoformat(), **{name: float(p[i]) for name, p in curves.items()})
                                        for i, d in enumerate(days)])
    inputs = []
    for w in WINDOWS:
        inputs.extend([sweeps_root / spec["strategy"] / w / f"{w}_{spec['risk_reward']}.csv",
                       sweeps_root / f"{spec['strategy']}_stats" / w / f"{w}_{spec['risk_reward']}_stats.csv"])
    inputs += [ROOT / "config/tape_coverage.json", ROOT / "src/pa_milky/loader.py"]
    code = [Path(__file__), Path(__file__).with_name("window_allocation_support.py"),
            Path(__file__).with_name("window_allocation_report.py")]
    manifest = dict(spec=spec, generated_utc=datetime.now(timezone.utc).isoformat(),
                    start=start.isoformat(), end_exclusive=end.isoformat(),
                    tape_trades=len(tape), evaluation_trades=len(evaluation),
                    sha256={str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p):
                            hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs + code},
                    random_summary=random_summary, assertions="Past-only exits; disjoint exhaustive state attribution; validated source tape")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False), encoding="utf-8")
    write_report(out, spec, days, metrics, paths, year_rows, stress, exposure_matches,
                 intervals, random_summary, states, review_rows, window_rows)
    checks = dict(passed=True, checks=[
        "Every training exit strictly precedes its decision timestamp",
        "Active, Watch and Rejected future trades partition the all-window trades and net P/L",
        "Every portfolio daily path sums to its accepted-trade net P/L",
        "Every cost-stress P/L equals base P/L minus extra cost times accepted trade count",
    ])
    for name, mask in masks.items():
        assert abs(float(values[mask].sum()) - indexed[name]["net_usd"]) < 1e-6
    for row in stress:
        bm = indexed[row["arm"]]
        assert abs(row["net_usd"] - (bm["net_usd"] - row["extra_round_trip_cost_usd"] * bm["trades"])) < 1e-6
    (out / "CHECKS.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    manifest["outputs_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in out.iterdir() if p.is_file() and p.name != "manifest.json"}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps({name: indexed[name] for name in ["all_windows", "positive_expanding_quarterly", primary]}, indent=2))
    print(f"Wrote {out}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=Path(__file__).with_name("window_allocation.json"))
    parser.add_argument("--sweeps-root", type=Path, default=ROOT / "1_sweeps")
    parser.add_argument("--out", type=Path, default=ROOT / "results/window_allocation/RR__rr_1.00")
    args = parser.parse_args()
    run(json.loads(args.spec.read_text(encoding="utf-8")), args.sweeps_root, args.out)


if __name__ == "__main__":
    main()
