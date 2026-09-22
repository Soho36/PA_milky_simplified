# GG-to-GG failure episodes

Research entry point written 2026-09-23 to document the completed GG-only
study. This is retrospective documentation, not a newly preregistered design.
The original [saved design](../../results/legacy_25k/gg_pairs/design.json),
[report](../../results/legacy_25k/gg_pairs/gg_pairs__REPORT.md) and
[manifest](../../results/legacy_25k/gg_pairs/manifest.json) retain the executed
specification and results. GG is the strategy; r/r is its numeric risk/reward
setting. The independent RR study is documented in [RR_EPISODES.md](RR_EPISODES.md).

## Account-failure experiment

Compare 13 GG r/r values from 0.50 through 3.50 at 0.25 increments: all 78
distinct equal-weight pairs and all 13 homogeneous controls. Each account
uses native GG entries while flat, one MNQ per trade and $1.05 commission
per completed round trip. This matches nominal sizing, not actual trade
counts, holding times or stop distances.

Primary accounts start flat together in 26 non-overlapping calendar quarters
from January 2020 through June 2026. Each begins with $1,500 headroom above
a fixed failure floor. Monthly and six-month non-overlapping starts are
sensitivities; $6,800 fixed headroom is a secondary control. The incomplete
July 2026 period is excluded. There are no withdrawals, purchases,
replacements, transfers, account-cap effects or portfolio deployment rules.

Record each account's first breach independently. A breach occurs when
settled P&L before a trade plus its MAE reaches the fixed floor, or when
net P&L at exit reaches it. A MAE breach is only known to occur between entry
and exit; a close-only breach is known on the settlement clock. Positions
still open at the analysis horizon remain uncredited, with their full MAE
censored because the excursion may occur after the horizon.

Analytical P&L continues after the first failure marker. Pair curves are
equal-weight averages, not sums, and cannot rescue a component account
that has breached its own floor. These are realized P&L curves, not exact
combined intratrade equity. A fixed starting floor also differs from a
fresh PA's trailing drawdown rule.

## Failure periods and common GG episodes

Count both-fail, lower-r/r-only, higher-r/r-only and neither periods for each
pair. Report each individual setting's failure count. "Both fail" means
both first breaches occur by period end, not necessarily on the same day.
Reciprocal protection requires some periods where each component survives
the other's failure; a safer constituent alone can explain one-way results.

Pool first-breach intervals across GG settings only. The shared trading-date
calendar also uses GG only. Group intervals separated by at most 5, 20 or
40 observed trading dates; 20 is the primary grouping. A gap counts observed
dates strictly between intervals. Merging is transitive and can form long
episodes, so retain their dates and full membership. These are historical
strategy-loss episodes, not independently identified economic regimes.

RR trades, failures and RR-to-GG overlap do not determine GG episode
boundaries or GG pair selection. Cross-strategy work is separate:
[RR_GG_EPISODES.md](RR_GG_EPISODES.md).

Monthly starts reset account state; they do not simply divide the same
quarterly path into smaller reporting buckets. Failure counts across reset
horizons therefore answer different questions. Overlapping historical
information and the same previously studied dataset provide descriptive
sensitivity checks, not independent validation or future probabilities.

## Current findings

| GG setting or equal-weight pair | Failed quarters for each component | Both fail by quarter end | Lower-only / higher-only quarters |
|---|---|---:|---:|
| GG r/r 1.25 alone | 5/26 | 5/26 | Not applicable |
| GG r/r 0.50 / 1.00 | 9/26 and 6/26 | 5/26 | 4 / 1 |
| GG r/r 0.50 / 1.25 | 9/26 and 5/26 | 5/26 | 4 / 0 |
| GG r/r 1.25 / 1.50 | 5/26 and 5/26 | 5/26 | 0 / 0 |

Twenty-four of 78 pairs show reciprocal unique failed quarters, but no pair
has fewer than five both-failed quarters. GG r/r 1.25 alone also fails in
five quarters. It is a useful individual benchmark, not a proven unique
optimum. GG r/r 1.50 has the same quarterly failure set. GG 0.50/1.00 shows
partial reciprocal protection, but loses more accounts overall and has
lower mean P&L than the GG 1.25 control. No clearly preferable GG pair has
been established under these criteria.

For the five shared quarterly failures, GG 0.50/1.00 recorded exits are
0, 5, 0, 3 and 4 calendar days apart, chronologically. GG 1.25/1.50 gaps are
0, 4, 0, 0 and 1 days. These particular shared failures are not separated
by months; exact intratrade breach times remain uncertain. This observation
does not prove the same timing pattern for every GG pair. Additional
distance-threshold work was deferred at the user's request.

There are no observed $6,800 fixed-floor breaches in the tested partitions,
so that control cannot rank failure synchronization.

## Checks and artifacts

The source GG tapes include the validated replacements for windows 13-14
and 16-17. Their [installation audit](../../results/legacy_25k/rr_gg_input_update/input_update.json)
records coverage checks, original-file backups and old/new hashes.

The GG-only runner checks source hashes and reproduces 338 individual
quarterly curves and 676 first-marker results from the previously audited
evidence. It checks 2,028 pair curves against constituent P&L and drawdown
bounds, and reconstructs 1,404 episode-pair counts from membership sets.
These checks do not resolve the uncertainty in intratrade breach timing.

- [Full report](../../results/legacy_25k/gg_pairs/gg_pairs__REPORT.md)
- [All GG pair and individual summaries](../../results/legacy_25k/gg_pairs/summary.csv)
- [Failure periods](../../results/legacy_25k/gg_pairs/pair_windows.csv)
- [Episode comparisons](../../results/legacy_25k/gg_pairs/pair_episodes.csv)
- [Dated episode membership](../../results/legacy_25k/gg_pairs/episode_membership.csv)
- [Original first-breach intervals](../../results/legacy_25k/gg_pairs/windows.csv)
- [Manifest and checks](../../results/legacy_25k/gg_pairs/manifest.json)

Reproduce from the project root with the project virtual environment:

```powershell
.\venv\Scripts\python.exe scripts/study_gg_pairs.py
```

This documentation adds no new simulation and leaves the saved study sealed.
