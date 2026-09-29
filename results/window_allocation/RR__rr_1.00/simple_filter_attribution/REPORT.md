# Why did the simple quarterly filter reduce drawdown?


## The two maximum drawdowns have different dates

All windows: $7,017.95, 2026-02-11 to 2026-03-27. Simple filter: $4,812.55, 2025-02-23 to 2025-04-04. The headline difference is $2,205.40. During the all-window worst interval, exclusions avoided $3,257.90 and the filtered path declined $3,760.05. The headline reduction equals that avoided loss minus $1,052.50, the amount by which the filter's separate worst episode exceeds its decline on those same dates. Maximum DD is not additive.


## Repeated protection versus concentration

Of 18 complete quarters, exclusions improved net profit in 8 and lowered standalone quarterly drawdown in 15; they raised quarterly drawdown in 3. The partial final quarter is reported separately. The largest single-quarter restoration is 2026-Q1: putting those excluded trades back raises full-path max DD to $7,017.95, leaving $-0.00 of the headline DD advantage. This is retrospective influence, not evidence that we could identify the influential quarter in advance.


## Interpretation

The filter repeatedly lowered absolute quarterly risk, but its full-sample maximum-DD advantage depends on avoiding the joint losses of several windows in one late stress quarter. That is a concentration warning, not proof of luck: protection also occurred in earlier drawdowns. Through 2025-12-31, profit/DD was 4.35 for the filter versus 5.65 for all windows. The final profit/DD ranking therefore depends on the later part of the sample. Smaller exposure explains a substantial part of smaller absolute DD. The evidence supports further validation of a risk/profit trade-off, not a confident claim of durable window-selection skill.


## How much is simply lower exposure?

The filtered book uses 71.1% of all-window contract-hours. Scaling all windows by that same constant factor gives $4,991.54 maximum DD, versus $4,812.55 for the filter. This fractional-contract, ex-post reference is not an executable sizing rule or an exact volatility match. It prevents interpreting every dollar of the unscaled drawdown reduction as selection skill.


## Largest episodes compared on identical dates

Each row fixes the source portfolio's peak and trough, then measures both books over exactly those dates. Negative decline means a net gain. Negative loss avoided means exclusion hurt. Dates denote end-of-day closed balances; equal-high plateaus use their last date, including weekends. Top five episodes per book are shown; the CSV contains every nonoverlapping high-to-recovery episode.


| Episode source | Rank | Peak | Trough | All decline $ | Filter decline $ | Loss avoided $ |
| --- | --- | --- | --- | --- | --- | --- |
| all_windows | 1 | 2026-02-11 | 2026-03-27 | 7,017.95 | 3,760.05 | 3,257.90 |
| all_windows | 2 | 2022-04-25 | 2022-07-04 | 5,451.55 | 1,713.00 | 3,738.55 |
| all_windows | 3 | 2025-02-23 | 2025-04-04 | 4,520.90 | 4,812.55 | -291.65 |
| all_windows | 4 | 2026-06-15 | 2026-07-01 | 3,754.25 | 2,082.00 | 1,672.25 |
| all_windows | 5 | 2023-09-11 | 2023-10-30 | 2,984.20 | 1,959.65 | 1,024.55 |
| positive_expanding_quarterly | 1 | 2025-02-23 | 2025-04-04 | 4,520.90 | 4,812.55 | -291.65 |
| positive_expanding_quarterly | 2 | 2026-02-11 | 2026-03-27 | 7,017.95 | 3,760.05 | 3,257.90 |
| positive_expanding_quarterly | 3 | 2025-10-27 | 2026-01-05 | 1,632.40 | 2,094.60 | -462.20 |
| positive_expanding_quarterly | 4 | 2023-09-11 | 2023-10-31 | 2,950.05 | 2,086.90 | 863.15 |
| positive_expanding_quarterly | 5 | 2026-06-15 | 2026-07-01 | 3,754.25 | 2,082.00 | 1,672.25 |


## Windows responsible during the all-window worst drawdown

This decomposition is additive on the fixed all-window peak-to-trough interval. It is not an additive decomposition of the difference between two different portfolio maxima. Quarter is the decision/entry quarter.


