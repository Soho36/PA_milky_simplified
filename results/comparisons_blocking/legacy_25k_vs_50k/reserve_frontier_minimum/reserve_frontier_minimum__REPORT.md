# Daily minimum versus maximum: matched reserve frontier — blocked copying

Completed 1,280 simulations, equally split between daily minimum and maximum withdrawals, on identical reserve grids and eight historical windows. Product-specific pipelines and owner funding are frozen to the prior maximum-frontier settings.

**Execution: blocked copying.** Each funded account holds at most one position; an account still in an earlier trade skips a new signal. Grid, pipelines and windows match the [non-blocking paired frontier](../../../comparisons/legacy_25k_vs_50k/reserve_frontier_minimum/reserve_frontier_minimum__REPORT.md).

legacy_25k: daily minimum's best tested ongoing cash is $329,932.00 at a $3,500.00 reserve (5 PAs alive); daily maximum's is $319,487.30 at $4,000.00. The full-history aged-PA survival boundary is $6,400.00 under minimum and $6,200.00 under maximum.

legacy_50k: daily minimum's best tested ongoing cash is $440,140.00 at a $3,000.00 reserve (16 PAs alive); daily maximum's is $337,153.10 at $1,000.00. The full-history aged-PA survival boundary is not reached under minimum and not reached under maximum.

## Full-history findings

| Product | Daily request | Best tested ongoing reserve | Ongoing net | PAs alive at that reserve | All deaths | Tested aged-PA survival boundary |
| --- | --- | --- | --- | --- | --- | --- |
| legacy_25k | minimum | $3,500.00 | $329,932.00 | 5 | 108 | $6,400.00 |
| legacy_25k | maximum | $4,000.00 | $319,487.30 | 3 | 105 | $6,200.00 |
| legacy_50k | minimum | $3,000.00 | $440,140.00 | 16 | 68 | n/a |
| legacy_50k | maximum | $1,000.00 | $337,153.10 | 6 | 144 | n/a |

For legacy_25k, the best tested minimum-policy ongoing cash exceeds the best tested maximum-policy ongoing cash by $10,444.70. Their winning reserves and survival outcomes differ; this is a comparison of the best settings on the common grid, not a same-reserve effect.

For legacy_50k, the best tested minimum-policy ongoing cash exceeds the best tested maximum-policy ongoing cash by $102,986.90. Their winning reserves and survival outcomes differ; this is a comparison of the best settings on the common grid, not a same-reserve effect.

The aged-PA boundary is the lowest tested reserve from which that reserve and all higher tested reserves have zero deaths of accounts at least 365 days old, with positive exposure of such accounts. It is not a no-failure boundary for new PAs, which must first earn their cushion. A missing value means the tested grid does not establish that condition.

These pipelines differ from some winners in the broader blocked pipeline search. The 25K daily-minimum winner there used batched starts, concurrency 10 and a spare target of 2 ($406,936.00 ongoing). Here 25K keeps the maximum study’s seven-day start spacing, concurrency 20 and spare target 2, so that result is not a control for this pipeline.

## Fixed-reserve comparisons

### legacy_25k

