# Window allocation: does positive evidence select better future trades?


RR at R:R 1.00 · 2022-01-01 to 2026-07-13 · one MNQ per accepted trade · $1.05 round-turn commission. No withdrawals, account starts, resets, compounding or firm rules. All comparisons share the same evaluation dates.


## Primary comparison

The predefined primary rule earns $4,224.95 versus $32,064.75 for all windows, with $2,737.30 versus $7,017.95 maximum end-of-day drawdown. It takes 1,281 of 8,845 available trades. Assess profit, risk and exposure together; a smaller dollar drawdown alone does not establish better selection.


| Rule | Net $ | Trades | PF | $/trade | EOD DD $ | Net / EOD DD | Daily $ Sharpe | Avg active |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_windows | 32,064.75 | 8,845 | 1.09 | 3.63 | 7,017.95 | 4.57 | 1.21 | 23.00 |
| positive_expanding_quarterly | 27,985.30 | 5,924 | 1.13 | 4.72 | 4,812.55 | 5.82 | 1.38 | 16.00 |
| evidence_24m_balanced_quarterly | 4,224.95 | 1,281 | 1.09 | 3.30 | 2,737.30 | 1.54 | 0.50 | 3.12 |


## What this experiment says

The richer evidence filter does not improve this historical portfolio. Of 10 evidence variants, 0 beat all-window daily dollar Sharpe and 0 beat its recovery factor. The simple quarterly positive-P/L filter is more promising: Sharpe 1.38 versus 1.21, recovery 5.82 versus 4.57, while giving up some total profit. This qualifies the earlier observation that the simple filter lost dollar profits: dollar profit alone did not measure its risk-adjusted usefulness. Neither result establishes future performance. The primary's lower absolute drawdown largely accompanies lower activity; its profit sits at approximately the 59th percentile of random subsets with matching active-window counts. Do not tune the gates repeatedly until this same tape looks good.


## What qualifies as sufficient evidence?

Primary: quarterly review, trailing 24 months; at least 150 completed trades; positive net expectancy; PF ≥ 1.10; mean trade / monthly-cluster standard error ≥ 1.0; net profit / max closed drawdown ≥ 1.0; at least 60% of complete six-month blocks profitable (3 of 4 for 24 months); positive profit even after removing the best six-month block; at least 20 recent trades and trailing-12-month PF ≥ 0.90; current drawdown at most 75% of the lookback's worst drawdown. Every gate must pass. These are transparent research choices, not estimated optimal thresholds or proofs of an edge.


## Three states and re-entry

Active receives one contract per signal. Watch receives no allocation and continues shadow trading. Rejected also continues shadow trading: adequate history plus PF ≤ 0.95, monthly-cluster score ≤ −1.645, and at least 60% losing six-month blocks. Rejected means negative historical evidence under this rule, not proof of permanent failure or structural unsuitability. All states are recomputed at each review; there is no permanent blacklist. Watch and Rejected have the same capital treatment.


## Subsequent results by year

Profits settle on exit dates; allocation is decided at entry.


| Year | all_windows | positive_expanding_quarterly | evidence_24m_balanced_quarterly |
| --- | --- | --- | --- |
| 2022 | 6,260.35 | 8,351.15 | -1,485.25 |
| 2023 | 4,575.15 | 4,358.40 | 371.00 |
| 2024 | 12,414.45 | 6,926.15 | 92.45 |
| 2025 | 7,559.65 | 1,280.25 | 2,176.90 |
| 2026 (partial) | 1,255.15 | 7,069.35 | 3,069.85 |


## Opportunity cost of suspension

These are subsequent outcomes grouped by the state known when each trade entered. Together they reconcile to trade-all. Profits from Watch and Rejected were recorded in shadow only.


| Entry state | Trades | Subsequent net $ | $/trade | PF |
| --- | --- | --- | --- | --- |
| Active | 1,281 | 4,224.95 | 3.30 | 1.09 |
| Watch | 7,410 | 27,430.00 | 3.70 | 1.10 |
| Rejected | 154 | 409.80 | 2.66 | 1.08 |


## Which windows did the rule exclude?

The primary's 150-trade floor never admits 17–18: its trailing histories contain only 104–133 trades. That is a direct consequence of the declared rule and a bias against slower windows, not evidence that 17–18 lacks an edge. Other gates also sometimes fail for that window. This finding is retained rather than repaired after seeing its profits. Multiple gates can fail together; gate_failures.csv is diagnostic, not a causal attribution of the performance loss.