| Decision quarter | Window | Loss avoided $ |
| --- | --- | --- |
| 2026-Q1 | 15-16 | 1,250.80 |
| 2026-Q1 | 12-13 | 807.85 |
| 2026-Q1 | 6-7 | 533.15 |
| 2026-Q1 | 21-22 | 502.05 |
| 2026-Q1 | 1-2 | 164.05 |


## Every quarter, including opportunity cost

Net P/L groups trades by entry quarter and follows them to their natural exit. Quarterly drawdowns instead use calendar-quarter settlements and reset the reference balance at quarter start. They are useful repeated risk observations, but do not sum to full-path maximum DD. The two views can differ at a quarter boundary.


| Quarter | Partial | OFF windows | Shadow net $ | Profit effect $ | All DD $ | Filter DD $ | DD reduction $ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2022-Q1 | 0 | 8 | 1,476.50 | -1,476.50 | 1,516.10 | 995.35 | 520.75 |
| 2022-Q2 | 0 | 8 | -3,039.20 | 3,039.20 | 5,349.50 | 1,724.80 | 3,624.70 |
| 2022-Q3 | 0 | 9 | 1,337.90 | -1,337.90 | 919.20 | 994.15 | -74.95 |
| 2022-Q4 | 0 | 8 | -1,866.00 | 1,866.00 | 2,271.20 | 855.15 | 1,416.05 |
| 2023-Q1 | 0 | 8 | 1,398.65 | -1,398.65 | 960.65 | 551.45 | 409.20 |
| 2023-Q2 | 0 | 8 | -1,526.10 | 1,526.10 | 1,484.05 | 536.80 | 947.25 |
| 2023-Q3 | 0 | 8 | -425.90 | 425.90 | 1,309.00 | 1,137.85 | 171.15 |
| 2023-Q4 | 0 | 9 | 770.10 | -770.10 | 1,976.70 | 1,509.60 | 467.10 |
| 2024-Q1 | 0 | 8 | 1,650.75 | -1,650.75 | 742.40 | 533.00 | 209.40 |
| 2024-Q2 | 0 | 7 | 1,876.90 | -1,876.90 | 1,795.00 | 1,236.25 | 558.75 |
| 2024-Q3 | 0 | 7 | 1,556.05 | -1,556.05 | 2,842.10 | 2,042.35 | 799.75 |
| 2024-Q4 | 0 | 7 | 404.60 | -404.60 | 1,081.95 | 1,160.20 | -78.25 |
| 2025-Q1 | 0 | 7 | 3,363.10 | -3,363.10 | 2,905.20 | 3,183.60 | -278.40 |
| 2025-Q2 | 0 | 5 | 3,471.30 | -3,471.30 | 2,339.25 | 2,073.00 | 266.25 |
| 2025-Q3 | 0 | 4 | -220.85 | 220.85 | 2,202.35 | 2,044.35 | 158.00 |
| 2025-Q4 | 0 | 4 | -334.15 | 334.15 | 2,013.00 | 2,007.90 | 5.10 |
| 2026-Q1 | 0 | 5 | -3,014.45 | 3,014.45 | 7,017.95 | 3,760.05 | 3,257.90 |
| 2026-Q2 | 0 | 6 | -2,442.65 | 2,442.65 | 3,275.40 | 1,469.95 | 1,805.45 |
| 2026-Q3 | 1 | 7 | -357.10 | 357.10 | 936.40 | 724.75 | 211.65 |


## Restore one quarter's excluded trades

All original filter decisions remain fixed; restore only the omitted trades admitted by that entry-quarter decision. Recompute the entire portfolio path and its worst DD. This keeps subsequent shadow learning unchanged. Effects overlap and must not be added across rows. Every quarter is shown.