| Reserve above floor | Daily rule | Ongoing net | Closing receipt | Total net | PAs alive | All deaths | Aged-PA deaths |
| --- | --- | --- | --- | --- | --- | --- | --- |
| $3,700.00 | maximum | $203,558.25 | $9,000.00 | $212,558.25 | 15 | 138 | 18 |
| $3,700.00 | minimum | $324,590.00 | $1,500.00 | $326,090.00 | 5 | 107 | 21 |
| $3,900.00 | maximum | $186,367.45 | $22,500.00 | $208,867.45 | 15 | 141 | 17 |
| $3,900.00 | minimum | $318,184.00 | $3,000.00 | $321,184.00 | 6 | 110 | 20 |
| $4,000.00 | maximum | $319,487.30 | $4,500.00 | $323,987.30 | 3 | 105 | 20 |
| $4,000.00 | minimum | $325,441.00 | $3,000.00 | $328,441.00 | 6 | 105 | 20 |
| $5,700.00 | maximum | $215,439.75 | $4,500.00 | $219,939.75 | 3 | 111 | 20 |
| $5,700.00 | minimum | $184,275.00 | $3,000.00 | $187,275.00 | 6 | 110 | 19 |
| $6,000.00 | maximum | $186,771.80 | $4,500.00 | $191,271.80 | 5 | 111 | 19 |
| $6,000.00 | minimum | $196,822.00 | $4,500.00 | $201,322.00 | 7 | 103 | 16 |
| $6,500.00 | maximum | $188,032.00 | $127,449.21 | $315,481.21 | 20 | 84 | 0 |
| $6,500.00 | minimum | $187,001.00 | $0.00 | $187,001.00 | 20 | 80 | 0 |
| $6,600.00 | maximum | $187,344.60 | $134,600.15 | $321,944.75 | 20 | 79 | 0 |
| $6,600.00 | minimum | $164,690.00 | $1,500.00 | $166,190.00 | 20 | 86 | 0 |
| $6,700.00 | maximum | $185,072.95 | $136,600.15 | $321,673.10 | 20 | 78 | 0 |
| $6,700.00 | minimum | $182,864.00 | $0.00 | $182,864.00 | 20 | 80 | 0 |
| $6,800.00 | maximum | $173,731.15 | $138,600.15 | $312,331.30 | 20 | 79 | 0 |
| $6,800.00 | minimum | $174,331.00 | $0.00 | $174,331.00 | 20 | 80 | 0 |
| $7,100.00 | maximum | $175,309.45 | $138,849.21 | $314,158.66 | 20 | 78 | 0 |
| $7,100.00 | minimum | $155,190.00 | $1,500.00 | $156,690.00 | 20 | 82 | 0 |
| $7,500.00 | maximum | $167,656.00 | $146,449.21 | $314,105.21 | 20 | 72 | 0 |
| $7,500.00 | minimum | $167,501.00 | $0.00 | $167,501.00 | 20 | 72 | 0 |

### legacy_50k

| Reserve above floor | Daily rule | Ongoing net | Closing receipt | Total net | PAs alive | All deaths | Aged-PA deaths |
| --- | --- | --- | --- | --- | --- | --- | --- |
| $3,700.00 | maximum | $289,465.75 | $1,689.90 | $291,155.65 | 15 | 88 | 24 |
| $3,700.00 | minimum | $416,750.00 | $2,757.90 | $419,507.90 | 14 | 64 | 24 |
| $3,900.00 | maximum | $205,227.75 | $14,289.90 | $219,517.65 | 15 | 88 | 24 |
| $3,900.00 | minimum | $336,635.00 | $3,628.70 | $340,263.70 | 14 | 63 | 24 |
| $4,000.00 | maximum | $235,070.65 | $18,589.90 | $253,660.55 | 14 | 63 | 24 |
| $4,000.00 | minimum | $239,750.00 | $3,628.70 | $243,378.70 | 15 | 63 | 24 |
| $5,700.00 | maximum | $204,851.00 | $20,000.00 | $224,851.00 | 12 | 63 | 24 |
| $5,700.00 | minimum | $194,595.00 | $20,000.00 | $214,595.00 | 14 | 63 | 24 |
| $6,000.00 | maximum | $189,597.75 | $12,000.00 | $201,597.75 | 10 | 66 | 24 |
| $6,000.00 | minimum | $190,410.00 | $10,000.00 | $200,410.00 | 14 | 56 | 17 |
| $6,500.00 | maximum | $196,939.80 | $132,885.79 | $329,825.59 | 20 | 41 | 4 |
| $6,500.00 | minimum | $200,235.00 | $0.00 | $200,235.00 | 20 | 41 | 4 |
| $6,600.00 | maximum | $194,953.10 | $134,885.79 | $329,838.89 | 20 | 41 | 4 |
| $6,600.00 | minimum | $195,735.00 | $0.00 | $195,735.00 | 20 | 41 | 4 |
| $6,700.00 | maximum | $175,530.60 | $136,885.79 | $312,416.39 | 20 | 41 | 4 |
| $6,700.00 | minimum | $180,395.00 | $0.00 | $180,395.00 | 20 | 41 | 4 |
| $6,800.00 | maximum | $176,765.60 | $138,885.79 | $315,651.39 | 20 | 41 | 4 |
| $6,800.00 | minimum | $173,695.00 | $0.00 | $173,695.00 | 20 | 41 | 4 |
| $7,100.00 | maximum | $171,847.10 | $144,885.79 | $316,732.89 | 20 | 41 | 4 |
| $7,100.00 | minimum | $142,250.00 | $0.00 | $142,250.00 | 19 | 47 | 4 |
| $7,500.00 | maximum | $158,517.05 | $152,885.79 | $311,402.84 | 20 | 41 | 4 |
| $7,500.00 | minimum | $137,970.00 | $0.00 | $137,970.00 | 19 | 47 | 4 |

