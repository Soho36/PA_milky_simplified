# RR–GG: reciprocal protection, with the same shared failure quarters

**GG offers historical protection against some RR failures, but the first
cross-strategy screen does not eliminate more complete-failure quarters than
the existing RR r/r 0.50 + RR r/r 2.50 benchmark.** The useful candidate band
is RR r/r 0.50 with GG r/r roughly 1.00–1.50, considering individual account
losses, drawdown and P&L together. This is an exploratory reading of the same
history, not an independently validated optimum.

The GG replacements are installed. The audit validated 6,923 effective
trade/stat pairs and replaced windows 13-14 and 16-17: 233 runs were extended
(175 and 58 respectively). Every old trade's economic values remain present.
Original files are backed up under
`outputs/sweep_backups/GG_20260922T000812-ae6c95`; staging copies are retained.
GG r/r 1.00 trade bytes are unchanged; only unused Sharpe statistics changed.
That narrow equivalence is recorded in the input-transition ledger. Extended
r/r tapes are not declared equivalent to the truncated ones. RR inputs and
the simulator are unchanged.

## What we compared

Thirteen r/r values per strategy, 0.50–3.50 by 0.25, produce 169 RR–GG pairs.
All 26 individual strategy/settings and the RR-only benchmark remain visible.
The primary test starts fresh accounts together in 26 non-overlapping quarters
from January 2020 through June 2026, with $1,500 fixed headroom, one MNQ and
$1.05 commission. There are no withdrawals, purchases, replacements or pooled
capital. The pair curve is normalized to an equal-weight one-MNQ equivalent.

| Equal-weight pair | RR failed quarters | Other failed quarters | Both fail | Mean quarter net P&L | Mean quarter realized max DD |
|---|---:|---:|---:|---:|---:|
| RR 0.50 + RR 2.50 benchmark | 5/26 | 6/26 | 3/26 | $1,181 | $1,660 |
| RR 0.50 + GG 1.00 | 5/26 | 6/26 | 3/26 | $1,008 | $1,539 |
| RR 0.50 + GG 1.25 | 5/26 | 5/26 | 3/26 | $1,082 | $1,565 |
| RR 0.50 + GG 1.50 | 5/26 | 5/26 | 3/26 | $1,075 | $1,575 |

No screened cross-strategy pair has fewer than three both-failed quarters.
For GG 1.25/1.50, the improvement is one fewer constituent failure opportunity,
not fewer complete-loss quarters. Their smaller average curve drawdown comes
with lower average P&L than the RR-only benchmark. These are descriptive
means and counts, not forecasts or independent failure probabilities.

## Different periods, in both directions

RR 0.50 + GG 1.25 has the following quarterly pattern:

| Period | RR r/r 0.50 | GG r/r 1.25 |
|---|---|---|
| April–June 2021 | Fails | Survives |
| October–December 2023 | Fails | Survives |
| January–March 2022 | Survives | Fails |
| January–March 2026 | Survives | Fails |
| April–June 2022 | Fails | Fails |
| July–September 2024 | Fails | Fails |
| April–June 2025 | Fails | Fails |

These are the same three complete-loss quarters as the RR-only benchmark.
The reciprocal quarter pattern also exists in both the earlier 2020–2022
and later 2023–June 2026 subsets. At the primary dated-episode grouping this
pair has two shared, three RR-only and three GG-only episodes. Reciprocal
exclusive episodes persist under all three period lengths and all three
grouping gaps. The distinction between three both-failed quarters and two
shared episodes arises because the May/June 2022 breaches can be separated
in time within the same quarter; widening the gap to 40 dates merges them.

## Why the lowest overlap score is not the best mixture

The generated report first sorts the predeclared episode Jaccard metric:
shared episodes divided by episodes where either component fails. RR 0.50
with GG 0.50 or GG 0.75 scores about 0.18, versus about 0.22 for the RR-only
benchmark. But the number of shared episodes stays at two; the denominator
grows because GG fails in more additional episodes. Both GG settings fail in
nine quarters, versus six for RR 2.50 and five for GG 1.25/1.50. Lower Jaccard
overlap here is not evidence of fewer clustered account losses.

The grid also shows that **RR r/r 2.50 and GG r/r 1.00 have identical primary
failed-quarter and dated-episode sets**. Different strategy names do not
automatically mean different failure regimes. RR 0.50 is doing much of the
complementary work in the candidate mixtures.

## Limits and evidence

The $6,800 fixed-headroom control has no breaches for either strategy at any
tested period length, so it cannot rank these mixtures. Shared losses remain,
and the selected pairs are not literally non-overlapping. Episode boundaries
are defined consistently across all 26 arms; adding GG can merge episodes
that were separate in an RR-only analysis. They are loss-history groupings,
not independently identified macroeconomic regimes. MAE breach times are
intervals; unclosed boundary trades remain censored.

The [generated report and charts](rr_gg_episodes__REPORT.generated.md),
[full pair screen](screen.csv), [quarter outcomes](pair_windows.csv), and
[dated episode membership](episode_membership.csv) retain all candidates.
The [independent audit](independent_audit.json) passed 18 interval-graph
reconstructions, 1,020 pair-window checks and 3,060 episode-pair checks.
The runner separately matched 676 routing sequences, checked 6,084 first
breaches with Decimal accounting, and reproduced all 3,042 prior RR markers.

The [GG installation audit](../rr_gg_input_update/input_update.json) contains
all replacement hashes and backup paths. This interpretation adds no new
simulation or unreported optimization.