| Restored exclusions | Net $ | Max DD $ | DD increase $ | DD advantage left $ | Profit / DD |
| --- | --- | --- | --- | --- | --- |
| 2026-Q1 | 24,970.85 | 7,017.95 | 2,205.40 | -0.00 | 3.56 |
| 2022-Q2 | 24,946.10 | 5,349.50 | 536.95 | 1,668.45 | 4.66 |
| 2025-Q2 | 31,456.60 | 5,066.70 | 254.15 | 1,951.25 | 6.21 |
| 2022-Q1 | 29,461.80 | 4,812.55 | 0.00 | 2,205.40 | 6.12 |
| 2022-Q3 | 29,323.20 | 4,812.55 | 0.00 | 2,205.40 | 6.09 |
| 2022-Q4 | 26,119.30 | 4,812.55 | 0.00 | 2,205.40 | 5.43 |
| 2023-Q1 | 29,383.95 | 4,812.55 | 0.00 | 2,205.40 | 6.11 |
| 2023-Q2 | 26,459.20 | 4,812.55 | 0.00 | 2,205.40 | 5.50 |
| 2023-Q3 | 27,559.40 | 4,812.55 | 0.00 | 2,205.40 | 5.73 |
| 2023-Q4 | 28,755.40 | 4,812.55 | 0.00 | 2,205.40 | 5.98 |
| 2024-Q1 | 29,636.05 | 4,812.55 | 0.00 | 2,205.40 | 6.16 |
| 2024-Q2 | 29,862.20 | 4,812.55 | 0.00 | 2,205.40 | 6.21 |
| 2024-Q3 | 29,541.35 | 4,812.55 | 0.00 | 2,205.40 | 6.14 |
| 2024-Q4 | 28,389.90 | 4,812.55 | 0.00 | 2,205.40 | 5.90 |
| 2025-Q3 | 27,764.45 | 4,812.55 | 0.00 | 2,205.40 | 5.77 |
| 2025-Q4 | 27,651.15 | 4,812.55 | 0.00 | 2,205.40 | 5.75 |
| 2026-Q2 | 25,542.65 | 4,812.55 | 0.00 | 2,205.40 | 5.31 |
| 2026-Q3 | 27,628.20 | 4,812.55 | 0.00 | 2,205.40 | 5.74 |
| 2025-Q1 | 31,348.40 | 4,266.75 | -545.80 | 2,751.20 | 7.35 |


## Restore two quarters together

Every pair was evaluated, without retuning the trading rule. The ten largest DD increases are shown, with all pairs in restore_quarter_pairs.csv. Rankings are hindsight concentration diagnostics.


| Restored exclusions | Net $ | Max DD $ | DD increase $ | DD advantage left $ | Profit / DD |
| --- | --- | --- | --- | --- | --- |
| 2022-Q1 + 2026-Q1 | 26,447.35 | 7,017.95 | 2,205.40 | -0.00 | 3.77 |
| 2022-Q2 + 2026-Q1 | 21,931.65 | 7,017.95 | 2,205.40 | -0.00 | 3.13 |
| 2022-Q3 + 2026-Q1 | 26,308.75 | 7,017.95 | 2,205.40 | -0.00 | 3.75 |
| 2022-Q4 + 2026-Q1 | 23,104.85 | 7,017.95 | 2,205.40 | -0.00 | 3.29 |
| 2023-Q1 + 2026-Q1 | 26,369.50 | 7,017.95 | 2,205.40 | -0.00 | 3.76 |
| 2023-Q2 + 2026-Q1 | 23,444.75 | 7,017.95 | 2,205.40 | -0.00 | 3.34 |
| 2023-Q3 + 2026-Q1 | 24,544.95 | 7,017.95 | 2,205.40 | -0.00 | 3.50 |
| 2023-Q4 + 2026-Q1 | 25,740.95 | 7,017.95 | 2,205.40 | -0.00 | 3.67 |
| 2024-Q1 + 2026-Q1 | 26,621.60 | 7,017.95 | 2,205.40 | -0.00 | 3.79 |
| 2024-Q2 + 2026-Q1 | 26,847.75 | 7,017.95 | 2,205.40 | -0.00 | 3.83 |


## Restore one window throughout the sample

Turn on the chosen window in every quarter when the original rule excluded it. All other allocations remain fixed. This assesses whether the result depends heavily on a particular window.


