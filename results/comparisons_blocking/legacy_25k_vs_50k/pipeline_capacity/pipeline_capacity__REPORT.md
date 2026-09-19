# Evaluation pipeline capacity: Legacy 25K and 50K — blocked copying

1,152 fixed-policy screening rows; 5,316 reserve-search rows (overlap possible). 16 historical headline controls reproduced exactly, including per-trade account assignments. January 2020–July 2026 tape. $5,000 initial + $200/month, unless a budget sensitivity is explicitly shown.

**Execution: blocked copying.** Each funded account holds at most one position; an account still in an earlier trade skips a new signal. Evaluations trade one position at a time, as before. The anchors and controls come from the [blocked evaluation-supply](../eval_supply/eval_supply__REPORT.md) and [blocked reserve](../reserve_by_policy/reserve_by_policy__REPORT.md) studies. Everything else matches the [non-blocking pipeline study](../../../comparisons/legacy_25k_vs_50k/pipeline_capacity/pipeline_capacity__REPORT.md).

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
| legacy_25k / aggressive; shared seats | persistent, 20 evals, one/1d, 0 spares | maximum / weekly / $0 | $325,884 | $0 | $325,884 | 262 / 11 | 0.0% | 87.6 | 10,228 |
| legacy_25k / aggressive; evals outside cap | persistent, 20 evals, one/1d, 10 spares | maximum / weekly / $0 | $408,808 | $0 | $408,808 | 353 / 18 | 36.4% | 59.02 | 6,716 |
| legacy_50k / aggressive; shared seats | persistent, 20 evals, one/1d, 2 spares | maximum / daily / $0 | $335,443 | $0 | $335,443 | 155 / 5 | 0.7% | 126.22 | 7,965 |
| legacy_50k / aggressive; evals outside cap | day-only, 20 evals, one/1d, 10 spares | maximum / daily / $0 | $383,750 | $0 | $383,750 | 206 / 5 | 39.3% | 73.22 | 4,237 |

## Retuned winners with the original shared-seat cap

| Product / objective | Pipeline | Withdrawal / cushion above floor | Ongoing | Closing | Total | Funded / alive | Next-check service | Wait p95¹ | Unfilled account-days |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_25k / total | day-only, 10 evals, one/1d, 5 spares | minimum / calendar_month / $1,700 | $330,912 | $166,658 | $497,570 | 93 / 20 | 24.7% | 95.02 | 2,507 |
| legacy_25k / ongoing | day-only, 20 evals, batch, 2 spares | minimum / weekly / $2,400 | $453,544 | $0 | $453,544 | 117 / 20 | 9.3% | 69.51 | 2,487 |
| legacy_50k / total | persistent, 20 evals, one/1d, 2 spares | minimum / calendar_month / $0 | $345,090 | $173,593 | $518,683 | 66 / 20 | 0.0% | 125.02 | 2,265 |
| legacy_50k / ongoing | persistent, 20 evals, one/1d, 2 spares | minimum / weekly / $0 | $469,400 | $0 | $469,400 | 88 / 16 | 0.0% | 125.02 | 3,792 |

## Capacity frontier within shortlisted pipelines

### Shared 20 seats

