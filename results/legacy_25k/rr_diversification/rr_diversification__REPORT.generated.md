# RR diversification: clustered deaths

286 frozen historical runs. Daily minimum/$6,800 headroom is primary; maximum-daily and MFE-first are sensitivities.
No RR weights, reserve or supply policy were optimized. Cash is net of all acquisition/evaluation fees, excludes owner contributions and excludes terminal receipts.

## Main comparisons

Death dates are exported-exit proxies. Same-signal deaths and possible interval clusters must be considered alongside rolling exit-timed losses.

### isolation, fresh 2020 start

| Portfolio | Net cash | Deaths | Alive | Wipeouts | Empty days | Max same-signal deaths | Possible 20-day cluster | Half-loss 20-day episodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| rr_0.50 | $-4,000 | 20 | 0 | 1 | 1865.2 | 20 | 20 | 1 |
| rr_0.75 | $-4,000 | 20 | 0 | 1 | 2314.0 | 20 | 20 | 1 |
| rr_1.00 | $-4,000 | 20 | 0 | 1 | 2314.0 | 20 | 20 | 1 |
| rr_1.25 | $-4,000 | 20 | 0 | 1 | 2324.8 | 20 | 20 | 1 |
| rr_1.50 | $-4,000 | 20 | 0 | 1 | 2324.7 | 20 | 20 | 1 |
| rr_2.00 | $-4,000 | 20 | 0 | 1 | 2314.0 | 20 | 20 | 1 |
| rr_2.50 | $-4,000 | 20 | 0 | 1 | 2327.2 | 20 | 20 | 1 |
| rr_3.00 | $-4,000 | 20 | 0 | 1 | 2327.4 | 20 | 20 | 1 |
| rr_3.50 | $-4,000 | 20 | 0 | 1 | 2327.4 | 20 | 20 | 1 |
| near | $-4,000 | 20 | 0 | 1 | 2314.0 | 10 | 20 | 2 |
| modest | $-4,000 | 20 | 0 | 1 | 1865.2 | 10 | 10 | 2 |
| four | $-4,000 | 20 | 0 | 1 | 1865.2 | 10 | 15 | 2 |
| wide | $-4,000 | 20 | 0 | 1 | 1865.2 | 5 | 15 | 3 |

### isolation, fresh 2023 start

| Portfolio | Net cash | Deaths | Alive | Wipeouts | Empty days | Max same-signal deaths | Possible 20-day cluster | Half-loss 20-day episodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| rr_0.50 | $-4,000 | 20 | 0 | 1 | 1229.9 | 20 | 20 | 1 |
| rr_0.75 | $266,000 | 0 | 20 | 0 | 0.0 | 0 | 0 | 0 |
| rr_1.00 | $356,000 | 0 | 20 | 0 | 0.0 | 0 | 0 | 0 |
| rr_1.25 | $366,000 | 0 | 20 | 0 | 0.0 | 0 | 0 | 0 |
| rr_1.50 | $376,000 | 0 | 20 | 0 | 0.0 | 0 | 0 | 0 |
| rr_2.00 | $366,000 | 0 | 20 | 0 | 0.0 | 0 | 0 | 0 |
| rr_2.50 | $466,000 | 0 | 20 | 0 | 0.0 | 0 | 0 | 0 |
| rr_3.00 | $416,000 | 0 | 20 | 0 | 0.0 | 0 | 0 | 0 |
| rr_3.50 | $386,000 | 0 | 20 | 0 | 0.0 | 0 | 0 | 0 |
| near | $316,000 | 0 | 20 | 0 | 0.0 | 0 | 0 | 0 |
| modest | $186,000 | 10 | 10 | 0 | 0.0 | 10 | 10 | 1 |
| four | $273,500 | 5 | 15 | 0 | 0.0 | 5 | 5 | 0 |
| wide | $306,000 | 5 | 15 | 0 | 0.0 | 5 | 5 | 0 |

### operating, fresh 2020 start

