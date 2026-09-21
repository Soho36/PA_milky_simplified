# RR versus GG: cross-strategy failure episodes

Design recorded 2026-09-22 before cross-strategy outcomes are calculated.
RR and GG are strategy names; r/r is the numeric risk/reward setting.
This follows the within-RR episode study, on already examined historical data.

First validate the supplied GG 13-14 and 16-17 replacement windows across
the full 0.50–3.50 grid at 0.01 increments. Verify the remaining GG windows
too, using the effective installed-plus-replacement grid. Reconcile stats,
trade fields and per-window coverage. Confirm old trades' economic values
remain present before installing with backups. Preserve the staging files
and record every old/new hash; no source-engine changes or re-sealing of
unrelated RR results is needed.

## Primary comparison

Screen 13 r/r values (0.50–3.50 at 0.25 increments) for each strategy:
169 cross-strategy equal-weight pairs plus all 26 homogeneous controls.
Include RR:0.50/RR:2.50 as an explicit within-strategy benchmark.
Do not assume signals match across strategies. Each account independently
accepts its strategy's native signals while flat, at one MNQ per trade,
with the inherited $1.05 round-trip commission. Common account starts,
equal fixed headroom and identical sizing; no withdrawals, replacements,
account cap, dynamic weighting or transfers between accounts.

Use 26 non-overlapping quarters from January 2020 to June 2026 with fresh
$1,500 headroom per account. Monthly and six-month non-overlapping partitions
and a $6,800 fixed-headroom control provide sensitivities. Count first MAE
or net-close breaches separately for each account; subsequent analytical
P&L remains defined. Unclosed boundary trades and their full MAE remain
censored. Retain native entry priority and independently verify routing.

For every pair count both-fail, RR-only, GG-only and neither periods, with
each homogeneous constituent's failure count. Report reciprocal protection
explicitly: the pair needs periods where RR survives GG and vice versa.
A rare-failing constituent can reduce overlap without evidence of two-way
diversification. Counts are descriptive, not independent probabilities.

Pool first-breach intervals across all 26 strategy/settings to form common
dated loss episodes, at gaps of 5, 20 and 40 observed trading dates (20 is
primary). Report transitive merging and long episode spans. These boundaries
can differ from the earlier 13-RR-only study because GG is now included;
compare all pairs and the RR benchmark under these same new boundaries.
Do not identify economic regimes from P&L alone. Rank primary episode Jaccard
overlap descriptively, show counts and ties, and check neighboring r/r values
and partition/gap sensitivity instead of declaring a finely tuned optimum.

## Economic and path controls

For quarter windows also save normalized equal-weight pair P&L and realized
maximum drawdown versus each constituent, and earlier/later failure counts.
Save continuous January-2020 paths and stress chronology as diagnostics.
One-MNQ sizing matches nominal capacity, not trade count, stop distance or
holding time. Lower overlap bought by a consistently losing component is
not automatically an attractive mixture. Report profitability without
silently filtering away inconvenient controls. No RR1000 arm in this study.

## Verification and delivery

Pin all source trade/stat files, coverage, GG installation evidence, scripts
and protocol. Match every quarter's accepted sequence to the existing blocked
router; independently reconstruct markers with Decimal accounting. Verify
the 13 RR quarterly results against the prior episode study. Reconstruct
episode grouping with an independent interval graph and pair counts with
sets. Save raw period outcomes, dated membership, all 169 pair comparisons,
source selection identities, charts, report and verification manifests.