| Window | Active reviews | All reviews | All trades | Accepted | All net $ | Accepted net $ | Shadow net $ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1-2 | 0 | 19 | 334 | 0 | -24.70 | 0.00 | -24.70 |
| 2-3 | 1 | 19 | 394 | 25 | 972.30 | -44.25 | 1,016.55 |
| 3-4 | 4 | 19 | 416 | 81 | 2,370.20 | 580.45 | 1,789.75 |
| 4-5 | 1 | 19 | 384 | 14 | -658.70 | -849.20 | 190.50 |
| 5-6 | 2 | 19 | 327 | 35 | 1,106.15 | -101.75 | 1,207.90 |
| 6-7 | 4 | 19 | 398 | 76 | -862.40 | -205.30 | -657.10 |
| 7-8 | 14 | 19 | 424 | 303 | 2,747.80 | 1,755.85 | 991.95 |
| 8-9 | 2 | 19 | 449 | 55 | 1,721.05 | 312.25 | 1,408.80 |
| 9-10 | 5 | 19 | 410 | 101 | 2,658.00 | 2,406.95 | 251.05 |
| 10-11 | 6 | 19 | 444 | 114 | 3,096.30 | 702.80 | 2,393.50 |
| 11-12 | 0 | 19 | 328 | 0 | 2,184.10 | 0.00 | 2,184.10 |
| 12-13 | 0 | 19 | 388 | 0 | -2,618.90 | 0.00 | -2,618.90 |
| 13-14 | 1 | 19 | 421 | 29 | 1,241.45 | -162.95 | 1,404.40 |
| 14-15 | 3 | 19 | 394 | 70 | 3,724.80 | 102.50 | 3,622.30 |
| 15-16 | 0 | 19 | 499 | 0 | -1,745.45 | 0.00 | -1,745.45 |
| 16-17 | 4 | 19 | 610 | 125 | 1,186.50 | 948.75 | 237.75 |
| 17-18 | 0 | 19 | 266 | 0 | 6,618.20 | 0.00 | 6,618.20 |
| 18-19 | 3 | 19 | 347 | 57 | 2,039.65 | -566.35 | 2,606.00 |
| 19-20 | 3 | 19 | 350 | 57 | 2,418.00 | -1,074.85 | 3,492.85 |
| 20-21 | 7 | 19 | 378 | 139 | 5,268.10 | 420.05 | 4,848.05 |
| 21-22 | 0 | 19 | 379 | 0 | -2,865.95 | 0.00 | -2,865.95 |
| 22-23 | 0 | 19 | 416 | 0 | 901.20 | 0.00 | 901.20 |
| 23-24 | 0 | 19 | 89 | 0 | 587.05 | 0.00 | 587.05 |


## Sensitivity: publish every tested rule

Nine quarterly evidence rules span 24-month, up-to-36-month and expanding histories, with lenient, balanced and strict gates. The 36-month rule uses the available 24 months initially and reaches a full 36 months in 2023. Annual balanced-24m and annual positive-P/L rules check review cadence. The primary was fixed before this run; the best row is not promoted to a validated winner. All gates are recorded in manifest.json.