| Restored exclusions | Net $ | Max DD $ | DD increase $ | DD advantage left $ | Profit / DD |
| --- | --- | --- | --- | --- | --- |
| 22-23 | 28,773.35 | 5,349.95 | 537.40 | 1,668.00 | 5.38 |
| 1-2 | 28,336.05 | 5,154.85 | 342.30 | 1,863.10 | 5.50 |
| 6-7 | 27,479.70 | 5,072.10 | 259.55 | 1,945.85 | 5.42 |
| 15-16 | 26,840.60 | 5,010.85 | 198.30 | 2,007.10 | 5.36 |
| 16-17 | 30,667.15 | 4,926.35 | 113.80 | 2,091.60 | 6.23 |
| 12-13 | 25,366.40 | 4,908.45 | 95.90 | 2,109.50 | 5.17 |
| 10-11 | 28,296.30 | 4,812.55 | 0.00 | 2,205.40 | 5.88 |
| 11-12 | 28,190.50 | 4,812.55 | 0.00 | 2,205.40 | 5.86 |
| 13-14 | 28,463.25 | 4,812.55 | 0.00 | 2,205.40 | 5.91 |
| 20-21 | 29,190.30 | 4,812.55 | 0.00 | 2,205.40 | 6.07 |
| 21-22 | 26,675.30 | 4,812.55 | 0.00 | 2,205.40 | 5.54 |
| 4-5 | 28,146.75 | 4,812.55 | 0.00 | 2,205.40 | 5.85 |
| 9-10 | 28,538.85 | 4,308.40 | -504.15 | 2,709.55 | 6.62 |
| 19-20 | 30,909.15 | 3,852.40 | -960.15 | 3,165.55 | 8.02 |


## Restore one window-quarter decision

Top ten influential individual exclusions; every observed excluded window-quarter with trades is saved in restore_window_quarters.csv. An increase greater than the original advantage can occur because the counterfactual's peak and trough change.


| Restored exclusions | Net $ | Max DD $ | DD increase $ | DD advantage left $ | Profit / DD |
| --- | --- | --- | --- | --- | --- |
| 2025-Q2 / 22-23 | 28,745.40 | 5,304.15 | 491.60 | 1,713.80 | 5.42 |
| 2025-Q1 / 1-2 | 28,174.40 | 5,154.85 | 342.30 | 1,863.10 | 5.47 |
| 2025-Q1 / 6-7 | 27,753.10 | 5,072.10 | 259.55 | 1,945.85 | 5.47 |
| 2026-Q1 / 15-16 | 27,592.10 | 5,010.85 | 198.30 | 2,007.10 | 5.51 |
| 2025-Q1 / 16-17 | 29,314.25 | 4,926.35 | 113.80 | 2,091.60 | 5.95 |
| 2025-Q1 / 12-13 | 27,695.75 | 4,908.45 | 95.90 | 2,109.50 | 5.64 |
| 2025-Q1 / 22-23 | 28,628.75 | 4,858.35 | 45.80 | 2,159.60 | 5.89 |
| 2022-Q1 / 1-2 | 28,014.75 | 4,812.55 | 0.00 | 2,205.40 | 5.82 |
| 2022-Q1 / 12-13 | 27,281.20 | 4,812.55 | 0.00 | 2,205.40 | 5.67 |
| 2022-Q1 / 13-14 | 28,463.25 | 4,812.55 | 0.00 | 2,205.40 | 5.91 |


## Could just two individual exclusions explain it?

All 8,778 pairs of observed excluded window-quarter decisions were restored and their full paths recomputed. This is distinct from restoring two entire quarters. The top ten pairs follow; restore_window_quarter_pairs.csv retains every pair. These exhaustive hindsight rankings are influence diagnostics only.


