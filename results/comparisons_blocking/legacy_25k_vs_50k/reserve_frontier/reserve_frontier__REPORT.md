# Fixed daily-maximum reserve frontier — blocked copying

Completed 566 simulations: two products, eight historical windows, frozen pipelines. The primary model reserves a PA slot for every in-flight evaluation and requires activation at the first daily check after passing. An unaffordable pass is abandoned.

**Execution: blocked copying.** Each funded account holds at most one position; an account still in an earlier trade skips a new signal. Pipelines, reserve grid, probes and windows are exactly those of the [non-blocking frontier](../../../comparisons/legacy_25k_vs_50k/reserve_frontier/reserve_frontier__REPORT.md).

**Finding:** the March 30, 2026 trade is no longer the cliff it was without blocking. On the full history, legacy_25k has no PA death that day from $6,100.00 (without blocking: $6,780.11); legacy_50k has no PA death that day from $6,100.00 (without blocking: $6,780.11). The boundary remains a retrospective diagnostic, not a dollar-precise operating recommendation. Above it, distinguish nearly flat total cash from declining ongoing cash.

## Frozen design and meanings

Both products start with $5,000 and receive $200 in each later calendar month; one monthly growth order persists until filled, with death replacements taking priority. Live trading PAs + activated dormant spares + in-flight evaluations cannot exceed 20. Both use at most 20 concurrent evaluation subscriptions and a target of two **already activated** spare PAs. New evaluation starts are spaced seven days apart for 25K and one day apart for 50K. These settings are frozen from the non-blocking shared-seat daily-maximum search, so only the copying rule differs; they are not optimized again here.

The reserve is the withdrawal target above the frozen failure floor, not a guaranteed minimum balance through subsequent losses. A $6,800 reserve means a $31,900 nominal balance target for 25K or $56,900 for 50K: $6,900 profit equity above starting balance, with a failure floor at +$100. Daily checks request the maximum permitted by the inherited payout model; they do not guarantee a payout every day.

Ongoing net cash = received operating withdrawals after the split minus all evaluation and activation fees. Total net cash adds the model-permitted terminal withdrawal. Owner contributions are financing, not profit. Terminal profit equity is reported separately in the CSV and is not all necessarily withdrawable.

The common reserve grid is $0–$10,000 in $1,000 steps, supplemented by $5,500–$8,000 in $100 steps. Full-tape diagnostics keep the $10 steps and two cent-level checks placed around the non-blocking cliff, so both frontiers share one grid.

## March 30, 2026: the exact event

| Product | Reserve | PAs in the trade | Distinct balances | Weakest PA equity before trade | Trade MAE | Weakest PA adverse equity | Failure floor | PAs failing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| legacy_25k | $6,700.00 | 20 | 2 | $695.55 | $-81.50 | $614.05 | $100.00 | 0 |
| legacy_25k | $6,780.10 | 20 | 1 | $889.60 | $-81.50 | $808.10 | $100.00 | 0 |
| legacy_25k | $6,780.11 | 20 | 1 | $889.61 | $-81.50 | $808.11 | $100.00 | 0 |
| legacy_25k | $6,800.00 | 20 | 1 | $909.50 | $-81.50 | $828.00 | $100.00 | 0 |
| legacy_50k | $6,700.00 | 20 | 1 | $809.50 | $-81.50 | $728.00 | $100.00 | 0 |
| legacy_50k | $6,780.10 | 20 | 1 | $889.60 | $-81.50 | $808.10 | $100.00 | 0 |
| legacy_50k | $6,780.11 | 20 | 1 | $889.61 | $-81.50 | $808.11 | $100.00 | 0 |
| legacy_50k | $6,800.00 | 20 | 1 | $909.50 | $-81.50 | $828.00 | $100.00 | 0 |

All rows refer to the same tape trade, `RR1.00:3-4:558:2084`, recorded at its exit on 2026-03-30 at 06:00. Where balances differ, the table shows the weakest PA. At $6,700 the weakest legacy_25k PA entered the trade with $695.55 of profit equity, against $101.40 without blocking, and kept $514.05 above the failure floor at the worst point. At $6,700 the weakest legacy_50k PA entered the trade with $809.50 of profit equity, against $101.40 without blocking, and kept $628.00 above the failure floor at the worst point. Without blocking, overlapping positions had already drained the book before this trade.

## Full-history frontier

