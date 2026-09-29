"""Attribute the simple quarterly filter's drawdown reduction; no rule tuning.

Uses the frozen allocation-study decisions and fills. Restoring exclusions is
a retrospective sensitivity experiment, not a newly selected trading policy.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date, timedelta, datetime, timezone
import hashlib
from itertools import combinations
import json
from pathlib import Path

import numpy as np

from window_allocation_support import path_metrics
from window_allocation_report import tables, chart

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results/window_allocation/RR__rr_1.00"
ARM = "positive_expanding_quarterly"


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        if not rows:
            return
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def quarter(day):
    return f"{day.year}-Q{(day.month - 1) // 3 + 1}"


def drawdown_episodes(daily, days):
    """Nonoverlapping EOD high-to-recovery episodes, including initial capital.

    Equal highs reset the peak date. The last date of a flat plateau is thus
    reported even if it is a non-trading day. Peak is excluded from loss sums.
    """
    equity = np.r_[0., np.cumsum(daily)]
    dates = [days[0] - timedelta(days=1)] + list(days)
    peak = 0
    trough = None
    episodes = []
    for i in range(1, len(equity)):
        if equity[i] >= equity[peak] - 1e-7:
            if trough is not None:
                episodes.append(dict(peak_index=peak, trough_index=trough,
                                     recovery_index=i, peak_date=dates[peak].isoformat(),
                                     trough_date=dates[trough].isoformat(), recovery_date=dates[i].isoformat(),
                                     depth_usd=float(equity[peak] - equity[trough]),
                                     duration_days=(dates[i] - dates[peak]).days, recovered=True))
            peak, trough = i, None
        else:
            if trough is None or equity[i] < equity[trough] - 1e-7:
                trough = i
    if trough is not None:
        episodes.append(dict(peak_index=peak, trough_index=trough, recovery_index=None,
                             peak_date=dates[peak].isoformat(), trough_date=dates[trough].isoformat(), recovery_date=None,
                             depth_usd=float(equity[peak] - equity[trough]),
                             duration_days=(dates[-1] - dates[peak]).days, recovered=False))
    return sorted(episodes, key=lambda r: r["depth_usd"], reverse=True)


def interval_attribution(all_daily, filtered_daily, episode):
    a, b = episode["peak_index"], episode["trough_index"]
    all_decline = -float(sum(all_daily[a:b]))
    filtered_decline = -float(sum(filtered_daily[a:b]))
    avoided = -float(sum((all_daily - filtered_daily)[a:b]))
    assert abs(all_decline - filtered_decline - avoided) < 1e-6
    return dict(all_decline_usd=all_decline, filtered_decline_usd=filtered_decline,
                excluded_loss_avoided_usd=avoided)


def restored_metrics(filtered, group_paths, groups, days, all_max_dd, original_dd):
    restored = filtered + sum((group_paths[g] for g in groups), np.zeros(len(days)))
    m = path_metrics(restored, days)
    return dict(restored_groups=" + ".join(groups), **m,
                dd_increase_vs_filter_usd=round(m["max_eod_dd_usd"] - original_dd, 2),
                dd_advantage_remaining_usd=round(all_max_dd - m["max_eod_dd_usd"], 2))


def restoration_dd_only(filtered, group_paths, groups, all_max_dd, original_dd):
    """Fast exact path recomputation for exhaustive individual-decision pairs."""
    restored = filtered + sum((group_paths[g] for g in groups), np.zeros(len(filtered)))
    equity = np.r_[0., np.cumsum(restored)]
    max_dd = float(np.max(np.maximum.accumulate(equity) - equity))
    net = float(equity[-1])
    return dict(restored_groups=" + ".join(groups), net_usd=net, max_eod_dd_usd=max_dd,
                dd_increase_vs_filter_usd=round(max_dd - original_dd, 2),
                dd_advantage_remaining_usd=round(all_max_dd - max_dd, 2),
                recovery_factor=net / max_dd if max_dd else None)


def run():
    manifest = json.loads((SOURCE / "manifest.json").read_text(encoding="utf-8"))
    inputs = ["trade_assignments.csv", "daily_equity.csv", "decisions.csv", "metrics.csv"]
    for name in inputs:
        assert hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() == manifest["outputs_sha256"][name], name
    fills = read_csv(SOURCE / "trade_assignments.csv")
    curves = read_csv(SOURCE / "daily_equity.csv")
    decisions = [r for r in read_csv(SOURCE / "decisions.csv") if r["arm"] == ARM]
    days = [date.fromisoformat(r["date"]) for r in curves]
    day_index = {d: i for i, d in enumerate(days)}
    reviews = sorted({r["review"] for r in decisions})
    decision_map = {(r["review"], r["window"]): r for r in decisions}
    review_array = np.array(reviews, dtype="datetime64[us]")
    groups = defaultdict(lambda: np.zeros(len(days)))
    quarter_paths = defaultdict(lambda: np.zeros(len(days)))
    window_paths = defaultdict(lambda: np.zeros(len(days)))
    all_daily, filtered = np.zeros(len(days)), np.zeros(len(days))
    cells = {}
    for r in decisions:
        q = quarter(date.fromisoformat(r["review"][:10]))
        cells[(q, r["window"])] = dict(quarter=q, window=r["window"], state=r["state"],
                                       history_net_usd=float(r["net_usd"]), trades=0, net_usd=0.,
                                       partial_quarter=q == quarter(days[-1]))
        assert (r["state"] == "Active") == (float(r["net_usd"]) > 0)
        assert r["latest_observed_exit"] < r["review"]
    for r in fills:
        entry = datetime.fromisoformat(r["entry"])
        idx = int(np.searchsorted(review_array, np.datetime64(entry, "us"), side="right") - 1)
        assert idx >= 0
        q = quarter(entry.date())
        w = r["window"]
        decision = decision_map[(reviews[idx], w)]
        assert int(r[ARM]) == int(decision["state"] == "Active")
        i, net = day_index[date.fromisoformat(r["exit"][:10])], float(r["net_usd"])
        all_daily[i] += net
        cells[(q, w)]["trades"] += 1
        cells[(q, w)]["net_usd"] += net
        if int(r[ARM]):
            filtered[i] += net
        else:
            groups[f"{q} / {w}"][i] += net
            quarter_paths[q][i] += net
            window_paths[w][i] += net
    np.testing.assert_allclose(np.cumsum(all_daily), [float(r["all_windows"]) for r in curves], atol=1e-7)
    np.testing.assert_allclose(np.cumsum(filtered), [float(r[ARM]) for r in curves], atol=1e-7)
    np.testing.assert_allclose(all_daily - filtered, sum(groups.values()), atol=1e-7)
    bm, fm = path_metrics(all_daily, days), path_metrics(filtered, days)
    gap = round(bm["max_eod_dd_usd"] - fm["max_eod_dd_usd"], 2)
    episodes, contributions = [], []
    for name, daily in [("all_windows", all_daily), (ARM, filtered)]:
        for rank, ep in enumerate(drawdown_episodes(daily, days), 1):
            row = dict(portfolio=name, rank=rank, **ep, **interval_attribution(all_daily, filtered, ep))
            episodes.append(row)
            if rank == 1:
                for group, values in groups.items():
                    q, w = group.split(" / ")
                    loss_avoided = -float(values[ep["peak_index"]:ep["trough_index"]].sum())
                    if abs(loss_avoided) > 1e-8:
                        contributions.append(dict(episode_portfolio=name, quarter=q, window=w,
                                                  excluded_loss_avoided_usd=loss_avoided))
                assert abs(sum(r["excluded_loss_avoided_usd"] for r in contributions if r["episode_portfolio"] == name)
                           - row["excluded_loss_avoided_usd"]) < 1e-6
    restore_args = (days, bm["max_eod_dd_usd"], fm["max_eod_dd_usd"])
    q_restore = [restored_metrics(filtered, quarter_paths, [q], *restore_args) for q in sorted(quarter_paths)]
    pair_restore = [restored_metrics(filtered, quarter_paths, pair, *restore_args)
                    for pair in combinations(sorted(quarter_paths), 2)]
    w_restore = [restored_metrics(filtered, window_paths, [w], *restore_args) for w in sorted(window_paths)]
    cell_restore = [restored_metrics(filtered, groups, [g], *restore_args) for g in sorted(groups)]
    cell_pair_restore = [restoration_dd_only(filtered, groups, pair, *restore_args[1:])
                         for pair in combinations(sorted(groups), 2)]
    for rows in [q_restore, pair_restore, w_restore, cell_restore, cell_pair_restore]:
        # Cent-rounded ties use a stable label rather than floating-point noise.
        rows.sort(key=lambda r: (-round(r["dd_increase_vs_filter_usd"], 2), r["restored_groups"]))
    quarter_rows = []
    for q in sorted({r["quarter"] for r in cells.values()}):
        c = [r for r in cells.values() if r["quarter"] == q]
        omitted = [r for r in c if r["state"] != "Active"]
        excluded_pnl = sum(r["net_usd"] for r in omitted)
        # P/L uses entry cohorts. Standalone quarter risk uses settlement dates,
        # preserving any natural crossing of a review boundary.
        indices = np.array([quarter(d) == q for d in days])
        qdays = [d for d in days if quarter(d) == q]
        qm_all, qm_filter = path_metrics(all_daily[indices], qdays), path_metrics(filtered[indices], qdays)
        quarter_rows.append(dict(quarter=q, partial_quarter=q == quarter(days[-1]),
                                  excluded_windows=len(omitted),
                                  excluded_losing_windows=sum(r["net_usd"] < -1e-7 for r in omitted),
                                  excluded_profitable_windows=sum(r["net_usd"] > 1e-7 for r in omitted),
                                  all_entry_cohort_net_usd=sum(r["net_usd"] for r in c),
                                  filtered_entry_cohort_net_usd=sum(r["net_usd"] for r in c if r["state"] == "Active"),
                                  excluded_entry_cohort_net_usd=excluded_pnl,
                                  exclusion_profit_effect_usd=-excluded_pnl,
                                  all_standalone_eod_dd_usd=qm_all["max_eod_dd_usd"],
                                  filtered_standalone_eod_dd_usd=qm_filter["max_eod_dd_usd"],
                                  standalone_dd_reduction_usd=qm_all["max_eod_dd_usd"] - qm_filter["max_eod_dd_usd"]))
    endpoints = []
    for year in range(days[0].year, days[-1].year):
        endpoints.append(date(year, 12, 31))
    endpoints += [date(days[-1].year, 3, 31), date(days[-1].year, 6, 30), days[-1]]
    truncations = []
    for endpoint in endpoints:
        if not days[0] <= endpoint <= days[-1]:
            continue
        n = day_index[endpoint] + 1
        a, f = path_metrics(all_daily[:n], days[:n]), path_metrics(filtered[:n], days[:n])
        truncations.append(dict(through=endpoint.isoformat(), all_net_usd=a["net_usd"], filtered_net_usd=f["net_usd"],
                                all_max_dd_usd=a["max_eod_dd_usd"], filtered_max_dd_usd=f["max_eod_dd_usd"],
                                dd_reduction_usd=a["max_eod_dd_usd"] - f["max_eod_dd_usd"],
                                all_recovery_factor=a["recovery_factor"], filtered_recovery_factor=f["recovery_factor"],
                                all_sharpe=a["daily_dollar_sharpe"], filtered_sharpe=f["daily_dollar_sharpe"]))
    # A constant historical scale reference separates exposure reduction from
    # selection approximately; realized contract-hours are an ex-post measure.
    metrics = {r["arm"]: r for r in read_csv(SOURCE / "metrics.csv")}
    fraction = float(metrics[ARM]["contract_hours"]) / float(metrics["all_windows"]["contract_hours"])
    scaled = path_metrics(all_daily * fraction, days)
    complete = [r for r in quarter_rows if not r["partial_quarter"]]
    summary = dict(all_windows=bm, simple_filter=fm, max_dd_reduction_usd=gap,
                   full_quarters=len(complete), full_quarters_exclusion_profitable=sum(r["exclusion_profit_effect_usd"] > 1e-7 for r in complete),
                   full_quarters_standalone_dd_lower=sum(r["standalone_dd_reduction_usd"] > 1e-7 for r in complete),
                   full_quarters_standalone_dd_higher=sum(r["standalone_dd_reduction_usd"] < -1e-7 for r in complete),
                   best_single_quarter_restore=q_restore[0], best_pair_restore=pair_restore[0],
                   best_single_decision_restore=cell_restore[0], best_two_decisions_restore=cell_pair_restore[0],
                   contract_hours_fraction=fraction, scaled_all=scaled,
                   retrospective_warning="Influence rankings use future outcomes; allocations are held fixed. No new strategy or independent validation.")
    out = SOURCE / "simple_filter_attribution"
    out.mkdir(exist_ok=True)
    outputs = {"quarters.csv": quarter_rows, "window_quarters.csv": list(cells.values()),
               "drawdown_episodes.csv": episodes, "worst_episode_contributions.csv": contributions,
               "restore_quarters.csv": q_restore, "restore_quarter_pairs.csv": pair_restore,
               "restore_windows.csv": w_restore, "restore_window_quarters.csv": cell_restore,
               "restore_window_quarter_pairs.csv": cell_pair_restore,
               "sample_endpoints.csv": truncations}
    for filename, rows in outputs.items():
        write_csv(out / filename, rows)
    (out / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    report(out, days, all_daily, filtered, summary, episodes, contributions, quarter_rows,
           q_restore, pair_restore, w_restore, cell_restore, cell_pair_restore, truncations)
    audit = dict(generated_utc=datetime.now(timezone.utc).isoformat(),
                 inputs_sha256={f: hashlib.sha256((SOURCE / f).read_bytes()).hexdigest() for f in inputs + ["manifest.json"]},
                 code_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                              [Path(__file__), Path(__file__).with_name("window_allocation_support.py"),
                               Path(__file__).with_name("window_allocation_report.py")]},
                 outputs_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()
                                 if p.is_file() and p.name != "manifest.json"},
                 checks=["Upstream artifact hashes match", "Saved masks agree with quarterly positive-P/L decisions",
                         "No decision uses an exit at or after review", "Rebuilt daily paths match original study",
                         "Excluded group paths reconcile to all minus filtered", "Worst-episode attribution reconciles"])
    (out / "manifest.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print("Wrote", out)


def report(out, days, all_daily, filtered, summary, episodes, contributions, quarters,
           q_restore, pair_restore, w_restore, cell_restore, cell_pair_restore, truncations):
    from html import escape
    title = "Why did the simple quarterly filter reduce drawdown?"
    html, md = [], [f"# {title}\n"]
    def section(title, text, rows=None, columns=None):
        html.append(f"<section><h2>{escape(title)}</h2><p>{escape(text)}</p>")
        md.append(f"## {title}\n\n{text}\n")
        if rows is not None:
            h, m = tables(rows, columns)
            html.append(h)
            md.append(m)
        html.append("</section>")
    gap = summary["max_dd_reduction_usd"]
    ba = next(r for r in episodes if r["portfolio"] == "all_windows" and r["rank"] == 1)
    fa = next(r for r in episodes if r["portfolio"] == ARM and r["rank"] == 1)
    adjustment = summary["simple_filter"]["max_eod_dd_usd"] - ba["filtered_decline_usd"]
    section("The two maximum drawdowns have different dates",
            f"All windows: ${ba['depth_usd']:,.2f}, {ba['peak_date']} to {ba['trough_date']}. "
            f"Simple filter: ${fa['depth_usd']:,.2f}, {fa['peak_date']} to {fa['trough_date']}. "
            f"The headline difference is ${gap:,.2f}. During the all-window worst interval, exclusions avoided "
            f"${ba['excluded_loss_avoided_usd']:,.2f} and the filtered path declined ${ba['filtered_decline_usd']:,.2f}. "
            f"The headline reduction equals that avoided loss minus ${adjustment:,.2f}, the amount by which the "
            "filter's separate worst episode exceeds its decline on those same dates. Maximum DD is not additive.")
    html.append(chart({"all_windows": all_daily, ARM: filtered}, days, ["all_windows", ARM], drawdown=True))
    best = q_restore[0]
    section("Repeated protection versus concentration",
            f"Of {summary['full_quarters']} complete quarters, exclusions improved net profit in "
            f"{summary['full_quarters_exclusion_profitable']} and lowered standalone quarterly drawdown in "
            f"{summary['full_quarters_standalone_dd_lower']}; they raised quarterly drawdown in "
            f"{summary['full_quarters_standalone_dd_higher']}. The partial final quarter is reported separately. "
            f"The largest single-quarter restoration is {best['restored_groups']}: putting those excluded trades back "
            f"raises full-path max DD to ${best['max_eod_dd_usd']:,.2f}, leaving ${best['dd_advantage_remaining_usd']:,.2f} "
            "of the headline DD advantage. This is retrospective influence, not evidence that we could identify the influential quarter in advance.")
    prior = next(r for r in truncations if r["through"] == f"{days[-1].year - 1}-12-31")
    section("Interpretation",
            "The filter repeatedly lowered absolute quarterly risk, but its full-sample maximum-DD advantage depends "
            "on avoiding the joint losses of several windows in one late stress quarter. That is a concentration warning, "
            "not proof of luck: protection also occurred in earlier drawdowns. "
            f"Through {prior['through']}, profit/DD was {prior['filtered_recovery_factor']:.2f} for the filter versus "
            f"{prior['all_recovery_factor']:.2f} for all windows. The final profit/DD ranking therefore depends on "
            "the later part of the sample. Smaller exposure explains a substantial part of smaller absolute DD. "
            "The evidence supports further validation of a risk/profit trade-off, not a confident claim of durable window-selection skill.")
    fraction = summary["contract_hours_fraction"]
    section("How much is simply lower exposure?",
            f"The filtered book uses {fraction:.1%} of all-window contract-hours. Scaling all windows by that same "
            f"constant factor gives ${summary['scaled_all']['max_eod_dd_usd']:,.2f} maximum DD, versus "
            f"${summary['simple_filter']['max_eod_dd_usd']:,.2f} for the filter. This fractional-contract, ex-post "
            "reference is not an executable sizing rule or an exact volatility match. It prevents interpreting every "
            "dollar of the unscaled drawdown reduction as selection skill.")
    episode_cols = [("portfolio", "Episode source"), ("rank", "Rank"), ("peak_date", "Peak"),
                    ("trough_date", "Trough"), ("all_decline_usd", "All decline $"),
                    ("filtered_decline_usd", "Filter decline $"), ("excluded_loss_avoided_usd", "Loss avoided $")]
    section("Largest episodes compared on identical dates",
            "Each row fixes the source portfolio's peak and trough, then measures both books over exactly those dates. "
            "Negative decline means a net gain. Negative loss avoided means exclusion hurt. Dates denote end-of-day "
            "closed balances; equal-high plateaus use their last date, including weekends. Top five episodes per book "
            "are shown; the CSV contains every nonoverlapping high-to-recovery episode.",
            [r for r in episodes if r["rank"] <= 5], episode_cols)
    section("Windows responsible during the all-window worst drawdown",
            "This decomposition is additive on the fixed all-window peak-to-trough interval. It is not an additive "
            "decomposition of the difference between two different portfolio maxima. Quarter is the decision/entry quarter.",
            sorted([r for r in contributions if r["episode_portfolio"] == "all_windows"],
                   key=lambda r: r["excluded_loss_avoided_usd"], reverse=True),
            [("quarter", "Decision quarter"), ("window", "Window"), ("excluded_loss_avoided_usd", "Loss avoided $")])
    section("Every quarter, including opportunity cost",
            "Net P/L groups trades by entry quarter and follows them to their natural exit. Quarterly drawdowns instead "
            "use calendar-quarter settlements and reset the reference balance at quarter start. They are useful repeated "
            "risk observations, but do not sum to full-path maximum DD. The two views can differ at a quarter boundary.", quarters,
            [("quarter", "Quarter"), ("partial_quarter", "Partial"), ("excluded_windows", "OFF windows"),
             ("excluded_entry_cohort_net_usd", "Shadow net $"), ("exclusion_profit_effect_usd", "Profit effect $"),
             ("all_standalone_eod_dd_usd", "All DD $"), ("filtered_standalone_eod_dd_usd", "Filter DD $"),
             ("standalone_dd_reduction_usd", "DD reduction $")])
    restore_cols = [("restored_groups", "Restored exclusions"), ("net_usd", "Net $"),
                    ("max_eod_dd_usd", "Max DD $"), ("dd_increase_vs_filter_usd", "DD increase $"),
                    ("dd_advantage_remaining_usd", "DD advantage left $"), ("recovery_factor", "Profit / DD")]
    section("Restore one quarter's excluded trades",
            "All original filter decisions remain fixed; restore only the omitted trades admitted by that entry-quarter "
            "decision. Recompute the entire portfolio path and its worst DD. This keeps subsequent shadow learning "
            "unchanged. Effects overlap and must not be added across rows. Every quarter is shown.", q_restore, restore_cols)
    section("Restore two quarters together",
            "Every pair was evaluated, without retuning the trading rule. The ten largest DD increases are shown, "
            "with all pairs in restore_quarter_pairs.csv. Rankings are hindsight concentration diagnostics.", pair_restore[:10], restore_cols)
    section("Restore one window throughout the sample",
            "Turn on the chosen window in every quarter when the original rule excluded it. All other allocations remain fixed. "
            "This assesses whether the result depends heavily on a particular window.", w_restore, restore_cols)
    section("Restore one window-quarter decision",
            "Top ten influential individual exclusions; every observed excluded window-quarter with trades is saved in "
            "restore_window_quarters.csv. An increase greater than the original advantage can occur because the "
            "counterfactual's peak and trough change.", cell_restore[:10], restore_cols)
    section("Could just two individual exclusions explain it?",
            f"All {len(cell_pair_restore):,} pairs of observed excluded window-quarter decisions were restored and their "
            "full paths recomputed. This is distinct from restoring two entire quarters. The top ten pairs follow; "
            "restore_window_quarter_pairs.csv retains every pair. These exhaustive hindsight rankings are influence diagnostics only.",
            cell_pair_restore[:10], restore_cols)
    section("Does the result depend on the end date?",
            "Recalculate expanding results through each historical endpoint, keeping exactly the same decisions. "
            "These are sensitivity views, not independent samples.", truncations,
            [("through", "Through"), ("all_net_usd", "All net $"), ("filtered_net_usd", "Filter net $"),
             ("all_max_dd_usd", "All DD $"), ("filtered_max_dd_usd", "Filter DD $"),
             ("dd_reduction_usd", "DD reduction $"), ("all_recovery_factor", "All profit/DD"),
             ("filtered_recovery_factor", "Filter profit/DD")])
    section("Limits and reproducibility",
            "Same RR=1.00 tape and $1.05 round-trip commission as the allocation study; January 2022 through July 2026. "
            "No withdrawals, restarts, position scaling or firm rules. This is closed-balance/EOD attribution, not "
            "intratrade mark-to-market risk or Apex failure attribution. No parameters were optimized here. "
            "Restoration changes allocation only, not trade outcomes, costs per trade, or future shadow decisions. "
            "The data has already been examined: neither repeated success nor a concentration finding establishes "
            "future causality or proves luck. Source hashes, decision masks and daily curves are checked against the "
            "original saved study. Reproduce with venv\\Scripts\\python.exe scripts\\study_window_allocation_attribution.py.")
    links = sorted([p.name for p in out.glob("*.csv")]) + ["summary.json", "manifest.json", "REPORT.md"]
    html.append("<section><h2>Audit files</h2><ul>" + "".join(f"<li><a href='{f}'>{f}</a></li>" for f in links) + "</ul></section>")
    md.append("## Audit files\n\n" + "\n".join(f"- [{f}]({f})" for f in links if f != "REPORT.md"))
    css = "body{background:#f2f6f8;color:#183044;font:16px/1.6 system-ui;margin:0}main{max-width:1250px;margin:35px auto;padding:0 24px}h1{font-size:35px;line-height:1.2}h2{font-size:23px}section{background:white;padding:24px;border:1px solid #dde5ea;border-radius:10px;margin:20px 0}.scroll{overflow:auto}table{border-collapse:collapse;font-size:13px;width:100%}td,th{padding:9px;border-bottom:1px solid #e3e9ee;text-align:right;white-space:nowrap}th{background:#f2f6f8}td:first-child,th:first-child{text-align:left}svg{width:100%;background:white}.legend{font-size:13px;display:flex;gap:20px}a{color:#007f75}"
    (out / "REPORT.html").write_text("<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>" +
                                     f"<title>{title}</title><style>{css}</style></head><body><main><h1>{title}</h1>" +
                                     "".join(html) + "</main></body></html>", encoding="utf-8")
    (out / "REPORT.md").write_text("\n\n".join(md) + "\n", encoding="utf-8")
    (out / "START_HERE.txt").write_text(title + "\n\nOpen REPORT.html or REPORT.md.\n"
                                        "Fixed original decisions; retrospective quarter/window restoration diagnostics.\n"
                                        "No new filter or account-management assumptions.\n", encoding="utf-8")


if __name__ == "__main__":
    run()