| Portfolio | Net cash | Deaths | Alive | Wipeouts | Empty days | Max same-signal deaths | Possible 20-day cluster | Half-loss 20-day episodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| rr_0.50 | $137,320 | 78 | 20 | 1 | 32.9 | 10 | 10 | 8 |
| rr_0.75 | $222,784 | 67 | 20 | 3 | 40.7 | 7 | 10 | 6 |
| rr_1.00 | $312,147 | 63 | 20 | 2 | 0.3 | 7 | 13 | 5 |
| rr_1.25 | $370,314 | 52 | 20 | 2 | 0.5 | 5 | 9 | 4 |
| rr_1.50 | $397,579 | 50 | 20 | 2 | 0.5 | 7 | 10 | 3 |
| rr_2.00 | $379,572 | 51 | 20 | 2 | 0.3 | 7 | 8 | 0 |
| rr_2.50 | $437,322 | 56 | 20 | 2 | 0.5 | 7 | 8 | 2 |
| rr_3.00 | $365,267 | 61 | 20 | 2 | 0.4 | 7 | 7 | 5 |
| rr_3.50 | $356,135 | 67 | 20 | 2 | 1.1 | 6 | 10 | 6 |
| near | $315,873 | 51 | 20 | 2 | 0.3 | 5 | 9 | 4 |
| modest | $307,712 | 61 | 20 | 0 | 0.0 | 8 | 12 | 5 |
| four | $330,034 | 54 | 20 | 0 | 0.0 | 4 | 8 | 2 |
| wide | $375,816 | 48 | 20 | 0 | 0.0 | 3 | 7 | 0 |

### operating, fresh 2023 start

| Portfolio | Net cash | Deaths | Alive | Wipeouts | Empty days | Max same-signal deaths | Possible 20-day cluster | Half-loss 20-day episodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| rr_0.50 | $158,459 | 16 | 20 | 1 | 69.5 | 6 | 6 | 1 |
| rr_0.75 | $149,629 | 20 | 20 | 1 | 47.2 | 6 | 6 | 1 |
| rr_1.00 | $176,775 | 19 | 19 | 1 | 42.2 | 5 | 6 | 1 |
| rr_1.25 | $176,669 | 19 | 18 | 1 | 46.1 | 2 | 6 | 1 |
| rr_1.50 | $206,563 | 22 | 18 | 1 | 53.1 | 5 | 6 | 1 |
| rr_2.00 | $209,228 | 25 | 19 | 0 | 0.0 | 2 | 6 | 1 |
| rr_2.50 | $263,867 | 17 | 20 | 0 | 0.0 | 2 | 4 | 1 |
| rr_3.00 | $241,058 | 20 | 20 | 0 | 0.0 | 3 | 6 | 1 |
| rr_3.50 | $180,528 | 36 | 19 | 1 | 46.1 | 3 | 6 | 1 |
| near | $173,275 | 22 | 20 | 1 | 9.2 | 4 | 6 | 1 |
| modest | $177,787 | 20 | 19 | 1 | 55.1 | 3 | 6 | 1 |
| four | $178,787 | 24 | 19 | 1 | 48.2 | 3 | 6 | 1 |
| wide | $188,417 | 28 | 18 | 0 | 0.0 | 4 | 6 | 1 |

## Mixture comparisons across primary start dates

| Phase | Mix | Lower same-signal peak vs RR1 | Lower possible 20-day peak vs RR1 | Fewer wipeouts vs RR1 | Higher net cash vs RR1 |
|---|---|---:|---:|---:|---:|
| isolation | near | 4/6 | 1/6 | 1/6 | 1/6 |
| isolation | modest | 4/6 | 2/6 | 1/6 | 2/6 |
| isolation | four | 4/6 | 4/6 | 1/6 | 2/6 |
| isolation | wide | 4/6 | 4/6 | 1/6 | 2/6 |
| operating | near | 4/6 | 2/6 | 2/6 | 2/6 |
| operating | modest | 1/6 | 3/6 | 4/6 | 3/6 |
| operating | four | 4/6 | 3/6 | 4/6 | 4/6 |
| operating | wide | 5/6 | 3/6 | 5/6 | 5/6 |

## Interpretation limits

- A homogeneous RR may be safer than a mixture; compare mixtures with all their constituents before attributing a benefit to mixing.
- Small native entry-set differences remain and are listed in signal_alignment.csv. No absent outcome was fabricated.
- Observed trade dates define rolling trading-day windows. Fractions use the cohort alive at the window start; replacement demand includes all deaths.
- Real intratrade threshold crossing times are unknown. Same-signal grouping and interval bounds do not reconstruct them.
- Fresh starts overlap the selection history and differ in duration. Results do not estimate independent probabilities or future annual income.
- The supply policy is inherited and frozen, including its fee/rule assumptions; this study does not verify current firm terms.

Every run checks assignment RR, no overlap, cash/economic reconciliation and evaluation seat limits. Homogeneous isolation controls and operating RR1 also reproduce the existing engine exactly.

Files: comparison.csv, deltas_vs_rr1.csv, signal_alignment.csv, contract.json, audit.json and per-case account/death ledgers in cases/.