| Product / objective | Pipeline | Withdrawal / cushion above floor | Ongoing | Closing | Total | Funded / alive | Next-check service | Wait p95¹ | Unfilled account-days |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_25k / total | day-only, 2 evals, batch, 2 spares | maximum / weekly / $6,400 | $312,669 | $104,697 | $417,366 | 59 / 20 | 25.6% | 188.02 | 2,618 |
| legacy_25k / ongoing | day-only, 2 evals, one/1d, 2 spares | minimum / daily / $3,000 | $322,024 | $0 | $322,024 | 69 / 4 | 13.9% | 143.23 | 4,939 |
| legacy_25k / total | day-only, 5 evals, batch, 2 spares | minimum / calendar_month / $1,700 | $319,845 | $167,191 | $487,036 | 83 / 20 | 12.7% | 136.02 | 3,170 |
| legacy_25k / ongoing | day-only, 5 evals, batch, 2 spares | minimum / weekly / $1,900 | $434,650 | $0 | $434,650 | 98 / 10 | 9.1% | 186.2 | 5,293 |
| legacy_25k / total | day-only, 10 evals, one/1d, 5 spares | minimum / calendar_month / $1,700 | $330,912 | $166,658 | $497,570 | 93 / 20 | 24.7% | 95.02 | 2,507 |
| legacy_25k / ongoing | day-only, 10 evals, one/1d, 10 spares | minimum / weekly / $1,900 | $446,164 | $0 | $446,164 | 127 / 12 | 20.0% | 101.6 | 4,426 |
| legacy_25k / total | day-only, 20 evals, batch, 2 spares | minimum / calendar_month / $0 | $345,361 | $149,592 | $494,953 | 145 / 20 | 8.0% | 79.12 | 3,698 |
| legacy_25k / ongoing | day-only, 20 evals, batch, 2 spares | minimum / weekly / $2,400 | $453,544 | $0 | $453,544 | 117 / 20 | 9.3% | 69.51 | 2,487 |
| legacy_50k / total | day-only, 2 evals, one/1d, 2 spares | minimum / calendar_month / $0 | $280,685 | $163,919 | $444,604 | 43 / 20 | 4.3% | 260.38 | 3,474 |
| legacy_50k / ongoing | day-only, 2 evals, one/1d, 2 spares | minimum / daily / $2,900 | $364,795 | $871 | $365,666 | 49 / 3 | 2.2% | 246.5 | 5,707 |
| legacy_50k / total | day-only, 5 evals, one/1d, 10 spares | minimum / calendar_month / $0 | $318,465 | $173,534 | $491,999 | 55 / 20 | 20.0% | 162.08 | 2,360 |
| legacy_50k / ongoing | day-only, 5 evals, one/1d, 2 spares | minimum / weekly / $0 | $426,800 | $0 | $426,800 | 64 / 6 | 1.7% | 189.02 | 4,845 |
| legacy_50k / total | day-only, 10 evals, batch, 2 spares | minimum / calendar_month / $0 | $333,390 | $175,027 | $508,417 | 50 / 20 | 3.3% | 130.02 | 2,524 |
| legacy_50k / ongoing | persistent, 10 evals, batch, 2 spares | minimum / weekly / $0 | $446,665 | $0 | $446,665 | 75 / 20 | 0.0% | 193.02 | 5,381 |
| legacy_50k / total | persistent, 20 evals, one/1d, 2 spares | minimum / calendar_month / $0 | $345,090 | $173,593 | $518,683 | 66 / 20 | 0.0% | 125.02 | 2,265 |
| legacy_50k / ongoing | persistent, 20 evals, one/1d, 2 spares | minimum / weekly / $0 | $469,400 | $0 | $469,400 | 88 / 16 | 0.0% | 125.02 | 3,792 |

### Sensitivity: evaluations outside funded cap

| Product / objective | Pipeline | Withdrawal / cushion above floor | Ongoing | Closing | Total | Funded / alive | Next-check service | Wait p95¹ | Unfilled account-days |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_25k / total | day-only, 2 evals, batch, 2 spares | maximum / weekly / $6,400 | $312,504 | $104,697 | $417,201 | 59 / 20 | 25.6% | 188.02 | 2,618 |
| legacy_25k / ongoing | day-only, 2 evals, one/1d, 2 spares | minimum / daily / $3,000 | $321,543 | $0 | $321,543 | 71 / 4 | 16.4% | 143.23 | 4,924 |
| legacy_25k / total | day-only, 5 evals, batch, 2 spares | minimum / calendar_month / $1,700 | $320,746 | $167,606 | $488,352 | 83 / 20 | 15.9% | 136.02 | 3,074 |
| legacy_25k / ongoing | day-only, 5 evals, batch, 2 spares | minimum / weekly / $1,900 | $429,669 | $0 | $429,669 | 104 / 10 | 12.8% | 186.2 | 5,108 |
| legacy_25k / total | day-only, 10 evals, one/1d, 5 spares | minimum / calendar_month / $1,700 | $333,391 | $167,092 | $500,483 | 94 / 20 | 31.1% | 95.02 | 2,405 |
| legacy_25k / ongoing | persistent, 10 evals, batch, 10 spares | minimum / weekly / $1,900 | $450,928 | $0 | $450,928 | 139 / 20 | 42.9% | 120.02 | 3,975 |
| legacy_25k / total | day-only, 20 evals, batch, 2 spares | minimum / calendar_month / $0 | $349,045 | $150,007 | $499,052 | 143 / 20 | 13.0% | 79.12 | 3,557 |
| legacy_25k / ongoing | day-only, 20 evals, batch, 2 spares | minimum / weekly / $2,400 | $457,721 | $0 | $457,721 | 118 / 20 | 11.2% | 55.51 | 2,444 |
| legacy_50k / total | day-only, 2 evals, one/1d, 2 spares | minimum / calendar_month / $0 | $280,605 | $163,919 | $444,524 | 43 / 20 | 4.3% | 260.38 | 3,474 |
| legacy_50k / ongoing | day-only, 2 evals, one/1d, 2 spares | minimum / daily / $2,900 | $364,465 | $871 | $365,336 | 51 / 3 | 6.2% | 246.5 | 5,675 |
| legacy_50k / total | day-only, 5 evals, one/1d, 10 spares | minimum / calendar_month / $0 | $317,720 | $173,693 | $491,413 | 64 / 20 | 36.4% | 92.35 | 1,782 |
| legacy_50k / ongoing | day-only, 5 evals, one/1d, 2 spares | minimum / weekly / $0 | $425,390 | $0 | $425,390 | 66 / 6 | 5.0% | 189.02 | 4,813 |
| legacy_50k / total | day-only, 10 evals, batch, 2 spares | minimum / calendar_month / $0 | $332,710 | $175,027 | $507,737 | 50 / 20 | 3.3% | 130.02 | 2,524 |
| legacy_50k / ongoing | persistent, 10 evals, batch, 2 spares | minimum / weekly / $0 | $446,385 | $0 | $446,385 | 79 / 20 | 6.8% | 193.02 | 5,242 |
| legacy_50k / total | persistent, 20 evals, one/1d, 2 spares | minimum / calendar_month / $0 | $346,600 | $173,215 | $519,815 | 68 / 20 | 4.2% | 125.02 | 2,137 |
| legacy_50k / ongoing | day-only, 20 evals, one/1d, 10 spares | minimum / weekly / $0 | $469,960 | $0 | $469,960 | 116 / 20 | 32.3% | 59.16 | 1,960 |

