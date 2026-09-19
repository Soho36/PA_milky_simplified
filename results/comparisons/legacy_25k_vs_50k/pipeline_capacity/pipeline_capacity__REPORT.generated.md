# Evaluation pipeline capacity: Legacy 25K and 50K

1,152 fixed-policy screening rows; 5,148 reserve-search rows (overlap possible). 16 historical headline controls reproduced exactly. January 2020–July 2026 tape. $5,000 initial + $200/month, unless a budget sensitivity is explicitly shown.

## What was tested

- Main experiment keeps live funded accounts + activated spares + evaluations in flight within 20 seats. The separate seat sensitivity allows evaluations outside that cap; live + activated spares still cannot exceed 20. This is an explicit modelling sensitivity, not a claim about firm rules.
- Concurrent subscription caps: 2, 5, 10, 20. Starts: batch, at most one per calendar day, or one every seven calendar days. The stagger applies globally to new subscriptions; renewals keep their original monthly anniversary. Staggering also slows launch throughput and does not make the shared tape independent.
- Spare targets: 0, 2, 5, 10; these are desired inventory, not guaranteed stock. Demand-only replenishment starts evaluations while orders or spare deficits remain. No free starting inventory.
- Persistent demand queues missed monthly growth orders until filled. Death replacements take priority and consume the current month’s growth order. Older missed growth orders remain FIFO. Growth orders are not admitted while live accounts plus outstanding orders already cover 20 seats. Original day-only demand remains a control.
- Three withdrawal anchors are frozen before screening: each product’s historical instant-supply total winner, evaluation-supply total winner and evaluation-supply ongoing winner. All use monthly current-slot replacements.
- For every concurrency and seat mode, screen leaders under both objectives nominate pipelines. Both products then receive the same union of nominated pipelines plus the original pipeline, with minimum/maximum requests, daily/weekly/monthly cadence, and the configured reserve grid. Local refinements around both objectives are also paired. This is a staged search, not an exhaustive global optimum.

## Frozen aggressive policies: can expanded supply sustain them?

| Product / objective | Pipeline | Withdrawal / cushion above floor | Ongoing | Closing | Total | Funded / alive | Next-check service | Wait p95¹ | Unfilled account-days |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_25k / aggressive; shared seats | persistent, 20 evals, one/1d, 2 spares | maximum / weekly / $0 | $383,378 | $0 | $383,378 | 304 / 18 | 2.5% | 92.19 | 12,958 |
| legacy_25k / aggressive; evals outside cap | persistent, 20 evals, one/1d, 10 spares | maximum / weekly / $0 | $411,552 | $0 | $411,552 | 431 / 20 | 30.2% | 70.73 | 9,662 |
| legacy_50k / aggressive; shared seats | day-only, 20 evals, one/1d, 5 spares | maximum / daily / $600 | $376,271 | $0 | $376,271 | 207 / 8 | 2.5% | 125.16 | 9,620 |
| legacy_50k / aggressive; evals outside cap | day-only, 20 evals, one/1d, 10 spares | maximum / daily / $600 | $506,741 | $0 | $506,741 | 264 / 14 | 41.6% | 79.12 | 6,080 |

## Retuned winners with the original shared-seat cap

| Product / objective | Pipeline | Withdrawal / cushion above floor | Ongoing | Closing | Total | Funded / alive | Next-check service | Wait p95¹ | Unfilled account-days |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_25k / total | persistent, 20 evals, batch, 10 spares | minimum / calendar_month / $2,800 | $466,369 | $183,425 | $649,794 | 52 / 20 | 68.8% | 126.04 | 951 |
| legacy_25k / ongoing | persistent, 10 evals, batch, 10 spares | minimum / daily / $3,900 | $597,317 | $0 | $597,317 | 76 / 19 | 35.1% | 126.04 | 1,836 |
| legacy_50k / total | persistent, 20 evals, batch, 10 spares | minimum / calendar_month / $2,800 | $461,445 | $183,318 | $644,763 | 39 / 20 | 42.1% | 189.2 | 1,282 |
| legacy_50k / ongoing | persistent, 20 evals, one/1d, 2 spares | minimum / daily / $3,700 | $582,835 | $0 | $582,835 | 69 / 12 | 1.8% | 121.35 | 2,222 |