legacy_25k: the highest **ongoing** net cash on the tested full-history grid occurs at **$4,000.00** ($319,487.30, 3 PAs alive at the horizon). At $6,800 it is $173,731.15 ongoing and $312,331.30 total, with 20 PAs alive. legacy_50k: the highest **ongoing** net cash on the tested full-history grid occurs at **$1,000.00** ($337,153.10, 6 PAs alive at the horizon). At $6,800 it is $176,765.60 ongoing and $315,651.39 total, with 20 PAs alive. A reserve selected for survival is a different choice from the best operating-cash result.

### legacy_25k

| Reserve | Ongoing net | Closing cash | Total net | PA deaths | Eval subscriptions | PAs alive at end |
| --- | --- | --- | --- | --- | --- | --- |
| $0.00 | $189,770.10 | $0.00 | $189,770.10 | 213 | 226 | 4 |
| $3,000.00 | $217,073.45 | $12,000.00 | $229,073.45 | 145 | 190 | 12 |
| $5,000.00 | $245,382.00 | $4,500.00 | $249,882.00 | 114 | 155 | 6 |
| $5,700.00 | $215,439.75 | $4,500.00 | $219,939.75 | 111 | 163 | 3 |
| $6,000.00 | $186,771.80 | $4,500.00 | $191,271.80 | 111 | 173 | 5 |
| $6,500.00 | $188,032.00 | $127,449.21 | $315,481.21 | 84 | 159 | 20 |
| $6,700.00 | $185,072.95 | $136,600.15 | $321,673.10 | 78 | 158 | 20 |
| $6,800.00 | $173,731.15 | $138,600.15 | $312,331.30 | 79 | 158 | 20 |
| $7,000.00 | $177,217.45 | $136,949.21 | $314,166.66 | 79 | 160 | 20 |
| $7,100.00 | $175,309.45 | $138,849.21 | $314,158.66 | 78 | 160 | 20 |
| $7,500.00 | $167,656.00 | $146,449.21 | $314,105.21 | 72 | 162 | 20 |
| $8,000.00 | $150,948.15 | $162,600.15 | $313,548.30 | 69 | 160 | 20 |
| $9,000.00 | $121,478.70 | $159,647.33 | $281,126.03 | 71 | 155 | 20 |
| $10,000.00 | $112,606.30 | $159,345.45 | $271,951.75 | 65 | 151 | 20 |

Cost of keeping extra cushion relative to $6,800, over the entire historical run:

| Reserve | Above observed passing boundary | Ongoing cash deferred/reduced | Change in closing cash | Change in total net | Mean retained profit / live PA |
| --- | --- | --- | --- | --- | --- |
| $7,000.00 | $900.00 | $-3,486.30 | $-1,650.94 | $1,835.36 | $3,960.01 |
| $7,500.00 | $1,400.00 | $6,075.15 | $7,849.06 | $1,773.91 | $4,306.88 |
| $8,000.00 | $1,900.00 | $22,783.00 | $24,000.00 | $1,217.00 | $4,536.63 |

At $6,800, the last PA death is **2024-07-26T20:00:00**, with 0 deaths of PAs aged at least one year. Mean retained profit is $37,681.00 across the live book, or $3,799.44 per live PA. Mean actual floor headroom is $3,932.39 per live PA.

### legacy_50k

| Reserve | Ongoing net | Closing cash | Total net | PA deaths | Eval subscriptions | PAs alive at end |
| --- | --- | --- | --- | --- | --- | --- |
| $0.00 | $335,443.25 | $0.00 | $335,443.25 | 150 | 171 | 5 |
| $3,000.00 | $329,748.90 | $0.00 | $329,748.90 | 101 | 137 | 11 |
| $5,000.00 | $210,348.00 | $19,863.30 | $230,211.30 | 63 | 177 | 14 |
| $5,700.00 | $204,851.00 | $20,000.00 | $224,851.00 | 63 | 162 | 12 |
| $6,000.00 | $189,597.75 | $12,000.00 | $201,597.75 | 66 | 164 | 10 |
| $6,500.00 | $196,939.80 | $132,885.79 | $329,825.59 | 41 | 131 | 20 |
| $6,700.00 | $175,530.60 | $136,885.79 | $312,416.39 | 41 | 152 | 20 |
| $6,800.00 | $176,765.60 | $138,885.79 | $315,651.39 | 41 | 146 | 20 |
| $7,000.00 | $170,392.15 | $142,885.79 | $313,277.94 | 41 | 151 | 20 |
| $7,100.00 | $171,847.10 | $144,885.79 | $316,732.89 | 41 | 139 | 20 |
| $7,500.00 | $158,517.05 | $152,885.79 | $311,402.84 | 41 | 140 | 20 |
| $8,000.00 | $149,414.10 | $162,885.79 | $312,299.89 | 41 | 131 | 20 |
| $9,000.00 | $104,712.10 | $175,734.85 | $280,446.95 | 41 | 141 | 20 |
| $10,000.00 | $49,147.10 | $99,074.51 | $148,221.61 | 53 | 150 | 19 |