## Budget sensitivity: selected main-study winners replayed without retuning

### $1,000 initial + $0/month

| Product / objective | Pipeline | Withdrawal / cushion above floor | Ongoing | Closing | Total | Funded / alive | Next-check service | Wait p95¹ | Unfilled account-days |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_25k / fixed | day-only, 10 evals, one/1d, 5 spares | minimum / calendar_month / $1,700 | $-997 | $0 | $-997 | 7 / 0 | 42.9% | 0.3 | 7,747 |
| legacy_25k / fixed | day-only, 20 evals, batch, 2 spares | minimum / weekly / $2,400 | $-990 | $0 | $-990 | 12 / 0 | 33.3% | 11.02 | 9,493 |
| legacy_50k / fixed | persistent, 20 evals, one/1d, 2 spares | minimum / calendar_month / $0 | $-1,000 | $0 | $-1,000 | 4 / 0 | 0.0% | None | 7,737 |
| legacy_50k / fixed | persistent, 20 evals, one/1d, 2 spares | minimum / weekly / $0 | $-990 | $0 | $-990 | 6 / 0 | 0.0% | None | 11,742 |

### $1,000 initial + $200/month

| Product / objective | Pipeline | Withdrawal / cushion above floor | Ongoing | Closing | Total | Funded / alive | Next-check service | Wait p95¹ | Unfilled account-days |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_25k / fixed | day-only, 10 evals, one/1d, 5 spares | minimum / calendar_month / $1,700 | $258,188 | $158,395 | $416,583 | 102 / 20 | 23.2% | 206.21 | 5,783 |
| legacy_25k / fixed | day-only, 20 evals, batch, 2 spares | minimum / weekly / $2,400 | $342,127 | $0 | $342,127 | 106 / 20 | 7.0% | 333.11 | 8,369 |
| legacy_50k / fixed | persistent, 20 evals, one/1d, 2 spares | minimum / calendar_month / $0 | $300,665 | $172,803 | $473,468 | 63 / 20 | 4.7% | 306.35 | 5,575 |
| legacy_50k / fixed | persistent, 20 evals, one/1d, 2 spares | minimum / weekly / $0 | $444,000 | $0 | $444,000 | 88 / 16 | 0.0% | 292.35 | 6,623 |

### $5,000 initial + $0/month

| Product / objective | Pipeline | Withdrawal / cushion above floor | Ongoing | Closing | Total | Funded / alive | Next-check service | Wait p95¹ | Unfilled account-days |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_25k / fixed | day-only, 10 evals, one/1d, 5 spares | minimum / calendar_month / $1,700 | $-4,977 | $0 | $-4,977 | 27 / 0 | 33.3% | 45.02 | 21,046 |
| legacy_25k / fixed | day-only, 20 evals, batch, 2 spares | minimum / weekly / $2,400 | $-4,975 | $0 | $-4,975 | 32 / 0 | 15.6% | 119.02 | 18,946 |
| legacy_50k / fixed | persistent, 20 evals, one/1d, 2 spares | minimum / calendar_month / $0 | $-4,970 | $0 | $-4,970 | 22 / 0 | 0.0% | 14.02 | 28,466 |
| legacy_50k / fixed | persistent, 20 evals, one/1d, 2 spares | minimum / weekly / $0 | $-4,970 | $0 | $-4,970 | 22 / 0 | 0.0% | 14.02 | 28,562 |

## How to interpret the service metrics

Next-check service is the fraction of actual account deaths replaced at the first daily decision at or after death. It is an observed service fraction, not a forward probability or a confidence estimate. ¹ Wait p95 includes only completed replacements; unresolved deaths are right-censored. Unfilled account-days includes both completed waits and unresolved waits through the tape horizon. See all_settings.csv for unresolved counts, oldest unresolved wait, average live accounts, zero-live days, subscription utilization and separate unaffordable activation, renewal and start counts. Cash-blocked counts can overlap other shortages and are diagnostics, not an additive attribution of profit loss.

All results are in-sample. Net cash excludes owner contributions and subtracts all evaluation and activation fees. Ongoing excludes the single permitted closing withdrawal. Funded account count is an outcome, not a decision variable. A 95% next-check service filter is reported only when reached by an observed candidate; this does not establish future reliability. The instant-supply historical result is a comparator under different timing/cost assumptions, not a mathematical upper bound.
