# Fixed daily-maximum reserve frontier

Completed 566 simulations: two products, eight historical windows, frozen pipelines. The primary model reserves a PA slot for every in-flight evaluation and requires activation at the first daily check after passing. An unaffordable pass is abandoned.

**Finding:** the March 2026 survival cliff is a common loss affecting synchronized PA balances. The exact full-tape boundary is a retrospective diagnostic, not a dollar-precise operating recommendation. Above it, distinguish nearly flat total cash from declining ongoing cash.

## Frozen design and meanings

Both products start with $5,000 and receive $200 in each later calendar month; one monthly growth order persists until filled, with death replacements taking priority. Live trading PAs + activated dormant spares + in-flight evaluations cannot exceed 20. Both use at most 20 concurrent evaluation subscriptions and a target of two **already activated** spare PAs. New evaluation starts are spaced seven days apart for 25K and one day apart for 50K. These settings are frozen from the prior shared-seat daily-maximum search; they are not optimized again here.

The reserve is the withdrawal target above the frozen failure floor, not a guaranteed minimum balance through subsequent losses. A $6,800 reserve means a $31,900 nominal balance target for 25K or $56,900 for 50K: $6,900 profit equity above starting balance, with a failure floor at +$100. Daily checks request the maximum permitted by the inherited payout model; they do not guarantee a payout every day.

Ongoing net cash = received operating withdrawals after the split minus all evaluation and activation fees. Total net cash adds the model-permitted terminal withdrawal. Owner contributions are financing, not profit. Terminal profit equity is reported separately in the CSV and is not all necessarily withdrawable.

The common reserve grid is $0–$10,000 in $1,000 steps, supplemented by $5,500–$8,000 in $100 steps. Full-tape diagnostics add $10 steps inside the known cliff and two cent-level checks inferred from the previous $6,700 failure. These extra points deliberately use hindsight.

## March 30, 2026: the exact event

| Product | Reserve | Profit equity before trade / PA | Trade MAE | Adverse profit equity / PA | Failure floor | PAs failing |
| --- | --- | --- | --- | --- | --- | --- |
| legacy_25k | $6,700.00 | $101.40 | $-81.50 | $19.90 | $100.00 | 20 |
| legacy_25k | $6,780.10 | $181.50 | $-81.50 | $100.00 | $100.00 | 20 |
| legacy_25k | $6,780.11 | $181.51 | $-81.50 | $100.01 | $100.00 | 0 |
| legacy_25k | $6,800.00 | $201.40 | $-81.50 | $119.90 | $100.00 | 0 |
| legacy_50k | $6,700.00 | $101.40 | $-81.50 | $19.90 | $100.00 | 20 |
| legacy_50k | $6,780.10 | $181.50 | $-81.50 | $100.00 | $100.00 | 20 |
| legacy_50k | $6,780.11 | $181.51 | $-81.50 | $100.01 | $100.00 | 0 |
| legacy_50k | $6,800.00 | $201.40 | $-81.50 | $119.90 | $100.00 | 0 |

All rows refer to the same tape trade, `RR1.00:3-4:558:2084`, recorded at its exit on 2026-03-30 at 06:00. The intratrade breach itself has no finer timestamp in these exports. Touching the +$100 floor fails. The one-cent separation demonstrates the simulator threshold and rounding, not predictive precision. The $6,800 reserve leaves only $19.89 above the inferred minimum passing reserve in this replay.

The accounts share the same trades and withdrawal rule. Once balances converge, twenty accounts do not provide twenty independent chances of surviving that loss. A count of twenty deaths here is one common shock, not twenty independent observations.

## Full-history frontier

The highest **ongoing** net cash on the tested full-history grid occurs at **$5,700** for both products. That policy loses the established book in 2026. At $6,800, less cash has been received during operation, but all 20 trading PAs remain alive at the horizon, with much larger closing withdrawals. A reserve selected for survival is therefore a different choice from the best operating-cash result.

### legacy_25k

