"""Self-contained HTML and Markdown reports for the allocation experiment."""
from html import escape
import math

import numpy as np


def fmt(value):
    if value is None:
        return "—"
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return f"{value:,}"
    if math.isinf(value):
        return "∞"
    return f"{value:,.2f}"


def tables(rows, columns):
    header = "<tr>" + "".join(f"<th>{escape(label)}</th>" for _, label in columns) + "</tr>"
    html = "<div class='scroll'><table><thead>" + header + "</thead><tbody>"
    md = "| " + " | ".join(label for _, label in columns) + " |\n"
    md += "| " + " | ".join("---" for _ in columns) + " |\n"
    for row in rows:
        cells = [fmt(row[key]) for key, _ in columns]
        html += "<tr>" + "".join(f"<td>{escape(v)}</td>" for v in cells) + "</tr>"
        md += "| " + " | ".join(v.replace("|", "/") for v in cells) + " |\n"
    return html + "</tbody></table></div>", md


def chart(paths, days, names, drawdown=False):
    colors = ["#637b92", "#cf8639", "#007f75"]
    series = []
    for name in names:
        y = np.r_[0.0, np.cumsum(paths[name])]
        if drawdown:
            y = y - np.maximum.accumulate(y)
        series.append(y)
    low = min(float(y.min()) for y in series)
    high = max(float(y.max()) for y in series)
    span = high - low or 1
    lo, hi = low - .08 * span, high + .08 * span
    def sy(y):
        return 258 - (y - lo) / (hi - lo) * 218
    svg = ["<svg viewBox='0 0 1100 310' role='img' aria-label='" +
           ("Drawdown" if drawdown else "Cumulative net profit") + " by strategy'>"]
    for value in np.linspace(low, high, 5):
        yy = sy(value)
        svg.append(f"<line x1='85' x2='1075' y1='{yy:.1f}' y2='{yy:.1f}' stroke='#dce4e9'/>")
        svg.append(f"<text x='73' y='{yy + 4:.1f}' text-anchor='end' fill='#506070' font-size='12'>${value:,.0f}</text>")
    for y, name, color in zip(series, names, colors):
        points = " ".join(f"{85 + i / (len(y) - 1) * 990:.1f},{sy(v):.1f}" for i, v in enumerate(y))
        svg.append(f"<polyline fill='none' stroke='{color}' stroke-width='2' points='{points}'/>")
    for i, d in enumerate(days):
        if (d.month == 1 and d.day == 1) or i == len(days) - 1:
            xx = 85 + (i + 1) / len(days) * 990
            svg.append(f"<text x='{xx:.1f}' y='285' text-anchor='middle' fill='#506070' font-size='12'>{d:%Y-%m}</text>")
    svg.append("</svg>")
    legend = " ".join(f"<span style='color:{c}'>● {escape(n)}</span>" for n, c in zip(names, colors))
    return "<div class='legend'>" + legend + "</div>" + "".join(svg)