Net cash is after payout splits and all evaluation/activation spending. It excludes owner contributions. Ongoing net subtracts all costs from operating receipts; total adds the final permitted withdrawal. The same trajectory produces both scores. End-of-run profit equity is a separate CSV column and should not be confused with the permitted closing receipt.

## How wide is the cash plateau?

| Product | Rule | Tested reserves within 1% of best ongoing cash |
| --- | --- | --- |
| legacy_25k | minimum | $3,000, $3,500, $3,600 |
| legacy_25k | maximum | $4,000, $4,100 |
| legacy_50k | minimum | $3,000 |
| legacy_50k | maximum | $0, $1,000 |

These are discrete tested values, not continuous intervals or confidence bands. A near-best cash reserve can still lose the whole established book. The most profitable reserve is not necessarily the reserve that best preserves earning capacity.

## Balance dispersion and the March event

| Product | Reserve | Rule | Live before March 30 trade | Different profit balances | Deaths on March 30 | Mean spread among frozen-floor PAs | Time all frozen-floor balances identical |
| --- | --- | --- | --- | --- | --- | --- | --- |
| legacy_25k | $6,500.00 | maximum | 20 | 2 | 0 | $994.92 | 2.5% |
| legacy_25k | $6,500.00 | minimum | 20 | 16 | 0 | $987.21 | 0.0% |
| legacy_25k | $6,700.00 | maximum | 20 | 2 | 0 | $923.79 | 2.6% |
| legacy_25k | $6,700.00 | minimum | 20 | 16 | 0 | $999.40 | 0.0% |
| legacy_25k | $6,800.00 | maximum | 20 | 1 | 0 | $925.95 | 19.0% |
| legacy_25k | $6,800.00 | minimum | 20 | 16 | 0 | $1,029.64 | 0.0% |
| legacy_50k | $6,500.00 | maximum | 20 | 1 | 0 | $385.33 | 25.8% |
| legacy_50k | $6,500.00 | minimum | 20 | 7 | 0 | $462.63 | 0.0% |
| legacy_50k | $6,700.00 | maximum | 20 | 1 | 0 | $405.23 | 26.2% |
| legacy_50k | $6,700.00 | minimum | 20 | 9 | 0 | $494.16 | 0.0% |
| legacy_50k | $6,800.00 | maximum | 20 | 1 | 0 | $398.42 | 26.3% |
| legacy_50k | $6,800.00 | minimum | 20 | 10 | 0 | $542.74 | 0.0% |

Minimum asks for $500 when eligible; maximum asks for all permitted excess above the target. Daily checks do not guarantee daily payouts. Fixed-size withdrawals can preserve residual balance differences while maximum withdrawals can reset accounts to the same target. Minimum also retains more money on some paths, so the fixed-reserve comparison measures both effects together.