| Rule | Net $ | Trades | PF | $/trade | EOD DD $ | Net / EOD DD | Daily $ Sharpe | Avg active |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_windows | 32,064.75 | 8,845 | 1.09 | 3.63 | 7,017.95 | 4.57 | 1.21 | 23.00 |
| positive_expanding_quarterly | 27,985.30 | 5,924 | 1.13 | 4.72 | 4,812.55 | 5.82 | 1.38 | 16.00 |
| positive_expanding_annual | 24,409.85 | 5,743 | 1.11 | 4.25 | 5,264.70 | 4.64 | 1.22 | 15.57 |
| evidence_24m_lenient_quarterly | 14,754.45 | 2,581 | 1.14 | 5.72 | 3,971.90 | 3.71 | 1.02 | 6.72 |
| evidence_24m_balanced_quarterly | 4,224.95 | 1,281 | 1.09 | 3.30 | 2,737.30 | 1.54 | 0.50 | 3.12 |
| evidence_24m_strict_quarterly | 2,463.90 | 252 | 1.26 | 9.78 | 1,567.70 | 1.57 | 0.58 | 0.55 |
| evidence_36m_lenient_quarterly | 9,209.30 | 2,874 | 1.08 | 3.20 | 7,712.05 | 1.19 | 0.64 | 7.50 |
| evidence_36m_balanced_quarterly | 8,156.10 | 1,808 | 1.11 | 4.51 | 4,434.05 | 1.84 | 0.71 | 4.79 |
| evidence_36m_strict_quarterly | -653.55 | 721 | 0.97 | -0.91 | 3,495.70 | -0.19 | -0.12 | 1.85 |
| evidence_expanding_lenient_quarterly | 14,612.10 | 3,298 | 1.12 | 4.43 | 5,246.10 | 2.79 | 0.99 | 8.57 |
| evidence_expanding_balanced_quarterly | 7,630.00 | 1,880 | 1.12 | 4.06 | 3,391.45 | 2.25 | 0.74 | 5.02 |
| evidence_expanding_strict_quarterly | 3,045.10 | 988 | 1.08 | 3.08 | 4,591.70 | 0.66 | 0.37 | 2.70 |
| evidence_24m_balanced_annual | 3,636.40 | 1,022 | 1.09 | 3.56 | 2,986.55 | 1.22 | 0.46 | 2.57 |


## Exposure-matched all-window reference

For each rule, scale the all-window path to the same total realized contract-hours. This is an ex-post analytical reference with fractional contracts, not an executable or past-only sizing rule. It matches time in the market, not dollar volatility or exact capital requirements. The unscaled Sharpe and recovery factor already remain unchanged under constant positive scaling.


| Rule | All-window multiplier | Scaled all net $ | Scaled all EOD DD $ | Selected minus scaled net $ |
| --- | --- | --- | --- | --- |
| all_windows | 1.00 | 32,064.75 | 7,017.95 | 0.00 |
| positive_expanding_quarterly | 0.71 | 22,806.14 | 4,991.54 | 5,179.16 |
| evidence_24m_balanced_quarterly | 0.14 | 4,462.45 | 976.69 | -237.50 |


## Count-matched random subsets

1,000 seeded controls choose windows uniformly at every quarterly review, taking exactly the primary's number of Active windows at that date. Count does not ensure equal risk, trade frequency or holding duration. This is a conditional selection diagnostic, not a formal p-value or a second optimized strategy.


| Metric | Primary | Random 5% | Random median | Random 95% | Fraction random below primary |
| --- | --- | --- | --- | --- | --- |
| net_usd | 4,224.95 | -2,293.93 | 3,516.17 | 8,756.90 | 0.59 |
| recovery_factor | 1.54 | -0.49 | 1.06 | 4.15 | 0.63 |
| daily_dollar_sharpe | 0.50 | -0.27 | 0.40 | 0.95 | 0.61 |
| max_eod_dd_usd | 2,737.30 | 1,871.92 | 3,208.28 | 5,877.66 | 0.33 |


## Uncertainty in the profit difference

Paired circular moving-block bootstrap of subsequent monthly P/L differences, with 1-, 3- and 6-month blocks. Only full calendar months are used; the final partial month is excluded. Intervals are conditional on the realized allocation path: they do not rerun selection, correct for researcher choices, or guarantee stationary future returns. A fraction of resamples above zero is not a posterior probability of an edge.


| Reference | Block months | Observed difference $ | 95% low $ | 95% high $ | Fraction positive |
| --- | --- | --- | --- | --- | --- |
| all_windows | 1 | -27,675.95 | -47,594.33 | -6,145.08 | 0.01 |
| positive_expanding_quarterly | 1 | -23,239.40 | -36,587.72 | -8,780.80 | 0.00 |
| all_windows | 3 | -27,675.95 | -44,055.72 | -11,045.47 | 0.00 |
| positive_expanding_quarterly | 3 | -23,239.40 | -35,666.12 | -9,828.47 | 0.00 |
| all_windows | 6 | -27,675.95 | -42,961.51 | -11,945.28 | 0.00 |
| positive_expanding_quarterly | 6 | -23,239.40 | -36,098.33 | -9,706.51 | 0.00 |


## Execution-cost sensitivity

Extra round-trip costs are applied to the same accepted trades. Decisions remain frozen at the base $1.05 commission: this isolates execution sensitivity rather than changing the allocation model.


