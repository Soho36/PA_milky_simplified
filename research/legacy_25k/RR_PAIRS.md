# Lower/higher RR pairs and allocation sensitivity

Design recorded 2026-09-21 before calculating the additional allocations.
This follows the synchronized unrestricted-curve screen; that history has
already been examined. This is a focused exploratory analysis, not fresh validation.

Use the audited paths and first-breach evidence of RR_CURVES.md unchanged.
Pair lower RRs 0.50, 0.75 and 1.00 with higher RRs 1.50 through 3.50 in
0.25 steps. Test 25%, 50% and 75% allocation to the lower RR: 81 combinations,
plus all 13 homogeneous controls. Retain all 23 equal twelve-month windows
and six supplemental full-history starts. Compare earlier twelve and later
eleven primary windows descriptively. Do not interpret overlapping windows
as independent probabilities. No fine tuning or operating policies are added.

Weights describe fractions of identical one-MNQ accounts: 25/75 means one
lower-RR seat for three higher-RR seats, normalized back to one-MNQ-equivalent
P&L. They do not resize individual positions or loss budgets. Changing weights
therefore cannot change a constituent's first breach date or whether both
constituents eventually breach. It changes portfolio P&L and fractions lost.
Keep every original position and continue every analytical curve after breach.

Primary outcomes: realized maximum drawdown, net P&L, fraction of seats with a
$1,500 fixed-floor excursion breach, same-signal concentration and possible
five-observed-day concentration. Report every-constituent breach windows,
but distinguish them from coincident deaths. Retain all three original marker
methods at both $1,500 and $6,800 budgets. The latter fixed floor had no breaches
in the source study and is expected to remain uninformative under reweighting.
Compare against RR1 and both homogeneous constituents, not only among mixes.

Save all window-level outcomes and all allocations, not only the lowest-DD
row. Show allocation and nearby-RR sensitivity. Tables highlighting the
lowest mean drawdown within each lower-RR/allocation group are in-sample
screens, not selection recommendations. Retain mean account-loss and cluster
metrics alongside drawdown so a smooth average curve cannot hide failures.

Verify source hashes and frozen source code, and preserve the original study.
Reconstruct weighted P&L and maximum drawdown independently, verify every
50/50 curve metric and breach metric against the earlier study, verify 0/100
weight endpoints and first-failure allocation invariants. Save a manifest
covering source evidence, protocol, profile, script and generated artifacts.
No MT5 session-close outcome is inferred from finite-RR trades or MAE/MFE.
