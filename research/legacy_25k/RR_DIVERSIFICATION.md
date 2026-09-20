# RR diversification: clustered account deaths

Completed findings: [RR diversification](../../results/legacy_25k/rr_diversification/rr_diversification__FINDINGS.generated.md).
The 2020 start is a separate stress case. A supplementary replay of the
previously documented March 2026 failure holds its original $5,700
daily-maximum policy and supply settings fixed; it is not part of the primary
$6,800 policy comparison and does not select new weights.

The objective is fewer large clusters of PA deaths and less interruption of
earning capacity. Net operating cash and total deaths constrain the trade-off;
neither profit maximization nor selecting precise RR weights is the objective.
Migration of the user's existing accounts is outside this study.

## Frozen design

The [profile](../../config/studies/legacy_25k_rr_diversification.json) specifies
nine homogeneous controls, including RR 1.00, and four simple equal-weight mixes.
Every PA uses one MNQ and keeps its RR for its lifetime. New accounts fill the
most underrepresented live RR group, with deterministic ties. This replenishes
depleted groups rather than silently dropping unsuccessful variants.

- **Isolation:** 20 identical, fresh PAs start together, paid at the inherited
  funded-seat price; no replacements or later purchases. This deliberately
  excludes initial balance/start-date dispersion. It does not model already
  mature accounts endowed with a reserve.
- **Operating:** $5,000 initial owner cash plus $200/month; zero seeded PAs;
  monthly growth demand and replacements consuming an unused current-month
  slot. Five concurrent evaluations, seven-day launch spacing, two desired
  spares and a shared 20-seat cap. Evaluation trading stays at RR 1.00 and three
  MNQ for every arm. Acquisition, fees, payouts and funding share one clock and
  cash ledger. This is one fixed supply policy, not an optimized pipeline.
- **Withdrawals:** daily minimum checks, retaining $31,900 balance ($6,800 above
  the frozen floor). This is earned cushion, not an endowed starting balance.
  Maximum-daily sensitivity retains the same balance threshold. No terminal
  liquidation or terminal receipt is credited.
- **History:** fresh January starts in 2020–2025; maximum-withdrawal checks for
  2020/2023/2025; MFE-first sensitivity for 2020/2023. All end on the available
  July 2026 tape. Overlapping, unequal-length histories are sensitivities, not
  independent validation or directly comparable annual returns.

## Signal identity and timing

Match signals by window plus entry timestamp, never MT5 tickets or row numbers.
RR-specific exits and extrema determine settlement and account availability.
Different RR exports have small differences in entry sets even after the
short runs are repaired. Primary results therefore replay each variant's
native exported offers; absent rows are not invented or treated as losses.
The alignment report lists those differences explicitly. This is an exported
strategy-variant experiment, not proof that every raw setup has an observed
counterfactual exit at every RR.

Exact death timestamps are **not available**: the inherited engine tests MAE/MFE
and records death at the exported exit. A longer target can delay that timestamp
without delaying the real breach. Therefore exit-timed rolling clusters are
reported alongside deaths on the same originating signal and the largest
number of death-trade intervals that could intersect a rolling window. The
interval count is a conservative possibility bound, not reconstructed intrabar
equity. MAE-first/MFE-first sensitivity tests the other inherited ambiguity.

## Measurements

For 1/5/20 observed tape trading dates, record the worst count and fraction lost
from the cohort alive at the start of the window. Accounts activated later do
not enter that denominator. Count nonoverlapping half-loss episodes only with
at least five starting accounts. Also report raw replacement demand, complete
wipeouts, days empty after the first PA activation, total deaths, surviving
accounts and net operating cash after all account/evaluation fees. Initial
pipeline startup with zero PAs is not counted as a subsequent wipeout.

Homogeneous alternatives distinguish a mixing benefit from simply choosing a
more resilient RR. A mixture must be compared with its components as well as
RR 1.00. A lower exit-timed death cluster alone cannot establish success.

## Reproduction

Run `scripts/audit_rr_sweep_updates.py --apply` once to validate and install the
replacement exports (original files are backed up). RR 1.00 trades are byte
identical; only its MT5 Sharpe statistic changed. The explicit input transition
preserves the old baseline manifests and numerical results.

Run `scripts/study_rr_diversification.py` for the frozen study. Saved input,
source and profile hashes prevent resuming a checkpoint under a changed design.
Run `scripts/audit_rr_diversification.py` to independently reconstruct the
death metrics, `scripts/study_rr_march_stress.py` for the frozen March replay,
and `scripts/summarize_rr_diversification.py` for the reader-facing findings.
The generated report and CSVs live under
`results/legacy_25k/rr_diversification/`.