| Rule | Extra $/trade | Net $ | PF | EOD DD $ | Net / EOD DD |
| --- | --- | --- | --- | --- | --- |
| all_windows | 0 | 32,064.75 | 1.09 | 7,017.95 | 4.57 |
| all_windows | 1 | 23,219.75 | 1.07 | 7,450.60 | 3.12 |
| all_windows | 2 | 14,374.75 | 1.04 | 8,202.60 | 1.75 |
| positive_expanding_quarterly | 0 | 27,985.30 | 1.13 | 4,812.55 | 5.82 |
| positive_expanding_quarterly | 1 | 22,061.30 | 1.10 | 4,983.55 | 4.43 |
| positive_expanding_quarterly | 2 | 16,137.30 | 1.07 | 6,003.75 | 2.69 |
| evidence_24m_balanced_quarterly | 0 | 4,224.95 | 1.09 | 2,737.30 | 1.54 |
| evidence_24m_balanced_quarterly | 1 | 2,943.95 | 1.06 | 3,333.30 | 0.88 |
| evidence_24m_balanced_quarterly | 2 | 1,662.95 | 1.03 | 3,929.30 | 0.42 |


## Primary state history

Tallinn entry-hour labels. Every review uses only trades completed strictly before that timestamp. The final row is the last historical review, not a live September 2026 recommendation. decisions.csv contains every metric and failed gate for every window and every rule.


| Review | Active | Watch | Rejected |
| --- | --- | --- | --- |
| 2022-01-01T00:00:00 | 8-9 14-15 | 1-2 2-3 3-4 4-5 5-6 6-7 7-8 9-10 10-11 11-12 12-13 13-14 15-16 16-17 17-18 18-19 20-21 21-22 22-23 23-24 | 19-20 |
| 2022-04-01T00:00:00 | 2-3 6-7 8-9 10-11 | 1-2 3-4 4-5 5-6 7-8 9-10 11-12 12-13 13-14 14-15 15-16 16-17 17-18 18-19 19-20 20-21 21-22 23-24 | 22-23 |
| 2022-07-01T00:00:00 | 6-7 | 1-2 2-3 3-4 4-5 5-6 7-8 8-9 9-10 10-11 11-12 12-13 13-14 14-15 15-16 16-17 17-18 18-19 19-20 20-21 21-22 23-24 | 22-23 |
| 2022-10-01T00:00:00 | 6-7 7-8 14-15 | 1-2 2-3 3-4 4-5 5-6 8-9 9-10 10-11 11-12 12-13 13-14 15-16 16-17 17-18 18-19 19-20 20-21 21-22 23-24 | 22-23 |
| 2023-01-01T00:00:00 | 7-8 20-21 | 1-2 2-3 3-4 4-5 5-6 6-7 8-9 9-10 10-11 11-12 12-13 13-14 14-15 15-16 16-17 17-18 18-19 19-20 21-22 22-23 23-24 |  |
| 2023-04-01T00:00:00 | 5-6 6-7 7-8 20-21 | 1-2 2-3 3-4 4-5 8-9 9-10 10-11 11-12 12-13 13-14 14-15 15-16 16-17 17-18 18-19 19-20 21-22 22-23 23-24 |  |
| 2023-07-01T00:00:00 | 5-6 7-8 20-21 | 1-2 2-3 3-4 4-5 6-7 8-9 9-10 10-11 11-12 12-13 13-14 14-15 15-16 16-17 17-18 18-19 19-20 21-22 22-23 23-24 |  |
| 2023-10-01T00:00:00 | 7-8 20-21 | 1-2 2-3 3-4 4-5 5-6 6-7 8-9 10-11 11-12 12-13 13-14 14-15 15-16 16-17 17-18 18-19 19-20 21-22 22-23 23-24 | 9-10 |
| 2024-01-01T00:00:00 | 7-8 18-19 20-21 | 1-2 2-3 3-4 4-5 5-6 6-7 8-9 9-10 10-11 11-12 12-13 13-14 14-15 15-16 16-17 17-18 19-20 21-22 22-23 23-24 |  |
| 2024-04-01T00:00:00 | 3-4 7-8 18-19 20-21 | 1-2 2-3 4-5 5-6 6-7 8-9 9-10 10-11 11-12 12-13 13-14 14-15 15-16 16-17 17-18 19-20 21-22 22-23 23-24 |  |
| 2024-07-01T00:00:00 | 7-8 13-14 20-21 | 1-2 2-3 3-4 4-5 5-6 6-7 8-9 9-10 10-11 11-12 12-13 14-15 15-16 16-17 17-18 18-19 19-20 21-22 22-23 23-24 |  |
| 2024-10-01T00:00:00 | 3-4 7-8 16-17 18-19 | 1-2 2-3 4-5 5-6 6-7 8-9 9-10 10-11 11-12 12-13 13-14 14-15 15-16 17-18 19-20 20-21 21-22 22-23 23-24 |  |
| 2025-01-01T00:00:00 | 7-8 16-17 | 1-2 2-3 3-4 4-5 5-6 8-9 9-10 10-11 11-12 12-13 13-14 14-15 15-16 17-18 18-19 19-20 20-21 21-22 22-23 23-24 | 6-7 |
| 2025-04-01T00:00:00 | 7-8 16-17 | 1-2 2-3 3-4 4-5 5-6 8-9 9-10 10-11 11-12 12-13 13-14 14-15 15-16 17-18 18-19 19-20 20-21 21-22 22-23 23-24 | 6-7 |
| 2025-07-01T00:00:00 | 9-10 10-11 16-17 | 1-2 2-3 3-4 4-5 5-6 6-7 7-8 8-9 11-12 12-13 13-14 14-15 15-16 17-18 18-19 19-20 20-21 21-22 22-23 23-24 |  |
| 2025-10-01T00:00:00 | 9-10 10-11 19-20 | 1-2 2-3 3-4 4-5 5-6 6-7 7-8 8-9 11-12 12-13 13-14 14-15 15-16 16-17 17-18 18-19 20-21 21-22 22-23 23-24 |  |
| 2026-01-01T00:00:00 | 4-5 7-8 9-10 10-11 19-20 | 1-2 2-3 3-4 5-6 6-7 8-9 11-12 12-13 13-14 14-15 15-16 16-17 17-18 18-19 20-21 21-22 22-23 23-24 |  |
| 2026-04-01T00:00:00 | 3-4 7-8 9-10 10-11 14-15 19-20 | 1-2 2-3 4-5 5-6 6-7 8-9 11-12 12-13 13-14 15-16 16-17 17-18 18-19 20-21 21-22 22-23 23-24 |  |
| 2026-07-01T00:00:00 | 3-4 7-8 9-10 10-11 | 1-2 2-3 4-5 5-6 6-7 8-9 11-12 12-13 13-14 14-15 15-16 16-17 17-18 18-19 19-20 20-21 22-23 23-24 | 21-22 |