Cost of keeping extra cushion relative to $6,800, over the entire historical run:

| Reserve | Above observed passing boundary | Ongoing cash deferred/reduced | Change in closing cash | Change in total net | Mean retained profit / live PA |
| --- | --- | --- | --- | --- | --- |
| $7,000.00 | $900.00 | $6,373.45 | $4,000.00 | $-2,373.45 | $3,638.22 |
| $7,500.00 | $1,400.00 | $18,248.55 | $14,000.00 | $-4,248.55 | $3,843.48 |
| $8,000.00 | $1,900.00 | $27,351.50 | $24,000.00 | $-3,351.50 | $4,033.34 |

At $6,800, the last PA death is **2022-07-01T22:00:00**, with 4 deaths of PAs aged at least one year. Mean retained profit is $38,916.13 across the live book, or $3,574.59 per live PA. Mean actual floor headroom is $3,943.42 per live PA.

## Replacement service and retained capital

| Product | Reserve | Completed wait median, days | Completed wait p95, days | Unresolved replacements | Unfilled replacement PA-days | Mean retained book profit |
| --- | --- | --- | --- | --- | --- | --- |
| legacy_25k | $6,700.00 | 114.4 | 672.23 | 0 | 15840.68 | $38,214.97 |
| legacy_25k | $6,800.00 | 118.9 | 672.23 | 0 | 16478.9 | $37,681.00 |
| legacy_25k | $7,500.00 | 72.4 | 766.44 | 0 | 17088.6 | $41,612.43 |
| legacy_25k | $8,000.00 | 91.26 | 812.15 | 0 | 17541.7 | $42,970.20 |
| legacy_50k | $6,700.00 | 125.02 | 775.54 | 0 | 13970.4 | $38,219.22 |
| legacy_50k | $6,800.00 | 125.02 | 769.54 | 0 | 13904.4 | $38,916.13 |
| legacy_50k | $7,500.00 | 125.02 | 776.08 | 0 | 14064.4 | $41,629.12 |
| legacy_50k | $8,000.00 | 125.02 | 731.54 | 0 | 14005.4 | $43,785.36 |

Replacement waits are FIFO, measured from actual recorded PA death to replacement deployment. Median and p95 include only completed waits; unresolved counts and accumulated waiting days include censored deaths at the horizon. They must be read together. `vacant_capacity_days_including_startup` also counts seats not yet demanded during the gradual monthly build, so it is not interchangeable with replacement downtime.

Retained capital integrates settled profit equity between trade settlements, payout settlements and daily decisions, before terminal liquidation. It excludes the nominal $25K/$50K balance and dormant spares with zero profit. Per-PA averages divide by actual live PA-days. Signed profit, positive-only profit, and actual drawdown headroom are separate CSV columns. Intratrade marked equity cannot be time-weighted from MAE/MFE exports because the intratrade timing is unknown.

## Historical window sensitivity

legacy_25k: across the annual cold starts, aged-PA deaths stop from $6,100.00 to $6,200.00. legacy_50k: across the annual cold starts, aged-PA deaths stop from $6,100.00 to $6,200.00. In the full history, PAs aged at least a year still die at the highest tested reserve, so the grid has no such boundary there. Compare the non-blocking windows before treating any single value as a universal boundary.

| Product | Cold-start window | No aged-PA deaths from tested reserve | All PA deaths at that reserve | PA-days aged at least a year | Best tested ongoing reserve |
| --- | --- | --- | --- | --- | --- |
| legacy_25k | full | $6,200.00 | 84 | 9943.93 | $4,000.00 |
| legacy_25k | start_2021 | $6,100.00 | 44 | 16691.93 | $4,000.00 |
| legacy_25k | start_2022 | $6,100.00 | 18 | 16121.93 | $4,000.00 |
| legacy_25k | start_2023 | $6,200.00 | 9 | 11091.93 | $4,000.00 |
| legacy_25k | start_2024 | $6,200.00 | 20 | 4541.65 | $4,000.00 |
| legacy_25k | two_years_2020 | n/a | 52 | 0 | $0.00 |
| legacy_25k | two_years_2022 | n/a | 40 | 0 | $2,000.00 |
| legacy_25k | two_years_2024 | $6,200.00 | 25 | 1320.88 | $0.00 |
| legacy_50k | full | n/a | n/a | n/a | $1,000.00 |
| legacy_50k | start_2021 | $6,100.00 | 19 | 21543.93 | $4,000.00 |
| legacy_50k | start_2022 | $6,100.00 | 6 | 16083.93 | $4,000.00 |
| legacy_50k | start_2023 | $6,100.00 | 0 | 10745.93 | $4,000.00 |
| legacy_50k | start_2024 | $6,200.00 | 13 | 4729.55 | $4,000.00 |
| legacy_50k | two_years_2020 | n/a | 39 | 0 | $0.00 |
| legacy_50k | two_years_2022 | $2,000.00 | 0 | 1263.79 | $2,000.00 |
| legacy_50k | two_years_2024 | $6,200.00 | 22 | 1729.83 | $2,000.00 |