| Restored exclusions | Net $ | Max DD $ | DD increase $ | DD advantage left $ | Profit / DD |
| --- | --- | --- | --- | --- | --- |
| 2026-Q1 / 12-13 + 2026-Q1 / 15-16 | 27,453.70 | 5,818.70 | 1,006.15 | 1,199.25 | 4.72 |
| 2025-Q1 / 1-2 + 2025-Q2 / 22-23 | 28,934.50 | 5,646.45 | 833.90 | 1,371.50 | 5.12 |
| 2025-Q1 / 6-7 + 2025-Q2 / 22-23 | 28,513.20 | 5,563.70 | 751.15 | 1,454.25 | 5.12 |
| 2026-Q1 / 15-16 + 2026-Q1 / 6-7 | 26,624.30 | 5,544.00 | 731.45 | 1,473.95 | 4.80 |
| 2026-Q1 / 15-16 + 2026-Q1 / 21-22 | 26,803.45 | 5,512.90 | 700.35 | 1,505.05 | 4.86 |
| 2026-Q1 / 21-22 + 2026-Q1 / 6-7 | 26,228.85 | 5,467.25 | 654.70 | 1,550.70 | 4.80 |
| 2025-Q1 / 16-17 + 2025-Q2 / 22-23 | 30,074.35 | 5,417.95 | 605.40 | 1,600.00 | 5.55 |
| 2025-Q1 / 1-2 + 2025-Q1 / 6-7 | 27,942.20 | 5,414.40 | 601.85 | 1,603.55 | 5.16 |
| 2026-Q1 / 1-2 + 2026-Q1 / 6-7 | 26,291.10 | 5,405.00 | 592.45 | 1,612.95 | 4.86 |
| 2025-Q1 / 12-13 + 2025-Q2 / 22-23 | 28,455.85 | 5,400.05 | 587.50 | 1,617.90 | 5.27 |


## Does the result depend on the end date?

Recalculate expanding results through each historical endpoint, keeping exactly the same decisions. These are sensitivity views, not independent samples.


| Through | All net $ | Filter net $ | All DD $ | Filter DD $ | DD reduction $ | All profit/DD | Filter profit/DD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2022-12-31 | 6,260.35 | 8,351.15 | 5,451.55 | 1,724.80 | 3,726.75 | 1.15 | 4.84 |
| 2023-12-31 | 10,835.50 | 12,709.55 | 5,451.55 | 2,086.90 | 3,364.65 | 1.99 | 6.09 |
| 2024-12-31 | 23,249.95 | 19,635.70 | 5,451.55 | 2,086.90 | 3,364.65 | 4.26 | 9.41 |
| 2025-12-31 | 30,809.60 | 20,915.95 | 5,451.55 | 4,812.55 | 639.00 | 5.65 | 4.35 |
| 2026-03-31 | 27,707.75 | 20,828.55 | 7,017.95 | 4,812.55 | 2,205.40 | 3.95 | 4.33 |
| 2026-06-30 | 31,047.95 | 26,611.40 | 7,017.95 | 4,812.55 | 2,205.40 | 4.42 | 5.53 |
| 2026-07-13 | 32,064.75 | 27,985.30 | 7,017.95 | 4,812.55 | 2,205.40 | 4.57 | 5.82 |


## Limits and reproducibility

Same RR=1.00 tape and $1.05 round-trip commission as the allocation study; January 2022 through July 2026. No withdrawals, restarts, position scaling or firm rules. This is closed-balance/EOD attribution, not intratrade mark-to-market risk or Apex failure attribution. No parameters were optimized here. Restoration changes allocation only, not trade outcomes, costs per trade, or future shadow decisions. The data has already been examined: neither repeated success nor a concentration finding establishes future causality or proves luck. Source hashes, decision masks and daily curves are checked against the original saved study. Reproduce with venv\Scripts\python.exe scripts\study_window_allocation_attribution.py.


## Audit files

- [drawdown_episodes.csv](drawdown_episodes.csv)
- [quarters.csv](quarters.csv)
- [restore_quarter_pairs.csv](restore_quarter_pairs.csv)
- [restore_quarters.csv](restore_quarters.csv)
- [restore_window_quarter_pairs.csv](restore_window_quarter_pairs.csv)
- [restore_window_quarters.csv](restore_window_quarters.csv)
- [restore_windows.csv](restore_windows.csv)
- [sample_endpoints.csv](sample_endpoints.csv)
- [window_quarters.csv](window_quarters.csv)
- [worst_episode_contributions.csv](worst_episode_contributions.csv)
- [summary.json](summary.json)
- [manifest.json](manifest.json)