## Capacity frontier within shortlisted pipelines

### Shared 20 seats

| Product / objective | Pipeline | Withdrawal / cushion above floor | Ongoing | Closing | Total | Funded / alive | Next-check service | Wait p95¹ | Unfilled account-days |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_25k / total | day-only, 2 evals, one/1d, 10 spares | maximum / daily / $6,800 | $411,231 | $104,813 | $516,044 | 57 / 20 | 27.0% | 148.27 | 1,452 |
| legacy_25k / ongoing | day-only, 2 evals, batch, 2 spares | minimum / daily / $4,000 | $440,294 | $0 | $440,294 | 64 / 4 | 16.7% | 125.26 | 3,486 |
| legacy_25k / total | persistent, 5 evals, one/7d, 5 spares | maximum / daily / $7,900 | $493,047 | $120,332 | $613,379 | 61 / 20 | 36.6% | 130.04 | 1,845 |
| legacy_25k / ongoing | persistent, 5 evals, one/7d, 5 spares | minimum / daily / $4,000 | $547,571 | $0 | $547,571 | 74 / 6 | 22.1% | 130.04 | 3,749 |
| legacy_25k / total | persistent, 10 evals, batch, 10 spares | minimum / calendar_month / $2,800 | $465,346 | $183,011 | $648,357 | 51 / 20 | 64.5% | 130.04 | 1,041 |
| legacy_25k / ongoing | persistent, 10 evals, batch, 10 spares | minimum / daily / $3,900 | $597,317 | $0 | $597,317 | 76 / 19 | 35.1% | 126.04 | 1,836 |
| legacy_25k / total | persistent, 20 evals, batch, 10 spares | minimum / calendar_month / $2,800 | $466,369 | $183,425 | $649,794 | 52 / 20 | 68.8% | 126.04 | 951 |
| legacy_25k / ongoing | persistent, 20 evals, batch, 10 spares | minimum / daily / $3,000 | $592,090 | $0 | $592,090 | 99 / 20 | 29.1% | 126.04 | 2,366 |
| legacy_50k / total | day-only, 2 evals, one/7d, 5 spares | maximum / daily / $7,200 | $404,389 | $112,664 | $517,054 | 44 / 20 | 12.5% | 148.49 | 1,467 |
| legacy_50k / ongoing | day-only, 2 evals, batch, 5 spares | minimum / daily / $3,900 | $433,520 | $0 | $433,520 | 50 / 2 | 4.2% | 130.49 | 4,003 |
| legacy_50k / total | day-only, 5 evals, one/1d, 10 spares | maximum / daily / $6,800 | $516,934 | $99,842 | $616,775 | 41 / 20 | 42.9% | 93.24 | 706 |
| legacy_50k / ongoing | day-only, 5 evals, one/1d, 10 spares | minimum / daily / $4,000 | $548,345 | $0 | $548,345 | 51 / 4 | 19.1% | 94.24 | 2,864 |
| legacy_50k / total | persistent, 10 evals, one/1d, 2 spares | maximum / daily / $6,800 | $539,972 | $98,886 | $638,857 | 43 / 20 | 4.3% | 126.35 | 1,138 |
| legacy_50k / ongoing | persistent, 10 evals, one/1d, 2 spares | minimum / daily / $4,000 | $569,995 | $0 | $569,995 | 57 / 4 | 1.9% | 126.35 | 3,195 |
| legacy_50k / total | persistent, 20 evals, batch, 10 spares | minimum / calendar_month / $2,800 | $461,445 | $183,318 | $644,763 | 39 / 20 | 42.1% | 189.2 | 1,282 |
| legacy_50k / ongoing | persistent, 20 evals, one/1d, 2 spares | minimum / daily / $3,700 | $582,835 | $0 | $582,835 | 69 / 12 | 1.8% | 121.35 | 2,222 |

