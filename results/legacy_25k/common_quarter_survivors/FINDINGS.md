# What survived the three shared failure quarters?

The full 0.01-step search found **no setting surviving all three quarters**.
There are 602 ordinary strategy/settings: 301 RR and 301 GG, r/r 0.50–3.50.
Each account starts fresh and flat at the quarter boundary with $1,500 fixed
headroom, one MNQ and $1.05 commission. Withdrawals and replacements are absent.

| Quarter | RR surviving r/r settings | GG surviving r/r settings |
|---|---|---|
| Q2 2022 | None | None |
| Q3 2024 | 0.59–0.61 and 0.77–1.21 | None |
| Q2 2025 | None | None |

This means RR settings can cover **one of the three shared failure periods**.
No ordinary setting in the available range covers the other two under the
unchanged experiment. Even combining all 602 independently funded settings
would leave no survivors by the end of those two fresh-start quarters. That
does not imply identical failure dates, or describe a mature portfolio with
different accumulated headroom.

## Survival margins matter

- RR 0.59–0.61 survives Q3 2024 with only **$4.55–$8.05** of minimum headroom.
  This narrow band is a fragile historical threshold result.
- RR 0.77–1.21 is a wider surviving band. RR 1.00 retains **$415.65** at its
  worst point in that quarter. Margins vary substantially within the band.
- RR 0.51 fails Q2 2022 by just **$0.05**, on the interval from June 30 at
  15:24:40 to 16:30:00. It is correctly a failure under the fixed rule, but
  the result should not be described as robust to small assumption changes.

No target test has an unclosed trade at its quarter boundary. Survival is
checked throughout the quarter, using MAE and net-close breaches; a later
recovery does not undo a failure. Minimum headroom is not peak drawdown.

## Covering a target quarter is not automatically a better replacement pair

The 48 surviving settings were also run across all 26 fresh-start quarters.
For example:

| RR setting | Failed quarters / 26 | Both fail with RR 2.50 | Both fail with GG 1.25 |
|---|---:|---:|---:|
| 0.59–0.61 | 4 | 3 | 3 |
| 0.82–0.85 | 5 | 3 | 3 |
| 1.00 | 7 | 4 | 3 |

For RR 0.59–0.61 and 0.82–0.85, either listed partner still produces three
shared failures: **Q2 2022, Q2 2025 and Q1 2026**. Replacing RR 0.50 with one
of these settings avoids Q3 2024 but introduces Q1 2026 as a shared failure.
It changes the failure dates without improving that pair's total count.

Adding one of these survivors as a third independently funded component to
RR 0.50 / RR 2.50, or RR 0.50 / GG 1.25, reduces their common failure set from
three quarters to **two** in this fixed-floor experiment. This statement is
a set intersection, not a tested account allocation, pooled-equity strategy
or operating policy. The surviving component's account count would determine
how much of the book remains alive.

The settings and quarters were examined on known history. A precise r/r
winner has not been independently validated. The full-band evidence and the
other failed quarters are more useful than selecting a single tiny margin.

## Separate RR1000 check

The existing, hash-verified RR1000 results also show failure in all three
quarters: recorded breach exits on April 22, 2022; August 7, 2024; and
April 4, 2025. All three cases are eligible in that study. This all-hours
tape has different entry availability and remains separate from the ordinary
602-setting grid. See the [original markers](../rr_episodes/windows.csv) and
[original manifest](../rr_episodes/manifest.json).

## Evidence

All 78 coarse-grid target cases reproduce exactly, along with 104 existing
coarse-grid contextual cases. The runner checks 2,979 distinct account paths
against the independent blocked router and Decimal first-marker calculation.
Every input tape passes reconciliation and coverage validation, with hashes
checked before and after loading. Prior studies were not rewritten.

- [Complete generated report and all survivor margins](REPORT.md)
- [All 1,806 target results](target_quarters.csv)
- [All 602 setting summaries](setting_summary.csv)
- [All-quarter context](context_quarters.csv)
- [Run manifest](manifest.json)
- [Design](../../../research/legacy_25k/COMMON_QUARTER_SURVIVORS.md)
