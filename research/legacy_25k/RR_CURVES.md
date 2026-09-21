# Synchronized unrestricted RR curves and shadow failures

Frozen 2026-09-21 before calculation. This isolates strategy-path complementarity
from sequential deployment, withdrawals, account purchases and replacement supply.
No settings are altered after observing results. This is exploratory historical
analysis; previously inspected history is not an untouched validation sample.

## Inputs and exposure

Use native RR exports 0.50 through 3.50 in increments of 0.25 (13 variants).
One MNQ per variant, inherited commission, every eligible entry while flat.
Entry priority is the established window/source-row/ticket ordering. Existing
exits precede new entries at the same timestamp. Start all variants flat on
the same date; ignore signals that entered before that date. Carry a position
past the analysis horizon without crediting its future P&L or freeing its slot.

No withdrawals, fees for acquiring accounts, caps, replacement purchases or
termination of analytical paths. A negative curve remains defined; that is not
a claim that a real account could continue trading. Net P&L is credited at exit.

Compare 13 homogeneous controls, all 78 equal-weight pairs, five predeclared
larger mixtures (wide4, center4, edge4, without050, grid5), and an identical-RR1
duplicate control. Every mixture is a weighted average in one-MNQ-equivalent
units, not a sum that increases exposure with account count. Each constituent
still represents an independent one-MNQ account for failure markers. There is
no rebalancing, cross-account transfer, risk scaling or capital compounding.

## Calendar

Primary equal-duration windows start each quarter from January 2020 through
July 2025 and run twelve calendar months (end exclusive): 23 overlapping
windows. Separately show January 2020--2025 starts through the last exported
exit; the final date may be a partial session. Both designs reset all variants simultaneously. A shared
calendar uses the union of offered entry/exit dates, including zero-P&L days.
The main curves are end-of-day realized P&L; event-time realized maximum
drawdown is a separate check. Neither is mark-to-market portfolio equity.

## Curve measurements

For each variant and mixture: net P&L, realized maximum drawdown from a peak
including initial zero, underwater duration in observed trading dates and
calendar days, completed versus unrecovered drawdown episodes, and worst
1/5/20-observed-day net changes. Include daily P&L correlation, joint negative
days and overlap of constituent drawdown episodes as explanatory statistics.
Compare mixtures with RR1, every constituent, and the weighted mean of the
constituents' own maximum drawdowns. The latter measures peak-offset smoothing;
it is not proof the mixture beats the safest constituent. Report profit costs.

Summarize paired differences by window, distinguish 2020 stress windows, and
show chronology rather than a single optimized score. A simple first/second
chronological-half stability table is descriptive; neither half is unseen data.
Avoid interpreting highly overlapping windows as independent probabilities.

## Shadow failure markers

Common fixed loss budgets are $1,500 and $6,800 below the starting value.
These describe identical headroom above a fixed floor, not a fresh PA's
trailing-drawdown rule. Report each constituent's first breach independently.

- Closed-P&L breach: first accepted trade exit where cumulative net P&L is at
  or below minus the loss budget; exact on the realized settlement clock.
- Excursion breach: cumulative settled P&L before a trade plus its exported
  MAE reaches the floor, or its net close breaches. A MAE breach lies somewhere
  between entry and exit; mark that interval and the originating signal.
  An unclosed boundary trade is censored because its full MAE may occur later.
- Separately record first realized peak-to-trough drawdown of those magnitudes.
  Those are drawdown markers, not fixed-floor account failures.

Mixture failure summaries weight the separate constituent markers: fraction
ever breached, largest same-originating-signal fraction, largest recorded
1/5/20-trading-day fraction and conservative possible interval cluster. A
pooled average curve cannot save a constituent account. Report censored
survivors explicitly; never reset or replace accounts after a first breach.

MAE/MFE do not provide synchronized intratrade paths. We do not sum individual
MAEs or label realized portfolio drawdown as exact open-equity drawdown.
Source entry-set differences and common negative-outcome differences remain
visible in alignment evidence; absent counterfactual trades are not invented.

## Verification and artifacts

Hash code, profile and inputs. Compare accepted trade identities with the
existing blocked router for every start and RR. Assert duplicate RR1 equals
single RR1, independent centroid accounting, no overlap, continuation after
breaches, and horizon censoring. Independently reconstruct metrics from saved
accepted trades and curves. Save daily curves, component trade selections,
shadow markers, pair diagnostics, comparisons and static plots with units.
