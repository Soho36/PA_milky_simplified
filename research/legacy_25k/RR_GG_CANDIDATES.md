# RR-to-GG candidates after the independent GG study

Readout dated 2026-09-23, using the existing audited 169-pair cross-strategy
screen. No new sweep, finer-grid search or distance-threshold study was run.
The methods are in [RR_GG_EPISODES.md](RR_GG_EPISODES.md); GG-only findings
are in [GG_EPISODES.md](GG_EPISODES.md).

## Why an unpaired GG setting can still help

A setting can resemble other GG settings yet encounter different failure
periods from an RR setting. Failure to establish a clearly preferable
GG-to-GG pair therefore does not rule out a useful RR-to-GG pair. Conversely,
the fact that RR 0.50 and RR 2.50 complement each other does not make them
equally suitable partners for GG.

GG r/r 1.25 is a useful individual control from the GG study, not a proven
global optimum. The existing cross-strategy grid already includes all 13 RR
partners for it and the neighboring GG r/r values.

## GG r/r 1.25 with selected RR partners

Primary evidence: 26 synchronized fresh-start quarters, January 2020–June
2026, $1,500 fixed headroom, no withdrawals or replacements. Pair P&L and
drawdown are equal-weight one-MNQ-equivalent averages.

| RR r/r paired with GG r/r 1.25 | RR failures | GG failures | Both fail | RR-only / GG-only | Mean quarter P&L | Mean quarter realized max DD |
|---|---:|---:|---:|---:|---:|---:|
| 0.50 | 5/26 | 5/26 | 3/26 | 2 / 2 | $1,082 | $1,565 |
| 1.00 | 7/26 | 5/26 | 3/26 | 4 / 2 | $1,171 | $1,690 |
| 2.50 | 6/26 | 5/26 | 5/26 | 1 / 0 | $1,396 | $1,798 |

**RR r/r 0.50 + GG r/r 1.25 is the clearest candidate here for balanced
reciprocal failure protection and lower account-loss counts.** It has fewer
complete-loss quarters than either component alone: three versus five.
Neither component survives every loss, so this is partial diversification.
RR r/r 1.00 + GG r/r 1.25 also has three complete-loss quarters, but more
individual failures and a different set of shared bad periods. In particular,
both fail in Q1 2026; RR 0.50 survives that quarter.

With RR r/r 2.50, GG r/r 1.25's entire five-quarter failure set is shared.
RR 2.50 contributes one additional failed quarter. That pair shows no
reciprocal protection at this horizon, despite its higher mean P&L.

## Dates and the existing RR-only benchmark

For RR 0.50 + GG 1.25:

- GG survives RR's failures in Q2 2021 and Q4 2023.
- RR survives GG's failures in Q1 2022 and Q1 2026.
- Both fail by the end of Q2 2022, Q3 2024 and Q2 2025.

The last three are also the complete-loss quarters of RR 0.50 + RR 2.50.
That RR-only benchmark has mean quarter P&L $1,181 and mean quarter drawdown
$1,660, versus $1,082 and $1,565 for RR 0.50 + GG 1.25. The cross-strategy
candidate has one fewer constituent failed quarter, but does not establish
better whole-book continuity than the RR-only pair.

GG r/r 1.00–1.50 is a reasonable neighborhood to retain as candidates.
No tested cross-strategy pair has fewer than three both-failed quarters.
This is a historical coarse screen, not an independently validated optimum
or a deployment recommendation for a live 20-account portfolio.

Do not rank solely by the overlap ratio. Extra GG-only failures can lower
that ratio without reducing shared failures. Inspect constituent failures,
joint failures, dated episodes, P&L and drawdown together. A both-failed
quarter does not establish same-day failures; those are separate concepts.

Evidence: [full pair screen](../../results/legacy_25k/rr_gg_episodes/screen.csv),
[quarter failure sets](../../results/legacy_25k/rr_gg_episodes/pair_windows.csv),
[original findings](../../results/legacy_25k/rr_gg_episodes/rr_gg_episodes__FINDINGS.md),
and [independent audit](../../results/legacy_25k/rr_gg_episodes/independent_audit.json).