Spread is the cross-account population standard deviation, averaged over event time. The frozen-floor group contains only live PAs whose failure floor has stopped trailing, reducing the influence of brand-new accounts. Periods with fewer than two qualifying PAs are excluded from the spread and synchronization denominators, and their exposure days are reported. The age-based survival measure and frozen-floor dispersion group are deliberately different concepts. All PAs still share the same trades; different balances do not create independent trading returns.

The March 30 final trade’s adverse excursion was $81.50. Without blocking it killed every daily-maximum PA up to a $6,780.10 reserve. With blocking, no PA dies on March 30 from $6,100.00 under maximum and $6,400.00 under minimum for legacy_25k; $6,100.00 under maximum and $6,400.00 under minimum for legacy_50k. Zero deaths on March 30 can also mean the book died earlier; read the pre-trade live count and lifetime death measures together.

## Comparison at similar actual retained capital

| Product | Minimum reserve | Nearest maximum reserve | Per-PA capital gap % | Book capital gap % | Both within 5% | Minimum ongoing | Maximum ongoing | Minimum survivors | Maximum survivors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| legacy_25k | $3,700.00 | $5,000.00 | 4.33 | 5.326 | no | $324,590.00 | $245,382.00 | 5 | 6 |
| legacy_25k | $3,900.00 | $5,000.00 | 2.148 | 8.085 | no | $318,184.00 | $245,382.00 | 6 | 6 |
| legacy_25k | $4,000.00 | $5,000.00 | 1.24 | 12.057 | no | $325,441.00 | $245,382.00 | 6 | 6 |
| legacy_25k | $6,000.00 | $6,400.00 | 2.386 | 0.21 | yes | $196,822.00 | $191,146.60 | 7 | 20 |
| legacy_25k | $6,500.00 | $7,000.00 | 1.645 | 0.528 | yes | $187,001.00 | $177,217.45 | 20 | 20 |
| legacy_25k | $6,700.00 | $7,100.00 | 1.266 | 1.16 | yes | $182,864.00 | $175,309.45 | 20 | 20 |
| legacy_25k | $6,800.00 | $7,100.00 | 0.442 | 0.422 | yes | $174,331.00 | $175,309.45 | 20 | 20 |
| legacy_25k | $7,100.00 | $7,300.00 | 0.223 | 0.961 | yes | $155,190.00 | $164,238.15 | 20 | 20 |
| legacy_25k | $7,500.00 | $8,000.00 | 0.642 | 1.022 | yes | $167,501.00 | $150,948.15 | 20 | 20 |
| legacy_50k | $3,700.00 | $5,700.00 | 7.487 | 26.424 | no | $416,750.00 | $204,851.00 | 14 | 12 |
| legacy_50k | $3,900.00 | $5,000.00 | 0.538 | 16.868 | no | $336,635.00 | $210,348.00 | 14 | 14 |
| legacy_50k | $4,000.00 | $4,500.00 | 2.017 | 1.564 | yes | $239,750.00 | $231,915.65 | 15 | 14 |
| legacy_50k | $6,000.00 | $6,700.00 | 0.32 | 0.912 | yes | $190,410.00 | $175,530.60 | 14 | 20 |
| legacy_50k | $6,500.00 | $7,300.00 | 0.502 | 1.98 | yes | $200,235.00 | $166,812.95 | 20 | 20 |
| legacy_50k | $6,700.00 | $7,300.00 | 0.228 | 0.336 | yes | $180,395.00 | $166,812.95 | 20 | 20 |
| legacy_50k | $6,800.00 | $7,200.00 | 0.761 | 0.064 | yes | $173,695.00 | $169,033.35 | 20 | 20 |
| legacy_50k | $7,100.00 | $6,900.00 | 2.044 | 2.091 | yes | $142,250.00 | $172,312.15 | 19 | 20 |
| legacy_50k | $7,500.00 | $7,400.00 | 0.378 | 3.576 | yes | $137,970.00 | $162,916.25 | 19 | 20 |

For every minimum setting with positive average retained profit, select the maximum setting in the same product/window minimizing the sum of relative differences in average book profit and average profit per live PA. A pair is flagged comparable only when both differences are at most 5%, relative to minimum. No interpolation or invented reserve is used.