def write_report(out, spec, days, metrics, paths, yearly, stress, matches, intervals,
                 random_summary, states, reviews, window_rows):
    primary = spec["primary"]
    names = ["all_windows", "positive_expanding_quarterly", primary]
    indexed = {r["arm"]: r for r in metrics}
    main = [indexed[n] for n in names]
    cols = [("arm", "Rule"), ("net_usd", "Net $"), ("trades", "Trades"),
            ("profit_factor", "PF"), ("expectancy_usd", "$/trade"),
            ("max_eod_dd_usd", "EOD DD $"), ("recovery_factor", "Net / EOD DD"),
            ("daily_dollar_sharpe", "Daily $ Sharpe"), ("average_active_windows", "Avg active")]
    html, markdown = [], []
    def section(title, prose, rows=None, columns=None):
        html.append(f"<section><h2>{escape(title)}</h2><p>{escape(prose)}</p>")
        markdown.append(f"## {title}\n\n{prose}\n")
        if rows is not None:
            h, m = tables(rows, columns)
            html.append(h)
            markdown.append(m)
        html.append("</section>")

    title = "Window allocation: does positive evidence select better future trades?"
    intro = (f"RR at R:R {spec['risk_reward']} · {days[0]} to {days[-1]} · "
             f"one MNQ per accepted trade · ${spec['commission_usd']:.2f} round-turn commission. "
             "No withdrawals, account starts, resets, compounding or firm rules. All comparisons share the same evaluation dates.")
    html.append(f"<header><div class='eyebrow'>CHRONOLOGICAL RESEARCH · EXPLORATORY</div><h1>{title}</h1><p>{escape(intro)}</p></header>")
    markdown.extend([f"# {title}\n", intro + "\n"])
    p = indexed[primary]
    b = indexed["all_windows"]
    summary = (f"The predefined primary rule earns ${p['net_usd']:,.2f} versus ${b['net_usd']:,.2f} for all windows, "
               f"with ${p['max_eod_dd_usd']:,.2f} versus ${b['max_eod_dd_usd']:,.2f} maximum end-of-day drawdown. "
               f"It takes {p['trades']:,} of {b['trades']:,} available trades. "
               "Assess profit, risk and exposure together; a smaller dollar drawdown alone does not establish better selection.")
    section("Primary comparison", summary, main, cols)
    evidence_rows = [r for r in metrics if r["arm"].startswith("evidence_")]
    better_sharpe = sum(r["daily_dollar_sharpe"] > b["daily_dollar_sharpe"] for r in evidence_rows)
    better_recovery = sum(r["recovery_factor"] > b["recovery_factor"] for r in evidence_rows)
    simple = indexed["positive_expanding_quarterly"]
    section("What this experiment says",
            f"The richer evidence filter does not improve this historical portfolio. Of {len(evidence_rows)} evidence "
            f"variants, {better_sharpe} beat all-window daily dollar Sharpe and {better_recovery} beat its recovery factor. "
            f"The simple quarterly positive-P/L filter is more promising: Sharpe {simple['daily_dollar_sharpe']:.2f} "
            f"versus {b['daily_dollar_sharpe']:.2f}, recovery {simple['recovery_factor']:.2f} versus {b['recovery_factor']:.2f}, "
            "while giving up some total profit. This qualifies the earlier observation that the simple filter lost dollar "
            "profits: dollar profit alone did not measure its risk-adjusted usefulness. Neither result establishes future "
            "performance. The primary's lower absolute drawdown largely accompanies lower activity; its profit sits at "
            f"approximately the {100 * random_summary['net_usd']['fraction_random_below_primary']:.0f}th percentile "
            "of random subsets with matching active-window counts. Do not tune the gates repeatedly until this same tape looks good.")
    html.append(chart(paths, days, names))
    html.append(chart(paths, days, names, drawdown=True))
    section("What qualifies as sufficient evidence?",
            "Primary: quarterly review, trailing 24 months; at least 150 completed trades; positive net expectancy; "
            "PF ≥ 1.10; mean trade / monthly-cluster standard error ≥ 1.0; net profit / max closed drawdown ≥ 1.0; "
            "at least 60% of complete six-month blocks profitable (3 of 4 for 24 months); positive profit even after "
            "removing the best six-month block; at least 20 recent trades and trailing-12-month PF ≥ 0.90; "
            "current drawdown at most 75% of the lookback's worst drawdown. Every gate must pass. "
            "These are transparent research choices, not estimated optimal thresholds or proofs of an edge.")
    section("Three states and re-entry",
            "Active receives one contract per signal. Watch receives no allocation and continues shadow trading. "
            "Rejected also continues shadow trading: adequate history plus PF ≤ 0.95, monthly-cluster score ≤ −1.645, "
            "and at least 60% losing six-month blocks. Rejected means negative historical evidence under this rule, "
            "not proof of permanent failure or structural unsuitability. All states are recomputed at each review; "
            "there is no permanent blacklist. Watch and Rejected have the same capital treatment.")
    year_table = []
    for year in sorted({r["year"] for r in yearly}):
        row = {"year": str(year) + (" (partial)" if any(r["year"] == year and r["partial_year"] for r in yearly) else "")}
        row.update({n: next(r["net_usd"] for r in yearly if r["year"] == year and r["arm"] == n) for n in names})
        year_table.append(row)
    section("Subsequent results by year", "Profits settle on exit dates; allocation is decided at entry.",
            year_table, [("year", "Year")] + [(n, n) for n in names])
    section("Opportunity cost of suspension", "These are subsequent outcomes grouped by the state known when each trade entered. "
            "Together they reconcile to trade-all. Profits from Watch and Rejected were recorded in shadow only.",
            [dict(state=s, **m) for s, m in states.items()],
            [("state", "Entry state"), ("trades", "Trades"), ("net_usd", "Subsequent net $"),
             ("expectancy_usd", "$/trade"), ("profit_factor", "PF")])
    section("Which windows did the rule exclude?",
            "The primary's 150-trade floor never admits 17–18: its trailing histories contain only 104–133 trades. "
            "That is a direct consequence of the declared rule and a bias against slower windows, not evidence that "
            "17–18 lacks an edge. Other gates also sometimes fail for that window. This finding is retained rather "
            "than repaired after seeing its profits. Multiple gates can fail together; gate_failures.csv is diagnostic, "
            "not a causal attribution of the performance loss.", window_rows,
            [("window", "Window"), ("active_reviews", "Active reviews"), ("reviews", "All reviews"),
             ("all_trades", "All trades"), ("selected_trades", "Accepted"),
             ("all_net_usd", "All net $"), ("selected_net_usd", "Accepted net $"), ("missed_net_usd", "Shadow net $")])
    section("Sensitivity: publish every tested rule",
            "Nine quarterly evidence rules span 24-month, up-to-36-month and expanding histories, with lenient, balanced "
            "and strict gates. The 36-month rule uses the available 24 months initially and reaches a full 36 months in 2023. "
            "Annual balanced-24m and annual positive-P/L rules check review cadence. The primary was fixed before this run; "
            "the best row is not promoted to a validated winner. All gates are recorded in manifest.json.", metrics, cols)
    section("Exposure-matched all-window reference",
            "For each rule, scale the all-window path to the same total realized contract-hours. This is an ex-post analytical "
            "reference with fractional contracts, not an executable or past-only sizing rule. It matches time in the market, "
            "not dollar volatility or exact capital requirements. The unscaled Sharpe and recovery factor already remain "
            "unchanged under constant positive scaling.", [r for r in matches if r["arm"] in names],
            [("arm", "Rule"), ("all_windows_fraction", "All-window multiplier"),
             ("scaled_all_net_usd", "Scaled all net $"), ("scaled_all_max_eod_dd_usd", "Scaled all EOD DD $"),
             ("selected_minus_scaled_all_net_usd", "Selected minus scaled net $")])
    section("Count-matched random subsets",
            f"{spec['random_subset_runs']:,} seeded controls choose windows uniformly at every quarterly review, taking "
            "exactly the primary's number of Active windows at that date. Count does not ensure equal risk, trade frequency "
            "or holding duration. This is a conditional selection diagnostic, not a formal p-value or a second optimized strategy.",
            [dict(metric=k, **v) for k, v in random_summary.items()],
            [("metric", "Metric"), ("primary", "Primary"), ("p05", "Random 5%"),
             ("median", "Random median"), ("p95", "Random 95%"),
             ("fraction_random_below_primary", "Fraction random below primary")])
    section("Uncertainty in the profit difference",
            "Paired circular moving-block bootstrap of subsequent monthly P/L differences, with 1-, 3- and 6-month blocks. "
            "Only full calendar months are used; the final partial month is excluded. Intervals are conditional on the "
            "realized allocation path: they do not rerun selection, correct for researcher choices, or guarantee stationary "
            "future returns. A fraction of resamples above zero is not a posterior probability of an edge.", intervals,
            [("reference", "Reference"), ("block_months", "Block months"),
             ("observed_difference_usd", "Observed difference $"), ("ci95_low_usd", "95% low $"),
             ("ci95_high_usd", "95% high $"), ("fraction_resamples_positive", "Fraction positive")])
    section("Execution-cost sensitivity",
            "Extra round-trip costs are applied to the same accepted trades. Decisions remain frozen at the base $1.05 "
            "commission: this isolates execution sensitivity rather than changing the allocation model.",
            [r for r in stress if r["arm"] in names],
            [("arm", "Rule"), ("extra_round_trip_cost_usd", "Extra $/trade"),
             ("net_usd", "Net $"), ("profit_factor", "PF"), ("max_eod_dd_usd", "EOD DD $"),
             ("recovery_factor", "Net / EOD DD")])
    section("Primary state history",
            "Tallinn entry-hour labels. Every review uses only trades completed strictly before that timestamp. "
            "The final row is the last historical review, not a live September 2026 recommendation. "
            "decisions.csv contains every metric and failed gate for every window and every rule.", reviews,
            [("review", "Review"), ("active", "Active"), ("watch", "Watch"), ("rejected", "Rejected")])
    section("Scope and limitations",
            "The full tape was previously inspected, so this is a chronological historical simulation, not an untouched "
            "out-of-sample experiment. Decisions use entry-bounded lookbacks and completed-trade outcomes only; an open "
            "trade is never used early. A position admitted before a review is allowed to close naturally afterwards. "
            "History accumulates even while a window is suspended. The mean-trade score allows dependence within each "
            "calendar month, but assumes independent monthly clusters and is not adjusted for testing many windows or "
            "rules. Six-month consistency gates and the score overlap in the evidence they measure. Trades can overlap "
            "across windows; there is no account slot cap. Fixed contracts do not mean equal dollar risk. "
            "EOD and closed-trade drawdowns omit floating P/L; these exports cannot reconstruct synchronized intratrade "
            "portfolio equity. Thus this study does not establish Apex survivability or required account capacity. "
            "Daily dollar Sharpe uses weekday P/L (plus any nonzero weekend settlement), 252-day annualization, "
            "and no arbitrary notional balance. No margin, financing or additional fill model is included.")
    files = ["metrics.csv", "decisions.csv", "primary_reviews.csv", "trade_assignments.csv", "yearly.csv", "monthly.csv",
             "daily_equity.csv", "cost_stress.csv", "exposure_matched.csv", "random_subsets.csv", "bootstrap.csv",
             "state_outcomes.csv", "window_outcomes.csv", "gate_failures.csv", "CHECKS.json", "manifest.json", "REPORT.md"]
    html.append("<section><h2>Reproduce and audit</h2><p><code>venv\\Scripts\\python.exe scripts\\study_window_allocation.py</code></p><ul>" +
                "".join(f"<li><a href='{f}'>{f}</a></li>" for f in files) + "</ul></section>")
    markdown.append("## Reproduce and audit\n\nRun `venv\\Scripts\\python.exe scripts\\study_window_allocation.py`. "
                    "Rule specification: `scripts/window_allocation.json`. Inputs and source hashes: `manifest.json`.\n\n" +
                    "\n".join(f"- [{f}]({f})" for f in files if f != "REPORT.md"))
    style = """body{margin:0;background:#f1f5f7;color:#172b3a;font:16px/1.6 system-ui,sans-serif}
main{max-width:1220px;margin:40px auto;padding:0 28px 50px}header{padding:28px 0 18px}h1{font-size:38px;line-height:1.15;max-width:1000px}
h2{font-size:23px;margin-top:0}p{max-width:1050px}.eyebrow{color:#007f75;font-size:12px;font-weight:750;letter-spacing:2px}
section{background:white;border:1px solid #dce4e9;border-radius:10px;padding:25px;margin:24px 0}.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:right;padding:10px 12px;border-bottom:1px solid #e4eaee;white-space:nowrap}
th:first-child,td:first-child{text-align:left}th{background:#f1f5f7}tr:hover td{background:#f5faf9}a{color:#007f75}
svg{width:100%;background:white;border-radius:8px}.legend{font-size:12px;display:flex;gap:20px;flex-wrap:wrap;margin:12px 0}code{font-size:13px}
@media(max-width:650px){main{padding:0 12px}h1{font-size:29px}section{padding:16px}}"""
    (out / "REPORT.html").write_text("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
                                     "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                                     f"<title>{title}</title><style>{style}</style></head><body><main>" +
                                     "\n".join(html) + "</main></body></html>", encoding="utf-8")
    (out / "REPORT.md").write_text("\n\n".join(markdown) + "\n", encoding="utf-8")
    (out / "START_HERE.txt").write_text(title + "\n\n" + summary + "\n\nOpen REPORT.html for the full study.\n"
                                        "The primary is predefined; all variants and audit files are retained.\n"
                                        "Historical dates only; no account-management rules or withdrawals.\n", encoding="utf-8")