| Reserve | Ongoing net | Closing cash | Total net | PA deaths | Eval subscriptions | PAs alive at end |
| --- | --- | --- | --- | --- | --- | --- |
| $0.00 | $226,389.97 | $0.00 | $226,389.97 | 235 | 255 | 9 |
| $3,000.00 | $414,429.00 | $0.00 | $414,429.00 | 155 | 173 | 10 |
| $5,000.00 | $450,534.00 | $0.00 | $450,534.00 | 105 | 117 | 2 |
| $5,700.00 | $538,435.18 | $0.00 | $538,435.18 | 63 | 74 | 5 |
| $6,000.00 | $532,975.08 | $0.00 | $532,975.08 | 63 | 74 | 5 |
| $6,500.00 | $524,276.12 | $0.00 | $524,276.12 | 62 | 74 | 2 |
| $6,700.00 | $520,426.12 | $0.00 | $520,426.12 | 63 | 73 | 4 |
| $6,800.00 | $530,656.82 | $99,263.62 | $629,920.44 | 36 | 58 | 20 |
| $7,000.00 | $527,016.78 | $102,903.62 | $629,920.40 | 36 | 58 | 20 |
| $7,100.00 | $525,196.80 | $104,723.62 | $629,920.42 | 36 | 58 | 20 |
| $7,500.00 | $517,916.79 | $112,003.62 | $629,920.41 | 36 | 58 | 20 |
| $8,000.00 | $507,450.23 | $121,290.18 | $628,740.41 | 34 | 57 | 20 |
| $9,000.00 | $489,050.13 | $139,690.18 | $628,740.31 | 34 | 57 | 20 |
| $10,000.00 | $470,087.36 | $158,652.94 | $628,740.30 | 34 | 57 | 20 |

Cost of keeping extra cushion relative to $6,800, over the entire historical run:

| Reserve | Above observed passing boundary | Ongoing cash deferred/reduced | Change in closing cash | Change in total net | Mean retained profit / live PA |
| --- | --- | --- | --- | --- | --- |
| $7,000.00 | $219.89 | $3,640.04 | $3,640.00 | $-0.04 | $5,337.30 |
| $7,500.00 | $719.89 | $12,740.03 | $12,740.00 | $-0.03 | $5,678.19 |
| $8,000.00 | $1,219.89 | $23,206.59 | $22,026.56 | $-1,180.03 | $6,068.83 |

At $6,800, the last PA death is **2022-06-30T12:11:40**, with 0 deaths of PAs aged at least one year. Mean retained profit is $82,733.41 across the live book, or $5,167.52 per live PA. Mean actual floor headroom is $5,158.87 per live PA.

### legacy_50k

| Reserve | Ongoing net | Closing cash | Total net | PA deaths | Eval subscriptions | PAs alive at end |
| --- | --- | --- | --- | --- | --- | --- |
| $0.00 | $358,270.94 | $0.00 | $358,270.94 | 205 | 226 | 8 |
| $3,000.00 | $459,988.55 | $0.00 | $459,988.55 | 141 | 162 | 7 |
| $5,000.00 | $537,260.48 | $0.00 | $537,260.48 | 69 | 91 | 11 |
| $5,700.00 | $549,134.58 | $1,898.95 | $551,033.53 | 48 | 70 | 13 |
| $6,000.00 | $543,231.40 | $0.00 | $543,231.40 | 48 | 70 | 13 |
| $6,500.00 | $534,441.40 | $0.00 | $534,441.40 | 48 | 70 | 11 |
| $6,700.00 | $529,946.40 | $0.00 | $529,946.40 | 55 | 77 | 7 |
| $6,800.00 | $542,879.40 | $98,885.60 | $641,765.00 | 22 | 44 | 20 |
| $7,000.00 | $539,279.39 | $102,485.60 | $641,764.99 | 22 | 44 | 20 |
| $7,100.00 | $537,479.39 | $104,285.60 | $641,764.99 | 22 | 44 | 20 |
| $7,500.00 | $530,279.40 | $111,485.60 | $641,765.00 | 22 | 44 | 20 |
| $8,000.00 | $521,279.40 | $120,485.60 | $641,765.00 | 22 | 44 | 20 |
| $9,000.00 | $503,279.22 | $138,485.60 | $641,764.82 | 22 | 44 | 20 |
| $10,000.00 | $484,370.58 | $157,394.23 | $641,764.81 | 22 | 44 | 20 |

Cost of keeping extra cushion relative to $6,800, over the entire historical run:

| Reserve | Above observed passing boundary | Ongoing cash deferred/reduced | Change in closing cash | Change in total net | Mean retained profit / live PA |
| --- | --- | --- | --- | --- | --- |
| $7,000.00 | $219.89 | $3,600.01 | $3,600.00 | $-0.01 | $5,198.16 |
| $7,500.00 | $719.89 | $12,600.00 | $12,600.00 | $0.00 | $5,529.87 |
| $8,000.00 | $1,219.89 | $21,600.00 | $21,600.00 | $0.00 | $5,948.48 |

At $6,800, the last PA death is **2021-06-07T12:10:40**, with 0 deaths of PAs aged at least one year. Mean retained profit is $85,026.12 across the live book, or $5,055.40 per live PA. Mean actual floor headroom is $5,153.66 per live PA.

## Replacement service and retained capital

| Product | Reserve | Completed wait median, days | Completed wait p95, days | Unresolved replacements | Unfilled replacement PA-days | Mean retained book profit |
| --- | --- | --- | --- | --- | --- | --- |
| legacy_25k | $6,700.00 | 31.75 | 124.02 | 16 | 3349.77 | $77,711.06 |
| legacy_25k | $6,800.00 | 27.48 | 126.04 | 0 | 1538.35 | $82,733.41 |
| legacy_25k | $7,500.00 | 27.48 | 126.04 | 0 | 1538.35 | $90,909.24 |
| legacy_25k | $8,000.00 | 36.62 | 126.04 | 0 | 1597.79 | $96,913.01 |
| legacy_50k | $6,700.00 | 35.49 | 121.35 | 13 | 2103.25 | $80,714.60 |
| legacy_50k | $6,800.00 | 35.49 | 123.35 | 0 | 830.17 | $85,026.12 |
| legacy_50k | $7,500.00 | 35.49 | 123.35 | 0 | 830.17 | $93,006.13 |
| legacy_50k | $8,000.00 | 35.49 | 123.35 | 0 | 830.17 | $100,046.74 |

Replacement waits are FIFO, measured from actual recorded PA death to replacement deployment. Median and p95 include only completed waits; unresolved counts and accumulated waiting days include censored deaths at the horizon. They must be read together. `vacant_capacity_days_including_startup` also counts seats not yet demanded during the gradual monthly build, so it is not interchangeable with replacement downtime.

Retained capital integrates settled profit equity between trade settlements, payout settlements and daily decisions, before terminal liquidation. It excludes the nominal $25K/$50K balance and dormant spares with zero profit. Per-PA averages divide by actual live PA-days. Signed profit, positive-only profit, and actual drawdown headroom are separate CSV columns. Intratrade marked equity cannot be time-weighted from MAE/MFE exports because the intratrade timing is unknown.

## Historical window sensitivity

The 2024 cold starts expose a higher boundary in 25K: one PA older than a year fails on March 24, 2026 with a $6,800 target. **$7,100 is the first common-grid reserve after which there are no aged-PA deaths** in those windows (only $100 resolution here). The 50K 2026-containing windows reach that condition at $6,800. This is direct evidence that $6,800 is not a universal boundary even on the same historical tape.

| Product | Cold-start window | No aged-PA deaths from tested reserve | All PA deaths at that reserve | PA-days aged at least a year | Best tested ongoing reserve |
| --- | --- | --- | --- | --- | --- |
| legacy_25k | full | $6,780.11 | 36 | 28538.93 | $5,700.00 |
| legacy_25k | start_2021 | $6,800.00 | 25 | 23770.93 | $5,700.00 |
| legacy_25k | start_2022 | $6,800.00 | 23 | 16295.93 | $5,000.00 |
| legacy_25k | start_2023 | $6,800.00 | 14 | 10950.93 | $5,000.00 |
| legacy_25k | start_2024 | $7,100.00 | 26 | 4717.44 | $5,000.00 |
| legacy_25k | two_years_2020 | n/a | 55 | 0 | $3,000.00 |
| legacy_25k | two_years_2022 | $4,000.00 | 16 | 1333.64 | $0.00 |
| legacy_25k | two_years_2024 | $7,100.00 | 32 | 1545.83 | $5,000.00 |
| legacy_50k | full | $6,780.11 | 22 | 30001.93 | $5,700.00 |
| legacy_50k | start_2021 | $6,800.00 | 11 | 25203.93 | $5,700.00 |
| legacy_50k | start_2022 | $6,800.00 | 8 | 15000.93 | $5,000.00 |
| legacy_50k | start_2023 | $6,800.00 | 3 | 10208.93 | $5,000.00 |
| legacy_50k | start_2024 | $6,800.00 | 17 | 4859.44 | $5,000.00 |
| legacy_50k | two_years_2020 | n/a | 51 | 0 | $3,000.00 |
| legacy_50k | two_years_2022 | $4,000.00 | 2 | 863.84 | $1,000.00 |
| legacy_50k | two_years_2024 | $6,800.00 | 28 | 1918.81 | $2,000.00 |