This is an outcome-based descriptive match, not a controlled causal experiment. Similar lifetime average capital does not guarantee the same capital immediately before a shock, the same account ages, or the same payout history. It can show whether a difference persists at roughly similar retention, but cannot assign a percentage of the benefit to desynchronization.

For legacy_25k, minimum at $6,800 matches maximum at $7,100.00 within 0.44% per PA and 0.42% for the book. Minimum delivers $978.45 less ongoing net cash; it finishes with 20 live PAs against 20. Average-capital matching keeps its limitations.

For legacy_50k, minimum at $6,800 matches maximum at $7,200.00 within 0.76% per PA and 0.06% for the book. Minimum delivers $4,661.65 more ongoing net cash; it finishes with 20 live PAs against 20. Average-capital matching keeps its limitations.

## Replacement demand and retained profit

| Product | Reserve | Rule | Eval subscriptions | Completed median wait, days | Completed p95 wait, days | Unfilled replacements at end | Unfilled replacement PA-days | Mean retained profit / live PA |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| legacy_25k | $3,900.00 | maximum | 181 | 87.31 | 389.31 | 5 | 16341.95 | $2,091.82 |
| legacy_25k | $3,900.00 | minimum | 142 | 79.62 | 346.31 | 14 | 12018.64 | $2,849.37 |
| legacy_25k | $6,700.00 | maximum | 158 | 114.4 | 672.23 | 0 | 15840.68 | $3,752.02 |
| legacy_25k | $6,700.00 | minimum | 158 | 106.9 | 662.87 | 0 | 15958.76 | $3,971.23 |
| legacy_25k | $6,800.00 | maximum | 158 | 118.9 | 672.23 | 0 | 16478.9 | $3,799.44 |
| legacy_25k | $6,800.00 | minimum | 161 | 110.9 | 672.31 | 0 | 16542.76 | $4,039.39 |
| legacy_25k | $7,100.00 | maximum | 160 | 83.08 | 729.31 | 0 | 16537.91 | $4,021.52 |
| legacy_25k | $7,100.00 | minimum | 168 | 73.4 | 743.23 | 0 | 17185.2 | $4,097.94 |
| legacy_50k | $3,900.00 | maximum | 146 | 49.08 | 530.54 | 5 | 10795.57 | $2,065.79 |
| legacy_50k | $3,900.00 | minimum | 120 | 45.95 | 530.54 | 6 | 9170.32 | $2,803.01 |
| legacy_50k | $6,700.00 | maximum | 152 | 125.02 | 775.54 | 0 | 13970.4 | $3,519.52 |
| legacy_50k | $6,700.00 | minimum | 159 | 125.02 | 776.08 | 0 | 13936.4 | $3,754.56 |
| legacy_50k | $6,800.00 | maximum | 146 | 125.02 | 769.54 | 0 | 13904.4 | $3,574.59 |
| legacy_50k | $6,800.00 | minimum | 160 | 125.02 | 776.54 | 0 | 14071.4 | $3,752.71 |
| legacy_50k | $7,100.00 | maximum | 139 | 125.02 | 728.54 | 0 | 13797.4 | $3,677.97 |
| legacy_50k | $7,100.00 | minimum | 173 | 122.69 | 790.54 | 1 | 14916.35 | $3,672.79 |

Median and p95 use completed replacement waits only. Unresolved counts and accumulated replacement PA-days include censored waits through the horizon. Unused capacity during startup is reported separately from unmet replacement demand. Actual retained profit integrates settled equity between trade, payout and decision events. It excludes nominal $25K/$50K balances and is not a reconstructed intratrade marked-equity path.

## Historical window sensitivity

For legacy_25k, minimum wins on best tested ongoing cash in 4 of 8 windows. Maximum wins in start_2024, two_years_2020, two_years_2022, two_years_2024. These are comparisons after separately selecting each mechanism's best reserve within each window, not the performance of one fixed reserve across all windows.