## Scope and limitations

The full tape was previously inspected, so this is a chronological historical simulation, not an untouched out-of-sample experiment. Decisions use entry-bounded lookbacks and completed-trade outcomes only; an open trade is never used early. A position admitted before a review is allowed to close naturally afterwards. History accumulates even while a window is suspended. The mean-trade score allows dependence within each calendar month, but assumes independent monthly clusters and is not adjusted for testing many windows or rules. Six-month consistency gates and the score overlap in the evidence they measure. Trades can overlap across windows; there is no account slot cap. Fixed contracts do not mean equal dollar risk. EOD and closed-trade drawdowns omit floating P/L; these exports cannot reconstruct synchronized intratrade portfolio equity. Thus this study does not establish Apex survivability or required account capacity. Daily dollar Sharpe uses weekday P/L (plus any nonzero weekend settlement), 252-day annualization, and no arbitrary notional balance. No margin, financing or additional fill model is included.


## Reproduce and audit

Run `venv\Scripts\python.exe scripts\study_window_allocation.py`. Rule specification: `scripts/window_allocation.json`. Inputs and source hashes: `manifest.json`.

- [metrics.csv](metrics.csv)
- [decisions.csv](decisions.csv)
- [primary_reviews.csv](primary_reviews.csv)
- [trade_assignments.csv](trade_assignments.csv)
- [yearly.csv](yearly.csv)
- [monthly.csv](monthly.csv)
- [daily_equity.csv](daily_equity.csv)
- [cost_stress.csv](cost_stress.csv)
- [exposure_matched.csv](exposure_matched.csv)
- [random_subsets.csv](random_subsets.csv)
- [bootstrap.csv](bootstrap.csv)
- [state_outcomes.csv](state_outcomes.csv)
- [window_outcomes.csv](window_outcomes.csv)
- [gate_failures.csv](gate_failures.csv)
- [CHECKS.json](CHECKS.json)
- [manifest.json](manifest.json)