### Sensitivity: evaluations outside funded cap

| Product / objective | Pipeline | Withdrawal / cushion above floor | Ongoing | Closing | Total | Funded / alive | Next-check service | Wait p95¹ | Unfilled account-days |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_25k / total | day-only, 2 evals, one/1d, 10 spares | maximum / daily / $6,800 | $411,828 | $104,813 | $516,640 | 57 / 20 | 32.4% | 148.27 | 1,434 |
| legacy_25k / ongoing | day-only, 2 evals, batch, 2 spares | minimum / daily / $4,000 | $440,945 | $0 | $440,945 | 66 / 4 | 22.6% | 125.26 | 3,462 |
| legacy_25k / total | day-only, 5 evals, batch, 5 spares | maximum / daily / $7,100 | $507,567 | $105,769 | $613,336 | 57 / 20 | 51.3% | 130.04 | 1,265 |
| legacy_25k / ongoing | day-only, 5 evals, batch, 5 spares | minimum / daily / $4,000 | $550,593 | $0 | $550,593 | 84 / 10 | 32.4% | 126.04 | 2,826 |
| legacy_25k / total | persistent, 10 evals, batch, 10 spares | minimum / calendar_month / $2,800 | $464,054 | $183,206 | $647,260 | 55 / 20 | 68.6% | 126.04 | 711 |
| legacy_25k / ongoing | persistent, 10 evals, batch, 10 spares | minimum / daily / $3,000 | $590,984 | $0 | $590,984 | 123 / 10 | 53.1% | 62.02 | 2,204 |
| legacy_25k / total | persistent, 20 evals, batch, 10 spares | minimum / calendar_month / $2,800 | $465,695 | $182,641 | $648,336 | 58 / 20 | 68.4% | 48.04 | 558 |
| legacy_25k / ongoing | persistent, 20 evals, batch, 10 spares | minimum / daily / $3,000 | $597,252 | $0 | $597,252 | 113 / 20 | 54.8% | 62.02 | 1,792 |
| legacy_50k / total | day-only, 2 evals, one/7d, 5 spares | maximum / daily / $7,200 | $399,189 | $112,664 | $511,853 | 44 / 20 | 12.5% | 159.22 | 1,595 |
| legacy_50k / ongoing | day-only, 2 evals, one/7d, 5 spares | maximum / weekly / $5,000 | $431,080 | $0 | $431,080 | 51 / 6 | 17.8% | 159.22 | 3,211 |
| legacy_50k / total | day-only, 5 evals, one/1d, 10 spares | minimum / daily / $8,800 | $486,390 | $133,428 | $619,818 | 44 / 20 | 62.5% | 93.24 | 472 |
| legacy_50k / ongoing | day-only, 5 evals, one/1d, 10 spares | minimum / daily / $4,000 | $554,290 | $0 | $554,290 | 64 / 7 | 49.1% | 93.24 | 2,090 |
| legacy_50k / total | persistent, 10 evals, one/1d, 2 spares | minimum / calendar_month / $2,800 | $456,140 | $185,060 | $641,200 | 44 / 20 | 12.5% | 126.35 | 1,135 |
| legacy_50k / ongoing | persistent, 10 evals, batch, 10 spares | minimum / daily / $2,600 | $575,090 | $0 | $575,090 | 118 / 20 | 54.1% | 94.24 | 2,845 |
| legacy_50k / total | persistent, 20 evals, one/1d, 2 spares | maximum / daily / $6,800 | $544,216 | $98,886 | $643,102 | 42 / 20 | 4.5% | 123.35 | 830 |
| legacy_50k / ongoing | persistent, 20 evals, one/1d, 2 spares | minimum / daily / $3,700 | $585,745 | $0 | $585,745 | 71 / 12 | 8.5% | 121.35 | 2,191 |

## Budget sensitivity: selected main-study winners replayed without retuning

### $1,000 initial + $0/month