For legacy_50k, minimum wins on best tested ongoing cash in 5 of 8 windows. Maximum wins in two_years_2020, two_years_2022, two_years_2024. These are comparisons after separately selecting each mechanism's best reserve within each window, not the performance of one fixed reserve across all windows.

Minimum needs a higher aged-PA survival reserve than maximum in: legacy_25k full ($6,400.00 versus $6,200.00); legacy_25k start_2021 ($6,400.00 versus $6,100.00); legacy_25k start_2022 ($6,400.00 versus $6,100.00); legacy_25k start_2023 ($6,400.00 versus $6,200.00); legacy_25k start_2024 ($6,400.00 versus $6,200.00); legacy_25k two_years_2024 ($6,300.00 versus $6,200.00); legacy_50k start_2021 ($6,200.00 versus $6,100.00); legacy_50k start_2022 ($6,200.00 versus $6,100.00); legacy_50k start_2023 ($6,400.00 versus $6,100.00); legacy_50k start_2024 ($6,400.00 versus $6,200.00). A boundary from one window is not stable across starting dates.

| Product | Window | Daily rule | Best ongoing reserve | Best ongoing net | Aged-PA survival boundary | All deaths at boundary | Aged PA-days at boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| legacy_25k | full | minimum | $3,500.00 | $329,932.00 | $6,400.00 | 83 | 9151.93 |
| legacy_25k | full | maximum | $4,000.00 | $319,487.30 | $6,200.00 | 84 | 9943.93 |
| legacy_25k | start_2021 | minimum | $3,000.00 | $406,786.00 | $6,400.00 | 44 | 16691.93 |
| legacy_25k | start_2021 | maximum | $4,000.00 | $368,788.35 | $6,100.00 | 44 | 16691.93 |
| legacy_25k | start_2022 | minimum | $3,000.00 | $382,882.00 | $6,400.00 | 18 | 16121.93 |
| legacy_25k | start_2022 | maximum | $4,000.00 | $358,323.80 | $6,100.00 | 18 | 16121.93 |
| legacy_25k | start_2023 | minimum | $3,000.00 | $320,129.00 | $6,400.00 | 9 | 11091.93 |
| legacy_25k | start_2023 | maximum | $4,000.00 | $298,136.95 | $6,200.00 | 9 | 11091.93 |
| legacy_25k | start_2024 | minimum | $3,400.00 | $151,129.00 | $6,400.00 | 15 | 4733.44 |
| legacy_25k | start_2024 | maximum | $4,000.00 | $151,264.40 | $6,200.00 | 20 | 4541.65 |
| legacy_25k | two_years_2020 | minimum | $0.00 | $2,191.00 | n/a | n/a | n/a |
| legacy_25k | two_years_2020 | maximum | $0.00 | $3,391.75 | n/a | n/a | n/a |
| legacy_25k | two_years_2022 | minimum | $2,000.00 | $64,131.00 | $2,000.00 | 13 | 1333.64 |
| legacy_25k | two_years_2022 | maximum | $2,000.00 | $71,476.15 | $2,000.00 | 13 | 1333.64 |
| legacy_25k | two_years_2024 | minimum | $3,600.00 | $47,405.00 | $6,300.00 | 23 | 1486.83 |
| legacy_25k | two_years_2024 | maximum | $0.00 | $66,187.90 | $6,200.00 | 25 | 1320.88 |
| legacy_50k | full | minimum | $3,000.00 | $440,140.00 | n/a | n/a | n/a |
| legacy_50k | full | maximum | $1,000.00 | $337,153.10 | n/a | n/a | n/a |
| legacy_50k | start_2021 | minimum | $3,000.00 | $438,530.00 | $6,200.00 | 19 | 21543.93 |
| legacy_50k | start_2021 | maximum | $4,000.00 | $412,220.75 | $6,100.00 | 19 | 21543.93 |
| legacy_50k | start_2022 | minimum | $3,000.00 | $385,560.00 | $6,200.00 | 6 | 16083.93 |
| legacy_50k | start_2022 | maximum | $4,000.00 | $362,718.30 | $6,100.00 | 6 | 16083.93 |
| legacy_50k | start_2023 | minimum | $3,000.00 | $325,810.00 | $6,400.00 | 0 | 10745.93 |
| legacy_50k | start_2023 | maximum | $4,000.00 | $303,053.70 | $6,100.00 | 0 | 10745.93 |
| legacy_50k | start_2024 | minimum | $3,400.00 | $155,040.00 | $6,400.00 | 13 | 4729.55 |
| legacy_50k | start_2024 | maximum | $4,000.00 | $152,178.60 | $6,200.00 | 13 | 4729.55 |
| legacy_50k | two_years_2020 | minimum | $0.00 | $18,260.00 | n/a | n/a | n/a |
| legacy_50k | two_years_2020 | maximum | $0.00 | $19,345.15 | n/a | n/a | n/a |
| legacy_50k | two_years_2022 | minimum | $0.00 | $64,900.00 | $0.00 | 0 | 1263.79 |
| legacy_50k | two_years_2022 | maximum | $2,000.00 | $73,120.95 | $2,000.00 | 0 | 1263.79 |
| legacy_50k | two_years_2024 | minimum | $3,400.00 | $58,510.00 | $6,200.00 | 22 | 1729.83 |
| legacy_50k | two_years_2024 | maximum | $2,000.00 | $82,959.55 | $6,200.00 | 22 | 1729.83 |