The boundary column is the lowest **tested** reserve from which this and all higher tested reserves have no deaths of PAs aged at least 365 days. This separates established-account survival from fragile new accounts that have not accumulated their target cushion. It does not mean no deaths of any age. Read the exposure column: low mature exposure is weak evidence, and zero exposure provides none. The early two-year windows show n/a because their raw zero-death condition starts at a reserve where no PA lives long enough to enter the aged group; that is not evidence that a zero reserve is safe. The CSV also reports deaths after the first and second system years and their last dates.

Each window restarts empty with the same cash and contribution schedule; there is no inherited PA inventory or equity. Annual cold starts end in July 2026. The three two-year windows run July 2020–June 2022, July 2022–June 2024, and July 2024–June 2026. Trades entering before a start or exiting beyond a window are excluded. Comparisons are within windows; absolute cash differs with duration. These windows overlap and reuse data that informed the strategy and reserve search. They show historical sensitivity, not independent validation or future survival probabilities.

## Activation assumptions and implementation checks

`shared_seats` is the requested conservative operating policy: reserve capacity before evaluations pass. It is stronger than merely enforcing a deadline; a deadline by itself does not make running evaluations occupy PA seats. The new `activate_on_first_check` option also eliminates indefinite waiting for activation cash. Its default remains off so previous studies preserve their behavior.

Current official Legacy documentation permits passed evaluations to remain active with monthly renewal payments until PA payment. Its 48-hour wording concerns renewal refunds. [Legacy activation documentation](https://apextraderfunding.com/help-center/legacy-evaluation-accounts/how-to-activate-your-legacy-pa/). The newer EOD/Intraday products instead have a seven-calendar-day activation deadline. [New-product activation deadline](https://apextraderfunding.com/help-center/billing/pa-activation-process-deadline-explained/). A three-day deadline was not verified. These pages were checked on 2026-09-15; this study uses the requested first-daily-check assumption, not those current product rules.

Historical evaluation sizing, fees, drawdown handling, payout restrictions and terminal interpretation remain those of the preceding Legacy study. Activation fees stay $125 for both products for comparability. The simulator is not a reconstruction of every historical or current firm rule.

In 84 full-history settings a passed evaluation was forfeited for lack of activation cash. These effects can move results relative to the older free-wait model and make reserve responses nonmonotonic. Per-setting forfeits, subscription resets, monthly fees and activation delays are in `frontier.csv`.

All 566 runs reconcile cash and economics and obey the reserved-seat cap. 6 inherited-policy controls reproduce every shared saved field. Eight detailed trace replays match their frontier rows. 3530 pre-existing result files are unchanged. The contract records input, engine, runner and configuration hashes and rejects a resume under changed assumptions.

Every trace replay was also checked independently for overlapping positions: across the 8 replays, none of 637 PA histories held two trades at once.

## How to use these results

Treat the observed threshold as a historical stress level. Compare a margin above it against cash deferred and replacement losses, rather than choosing the best cent from this tape. A flat total-cash curve alone does not establish a flat operating-cash curve. Keep newborn-account survival and evaluation financing separate from the mature-account cushion question.

A further robustness test should perturb the loss sequence while preserving blocks of trades and common shocks across PAs, and test execution/commission stress under frozen policies. Shuffling each PA independently would erase the synchronized failure risk found here. Any such resampling remains a stress experiment; a genuinely untouched future period is needed for out-of-sample evidence.

Files: [complete frontier](frontier.csv), [window boundaries](boundaries.csv), [machine-readable study](study.json), [audit](AUDIT.json). Detail folders contain the March trade trace, PA deaths, evaluation histories, replacement waits and daily pipeline states.
