# Fixed RR/GG shortlist: historical protection and operating continuity

Design frozen 2026-09-23 before this comparison is calculated. Earlier studies
have already examined this history and the target crisis quarters. This is
an exploratory comparison, not a new holdout or prospective validation.

## Fixed candidates

- RR pair: RR r/r 0.50 and RR r/r 2.50.
- Cross-strategy pair: RR r/r 0.50 and GG r/r 1.25.
- RR triple: the RR pair plus RR r/r 1.00.
- Cross-strategy triple: the cross-strategy pair plus RR r/r 1.00.
- Four homogeneous controls: each distinct constituent alone.

Do not add settings or tune allocations after observing this run. Primary
mixtures allocate equally to each constituent. Four mixtures are small enough
to retain all of them in the operating comparison, avoiding a post-hoc winner
filter. RR and GG name strategies; r/r is the numeric risk/reward setting.

## Isolation comparison

Use all 26 complete calendar quarters, January 2020 through June 2026, with
fresh synchronized starts. Each account takes native signals while flat,
one MNQ, $1.05 commission, $1,500 headroom above a fixed starting floor.
No withdrawals, replacements, transfers, account cap or deployment sequence.
Equality at the floor fails. MAE breaches have entry-to-exit uncertainty.
Unclosed horizon trades and their full MAE remain censored.

For each portfolio record full-loss quarters, fraction of accounts failing,
partial-loss quarters and worst fraction lost. Fractions use equal constituent
weights, so adding a component does not add capital. Every member of an
identical same-start constituent group follows the same path. Complete loss
means every group has breached by quarter end, not simultaneous deaths.

Compare normalized mean quarterly P&L, mean/worst quarterly realized maximum
drawdown and the continuous January-2020-to-June-2026 path. Curves are weighted
averages; unrestricted analytical P&L continues after failure markers. They
are not realizable cash from dead accounts or exact combined intratrade equity.
Report every quarter, including crises; do not drop adverse periods or combine
outcomes into an optimized single score. Show the pair-to-triple change.

## Operating comparison

Reuse the primary operating setup from RR_FOLLOWUP: daily minimum withdrawals,
$6,800 reserve above the frozen floor, $5,000 starting purchasing cash plus
$200 monthly, monthly-current-slot replacements, two spare slots, RR 1.00
evaluations, five simultaneous evaluations and seven-day initiation spacing.
The shared cap is 20 across live PAs, reserved evaluation seats and spares.
Evaluation fees and contract sizing remain those in the saved legacy spec.
PAs have the original trailing-floor rules; $6,800 is a withdrawal threshold,
not gifted starting headroom. Start without PAs in each year 2020–2025.

Accounts retain their assigned strategy/r/r for life. New PAs fill the least
populated live group; list order breaks ties. Run every distinct assignment
order: two per pair, six per triple and one per homogeneous control, over six
starts: 120 cases. Equal target group sizes need not be exactly attainable
under the 20-slot cap or during build-up. Report actual occupancy and every
order, not merely the most favorable permutation.

Use the common event clock from all four constituent tapes in every operating
case, with trading restricted to the account's assigned constituent. The RR
1.00 evaluation tape is identical across cases. Operating runs retain the
full installed horizon through July 13, 2026, to match earlier operating work;
the partial July quarter is excluded from the isolation comparison. Compare
all orders within each start, then equally weight the six starts. Different
start horizons overlap and are not independent trials.

Record account deaths, receipts less acquisition costs, retained equity,
complete-book wipeouts, empty days after first activation, time to initial
activation, and actual group occupancy. A case that never activates is not
a continuity success. No new distance-threshold or reserve search.

## Verification

Keep the shared engine and existing sealed studies unchanged. Validate source
reconciliation/coverage and hashes; reproduce prior component markers and
pair/homogeneous curves. Independently check routing, Decimal first breaches,
weighting, P&L and drawdown bounds. In operating cases check account-specific
strategy membership, non-overlap, lifetime assignments, reserve enforcement,
cash identities and shared pipeline capacity. Reproduce the 18 previously
saved RR homogeneous operating account ledgers and economics. Preserve source,
code and output hashes, per-quarter results and per-operating-case evidence.

Reproduce:

```powershell
.\venv\Scripts\python.exe scripts/study_rr_gg_shortlist.py
```

[Findings](../../results/legacy_25k/rr_gg_shortlist/FINDINGS.md) ·
[Generated comparison](../../results/legacy_25k/rr_gg_shortlist/REPORT.generated.md)