The full history runs January 2020–July 2026. Annual cold starts begin in 2021, 2022, 2023 and 2024 and end at the same July 2026 horizon. Three two-year windows start in July 2020, July 2022 and July 2024. Every window starts empty with fresh funding and no inherited account equity. No trade entering before the start or exiting beyond the end is imported.

These overlapping windows reuse the same history that informed earlier choices. They measure historical sensitivity, not independent validation or future survival probabilities. No new market paths or replacement-supply outages are generated in this frontier; those require a separate paired stress experiment.

The useful next comparison is a small, preselected stress set around each mechanism’s best cash reserve and its established-account survival reserve, with matched controls. Apply the same replacement interruptions and adverse trade sequences to both mechanisms, and compare cash, book recovery and capital immediately before each shock. This frontier alone does not answer that counterfactual or establish a live trading reserve.

## Frozen assumptions and validation

Both products use $5,000 initial funding plus $200 per later month, persistent monthly growth demand, a 20-seat reservation limit, concurrency 20 and two activated spare PAs as the shelf target. New evaluations start at most every seven days for 25K and every day for 50K. Evaluations reserve future PA capacity and passed evaluations must activate at the next daily check or be forfeited. The study keeps the earlier Legacy fees, exposure, payout interpretation and trade-path convention. This is an operating model, not a reconstruction of all historical firm rules.

The common grid is $0–$10,000 in $1,000 steps, with $100 steps from $3,000–$4,500 and $6,000–$7,500, plus the $5,700 probe kept from the non-blocking study, where it was the maximum-policy winner. The grid has 40 reserves for each of two products, two mechanisms and eight windows. There is no pipeline retuning or post-result expansion of the grid.

All 1,280 runs reconcile economic and owner-cash identities and obey the seat cap. 416 maximum-policy rows reproduce every shared numerical field from the previous frontier. The matched March-review cases also reproduce their cash and survival results. 23 detailed replays match their frontier rows. 3487 prior result files are unchanged; plain-language navigation guides may be refreshed separately.

10 settings shared with the blocked March review reproduce it, including per-trade account assignments. Across the 23 detailed replays, none of 2,014 PA histories held two trades at once.

Files: [all settings](frontier.csv), [same-reserve differences](matched_reserves.csv), [similar-capital comparisons](similar_capital.csv), [window summaries](window_summaries.csv), [complete study](study.json), [audit](AUDIT.json). The detailed run folders hold March traces, account deaths, replacement waits and daily pipeline states. Each has a START_HERE.txt guide.