| Product / objective | Pipeline | Withdrawal / cushion above floor | Ongoing | Closing | Total | Funded / alive | Next-check service | Wait p95¹ | Unfilled account-days |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_25k / fixed | persistent, 20 evals, batch, 10 spares | minimum / calendar_month / $2,800 | $-983 | $0 | $-983 | 1 / 0 | 0.0% | None | 2,314 |
| legacy_25k / fixed | persistent, 10 evals, batch, 10 spares | minimum / daily / $3,900 | $-976 | $0 | $-976 | 2 / 0 | 0.0% | None | 4,628 |
| legacy_50k / fixed | persistent, 20 evals, batch, 10 spares | minimum / calendar_month / $2,800 | $-1,000 | $0 | $-1,000 | 0 / 0 | n/a | None | 0 |
| legacy_50k / fixed | persistent, 20 evals, one/1d, 2 spares | minimum / daily / $3,700 | $415,345 | $0 | $415,345 | 67 / 12 | 1.8% | 245.02 | 5,308 |

### $1,000 initial + $200/month

| Product / objective | Pipeline | Withdrawal / cushion above floor | Ongoing | Closing | Total | Funded / alive | Next-check service | Wait p95¹ | Unfilled account-days |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_25k / fixed | persistent, 20 evals, batch, 10 spares | minimum / calendar_month / $2,800 | $373,901 | $190,226 | $564,127 | 75 / 20 | 34.5% | 135.05 | 1,730 |
| legacy_25k / fixed | persistent, 10 evals, batch, 10 spares | minimum / daily / $3,900 | $505,943 | $0 | $505,943 | 91 / 19 | 29.2% | 117.02 | 2,375 |
| legacy_50k / fixed | persistent, 20 evals, batch, 10 spares | minimum / calendar_month / $2,800 | $388,400 | $189,135 | $577,535 | 56 / 20 | 8.3% | 271.02 | 3,471 |
| legacy_50k / fixed | persistent, 20 evals, one/1d, 2 spares | minimum / daily / $3,700 | $514,760 | $0 | $514,760 | 82 / 12 | 1.4% | 245.02 | 5,050 |

### $5,000 initial + $0/month

| Product / objective | Pipeline | Withdrawal / cushion above floor | Ongoing | Closing | Total | Funded / alive | Next-check service | Wait p95¹ | Unfilled account-days |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_25k / fixed | persistent, 20 evals, batch, 10 spares | minimum / calendar_month / $2,800 | $460,645 | $183,819 | $644,464 | 53 / 20 | 66.7% | 126.04 | 988 |
| legacy_25k / fixed | persistent, 10 evals, batch, 10 spares | minimum / daily / $3,900 | $522,299 | $0 | $522,299 | 103 / 20 | 20.5% | 189.21 | 4,100 |
| legacy_50k / fixed | persistent, 20 evals, batch, 10 spares | minimum / calendar_month / $2,800 | $381,805 | $189,226 | $571,031 | 55 / 20 | 22.9% | 337.02 | 3,616 |
| legacy_50k / fixed | persistent, 20 evals, one/1d, 2 spares | minimum / daily / $3,700 | $494,175 | $0 | $494,175 | 85 / 12 | 1.4% | 260.49 | 5,713 |

## How to interpret the service metrics

Next-check service is the fraction of actual account deaths replaced at the first daily decision at or after death. It is an observed service fraction, not a forward probability or a confidence estimate. ¹ Wait p95 includes only completed replacements; unresolved deaths are right-censored. Unfilled account-days includes both completed waits and unresolved waits through the tape horizon. See all_settings.csv for unresolved counts, oldest unresolved wait, average live accounts, zero-live days, subscription utilization and separate unaffordable activation, renewal and start counts. Cash-blocked counts can overlap other shortages and are diagnostics, not an additive attribution of profit loss.

All results are in-sample. Net cash excludes owner contributions and subtracts all evaluation and activation fees. Ongoing excludes the single permitted closing withdrawal. Funded account count is an outcome, not a decision variable. A 95% next-check service filter is reported only when reached by an observed candidate; this does not establish future reliability. The instant-supply historical result is a comparator under different timing/cost assumptions, not a mathematical upper bound.
