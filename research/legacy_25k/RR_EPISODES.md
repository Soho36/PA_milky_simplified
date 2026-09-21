# Failure episodes and the observed RR1000 arm

Design recorded before examining episode outcomes, 2026-09-21. Historical,
exploratory follow-up; none of this history is unseen validation data.

## Account-failure experiment

Use the same 13 finite RRs, one MNQ, $1.05 commission and native while-flat
selection as RR_CURVES.md. Primary starts are non-overlapping calendar
quarters from 2020-01-01 through 2026-04-01, each ending at the next quarter.
Every account starts flat with identical $1,500 fixed headroom; record its
first excursion-or-net-close breach. Curves continue; no withdrawals,
replacements, purchases or capital pooling. $6,800 is a secondary headroom
control. Include one-month and six-month non-overlapping windows as boundary
and accumulation-horizon sensitivities. Exclude the incomplete July 2026
period from every primary and sensitivity partition.

A calendar window is an exposure opportunity, not automatically a distinct
market episode. For each partition, pool first-breach intervals across the
13 finite RRs and group nearby intervals using gaps of 5, 20 and 40 observed
trading dates. Twenty dates is the primary grouping. A gap means the number
of observed dates strictly between intervals. Use each breach's entry-to-exit
interval if its MAE crosses the floor; a close-only breach is an exact exit.
Merge transitively and retain the full span and all underlying events. This
can combine a prolonged crisis into a long episode; report that span rather
than calling every cohort failure an independent episode. No pair-specific
episode boundaries and no economic regime labels inferred from trade P&L.

For each RR pair report both-fail, only-left, only-right and neither windows;
conditional co-failure and Jaccard overlap of failed windows; event groups
shared or unique to either RR; individual failure counts and homogeneous
controls. A lack of joint failure is not necessarily temporal diversification:
if one RR never fails, there is no observed reciprocal complementarity.
Distinguish pairs with nonzero unique episodes on both sides from those
dominated by one safer constituent. Retain source dates for inspection.
Report grouping and partition sensitivities, not just the most flattering pair.

## Supplementary stress chronology

Use continuous January-2020 realized curves to display drawdowns. Highlight
periods with realized drawdown of at least $1,500 from the earned peak. These
are recurring stress observations, NOT fixed-floor account deaths. Their
overlap supplements rather than replaces the account-failure experiment.

## RR1000 handling and validation

The user states the EA flattens at 23:30. Load the separate single observed
RR1000 file and its stats with a dedicated research adapter; leave the frozen
23-window loader, source digests and earlier reports unchanged. Validate
schema, numeric values, chronology, non-overlap, stats, end coverage, stop
size, excursion limits and actual exit clocks. Export all cross-date holds
and unmatched signals rather than silently repairing them. Confirm no
observed MFE reaches 1000 times the inherited two-dollar-per-point stop risk.

The file is already a single non-overlapping trade stream, with entry-set
differences from the finite-RR window exports. Treat it as an observed
alternative strategy, not causal proof about changing TP alone. Do not
invent missed entry opportunities. If a position straddles an analysis start,
mark that RR1000 window unavailable for fresh-flat comparison, because the
counterfactual entries during its occupied interval are absent. Exclude those
windows pairwise and give each pair's eligible denominator.

RR1000 does not define the finite-RR episode boundaries. Compare it with
each RR using the same eligible windows; show its own failure dates and
where they overlap the finite-RR timeline. Do not claim its $6,800 control
has no failures without checking. Do not claim an unconditional daily-flat
rule when cross-date positions exist in the supplied tape.

## Checks and artifacts

Pin code, input files and source-study evidence. Reproduce all 13 full-2020
finite-RR daily paths and accepted trade identities against the prior study.
Check the new adapter separately; match selected trades with the original
blocked router. Independently reconstruct first breaches from saved accepted
trades, using Decimal arithmetic, and independently check pair/episode set
counts. Save windows, trades, markers, episode membership, pair comparisons,
chronology plots, validation evidence and a report. No live account action.