The boundary column is the lowest **tested** reserve from which this and all higher tested reserves have no deaths of PAs aged at least 365 days. This separates established-account survival from fragile new accounts that have not accumulated their target cushion. It does not mean no deaths of any age. Read the exposure column: low mature exposure is weak evidence, and zero exposure provides none. The early two-year windows show n/a because their raw zero-death condition starts at a reserve where no PA lives long enough to enter the aged group; that is not evidence that a zero reserve is safe. The CSV also reports deaths after the first and second system years and their last dates.

Each window restarts empty with the same cash and contribution schedule; there is no inherited PA inventory or equity. Annual cold starts end in July 2026. The three two-year windows run July 2020–June 2022, July 2022–June 2024, and July 2024–June 2026. Trades entering before a start or exiting beyond a window are excluded. Comparisons are within windows; absolute cash differs with duration. These windows overlap and reuse data that informed the strategy and reserve search. They show historical sensitivity, not independent validation or future survival probabilities.

## Activation assumptions and implementation checks

`shared_seats` is the requested conservative operating policy: reserve capacity before evaluations pass. It is stronger than merely enforcing a deadline; a deadline by itself does not make running evaluations occupy PA seats. The new `activate_on_first_check` option also eliminates indefinite waiting for activation cash. Its default remains off so previous studies preserve their behavior.

Current official Legacy documentation permits passed evaluations to remain active with monthly renewal payments until PA payment. Its 48-hour wording concerns renewal refunds. [Legacy activation documentation](https://apextraderfunding.com/help-center/legacy-evaluation-accounts/how-to-activate-your-legacy-pa/). The newer EOD/Intraday products instead have a seven-calendar-day activation deadline. [New-product activation deadline](https://apextraderfunding.com/help-center/billing/pa-activation-process-deadline-explained/). A three-day deadline was not verified. These pages were checked on 2026-09-15; this study uses the requested first-daily-check assumption, not those current product rules.

Historical evaluation sizing, fees, drawdown handling, payout restrictions and terminal interpretation remain those of the preceding Legacy study. Activation fees stay $125 for both products for comparability. The simulator is not a reconstruction of every historical or current firm rule.

In 47 full-history settings a passed evaluation was forfeited for lack of activation cash. These effects can move results relative to the older free-wait model and make reserve responses nonmonotonic. Per-setting forfeits, subscription resets, monthly fees and activation delays are in `frontier.csv`.

All 566 runs reconcile cash and economics and obey the reserved-seat cap. 6 inherited-policy controls reproduce every shared saved field. Eight detailed trace replays match their frontier rows. 528 pre-existing result files are unchanged. The contract records input, engine, runner and configuration hashes and rejects a resume under changed assumptions.

An output-only repair omitted the nested date-keyed daily P&L dictionary from the flat death CSV. `OUTPUT_EXPORT_FIX.json` verifies that this was the sole source change, that all numerical functions are unchanged, and that the completed checkpoint was preserved. The original runner and contract are archived alongside the repair record.

## How to use these results

Treat the observed threshold as a historical stress level. Compare a margin above it against cash deferred and replacement losses, rather than choosing the best cent from this tape. A flat total-cash curve alone does not establish a flat operating-cash curve. Keep newborn-account survival and evaluation financing separate from the mature-account cushion question.

A further robustness test should perturb the loss sequence while preserving blocks of trades and common shocks across PAs, and test execution/commission stress under frozen policies. Shuffling each PA independently would erase the synchronized failure risk found here. Any such resampling remains a stress experiment; a genuinely untouched future period is needed for out-of-sample evidence.

Files: [complete frontier](frontier.csv), [window boundaries](boundaries.csv), [machine-readable study](study.json), [audit](AUDIT.json). Detail folders contain the March trade trace, PA deaths, evaluation histories, replacement waits and daily pipeline states.
