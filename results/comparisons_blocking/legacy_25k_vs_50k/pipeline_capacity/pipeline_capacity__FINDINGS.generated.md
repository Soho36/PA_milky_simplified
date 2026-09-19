# What expanded evaluation capacity changed — blocked copying

6,342 unique simulations, 16 reproduced historical controls. January 2020–July 2026; $5,000 initial + $200/month. Dollar figures are net of evaluation and activation fees, and exclude owner contributions. Main results retain the shared 20-seat cap.

**Execution: blocked copying.** Each funded account holds at most one position; an account still in an earlier trade skips a new signal. Compare the [non-blocking findings](../../../comparisons/legacy_25k_vs_50k/pipeline_capacity/pipeline_capacity__FINDINGS.generated.md).

The earlier 102/55 funded-account counts were outcomes of the winning withdrawal policies, not production ceilings. The original five-evaluation pipeline already supplied many more accounts under aggressive withdrawals. The relevant question is whether expanded supply makes that higher turnover timely and profitable enough to win.

## Does the old aggressive policy recover?

| Product | Historical instant supply | Original evaluation pipeline | Best tested expanded shared-seat pipeline | Best tested evaluations-outside-cap sensitivity |
|---|---:|---:|---:|---:|
| legacy_25k | $670,286 (539 accounts) | $164,807 (213 accounts) | $325,884 (262 accounts) | $408,808 (353 accounts) |
| legacy_50k | $603,596 (283 accounts) | $217,745 (121 accounts) | $335,443 (155 accounts) | $383,750 (206 accounts) |

The withdrawal policy is held fixed within each product. Expanded-pipeline columns select the best tested pipeline for that policy.

- legacy_25k, shared seats: 20 subscriptions; 1 per 1d; 0 spares; persistent. Evaluations outside cap: 20 subscriptions; 1 per 1d; 10 spares; persistent.
- legacy_50k, shared seats: 20 subscriptions; 1 per 1d; 2 spares; persistent. Evaluations outside cap: 20 subscriptions; 1 per 1d; 10 spares; day-only.

## Does the earlier $6,000–$7,000 daily reserve still appear?

| Product | Best tested daily-maximum cushion | Ongoing | Closing | Total | Funded accounts |
|---|---:|---:|---:|---:|---:|
| legacy_25k | $6,800 | $281,234 | $138,413 | $419,648 | 81 |
| legacy_50k | $6,800 | $373,504 | $136,597 | $510,101 | 49 |

These are the best tested **daily maximum** candidates, not the winners across all withdrawal families. Compare with the $6,000–$7,000 region found without blocking. These cushions belong to that particular withdrawal policy, not a universal reserve amount.


## What retuning selected

| Product / score | Pipeline | Withdrawal | Cushion above floor | Ongoing | Closing | Total | Funded / alive |
|---|---|---|---:|---:|---:|---:|---:|
| legacy_25k / total | 10 subscriptions; 1 per 1d; 5 spares; day-only | minimum / calendar_month | $1,700 | $330,912 | $166,658 | $497,570 | 93 / 20 |
| legacy_25k / ongoing | 20 subscriptions; batch; 2 spares; day-only | minimum / weekly | $2,400 | $453,544 | $0 | $453,544 | 117 / 20 |
| legacy_50k / total | 20 subscriptions; 1 per 1d; 2 spares; persistent | minimum / calendar_month | $0 | $345,090 | $173,593 | $518,683 | 66 / 20 |
| legacy_50k / ongoing | 20 subscriptions; 1 per 1d; 2 spares; persistent | minimum / weekly | $0 | $469,400 | $0 | $469,400 | 88 / 16 |

Cushion means profit above the frozen floor, not nominal account balance. The earlier 25K $31,900 threshold was a $6,800 cushion. It is a withdrawal threshold, not a target equity balance: minimum monthly withdrawals can let balances accumulate well above it. A smaller threshold under that policy is not the same as keeping a smaller actual cushion under daily maximum withdrawals. Funded-account counts are outcomes of each policy, not quantities the optimizer directly chose.

- legacy_25k / total: tested cushions $1,700, $1,800 are within $1 of the selected score at this same pipeline and withdrawal family. Do not interpret cent-level rankings as a unique optimum.
- legacy_50k / total: tested cushions $0, $100, $200, $300, $400, $500, $1,000, $2,000 are within $1 of the selected score at this same pipeline and withdrawal family. Do not interpret cent-level rankings as a unique optimum.
- legacy_50k / ongoing: tested cushions $0, $100, $200, $300, $400, $500, $1,000, $1,600, $1,700, $1,800, $1,900, $2,000 are within $1 of the selected score at this same pipeline and withdrawal family. Do not interpret cent-level rankings as a unique optimum.

## Replacement service of the selected total winners

| Product / seats | Next-check service | Deaths / unresolved | Completed wait median / p95 days | Unfilled account-days | Average live | Zero-live days | Cash-blocked days |
|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_25k / shared | 24.7% | 73 / 0 | 29.1 / 95.02 | 2,507 | 14.69 | 96.67 | 15 |
| legacy_25k / evals outside | 31.1% | 74 / 0 | 25.27 / 95.02 | 2,405 | 14.73 | 96.67 | 15 |
| legacy_50k / shared | 0.0% | 46 / 0 | 33.49 / 125.02 | 2,265 | 16.41 | 102.67 | 0 |
| legacy_50k / evals outside | 4.2% | 48 / 0 | 32.35 / 125.02 | 2,137 | 16.47 | 87.67 | 0 |

Completed-wait percentiles exclude unresolved replacements. Unfilled account-days includes every death’s wait until replacement or the horizon. Daily-state occupancy is sampled at decision boundaries; zero-live days includes startup.

## Matched changes at frozen withdrawal settings

These comparisons use the full screening matrix only. Each pair keeps product, withdrawal policy, seat mode, and all other pipeline settings fixed. Medians and win shares describe this grid, not probabilities of future improvement.

| Product | Seat mode | Change | Matched pairs | Median total change | Share improved |
|---|---|---|---:|---:|---:|
| legacy_25k | shared | persist missed demand | 144 | $-8,138 | 38% |
| legacy_25k | shared | batch → one/day | 96 | $-1,814 | 43% |
| legacy_25k | shared | batch → one/week | 96 | $-18,302 | 25% |
| legacy_25k | shared | 0 → 5 spares | 72 | $8,088 | 68% |
| legacy_25k | shared | 5 → 10 spares | 72 | $0 | 43% |
| legacy_25k | shared | 5 → 10 subscriptions | 72 | $28,305 | 93% |
| legacy_25k | shared | 10 → 20 subscriptions | 72 | $4,594 | 68% |
| legacy_25k | evals outside | persist missed demand | 144 | $-3,680 | 43% |
| legacy_25k | evals outside | batch → one/day | 96 | $-1,091 | 46% |
| legacy_25k | evals outside | batch → one/week | 96 | $-18,270 | 23% |
| legacy_25k | evals outside | 0 → 5 spares | 72 | $45,198 | 83% |
| legacy_25k | evals outside | 5 → 10 spares | 72 | $2,683 | 56% |
| legacy_25k | evals outside | 5 → 10 subscriptions | 72 | $29,583 | 96% |
| legacy_25k | evals outside | 10 → 20 subscriptions | 72 | $5,755 | 68% |
| legacy_50k | shared | persist missed demand | 144 | $2,598 | 66% |
| legacy_50k | shared | batch → one/day | 96 | $1,283 | 57% |
| legacy_50k | shared | batch → one/week | 96 | $-13,275 | 18% |
| legacy_50k | shared | 0 → 5 spares | 72 | $20,066 | 62% |
| legacy_50k | shared | 5 → 10 spares | 72 | $-1,709 | 11% |
| legacy_50k | shared | 5 → 10 subscriptions | 72 | $23,282 | 99% |
| legacy_50k | shared | 10 → 20 subscriptions | 72 | $8,745 | 83% |
| legacy_50k | evals outside | persist missed demand | 144 | $2,209 | 65% |
| legacy_50k | evals outside | batch → one/day | 96 | $1,329 | 57% |
| legacy_50k | evals outside | batch → one/week | 96 | $-6,347 | 28% |
| legacy_50k | evals outside | 0 → 5 spares | 72 | $52,144 | 74% |
| legacy_50k | evals outside | 5 → 10 spares | 72 | $-865 | 31% |
| legacy_50k | evals outside | 5 → 10 subscriptions | 72 | $24,800 | 97% |
| legacy_50k | evals outside | 10 → 20 subscriptions | 72 | $7,522 | 79% |

## Did any tested aggressive pipeline reach 95% next-check service?

- legacy_25k, shared seats: no tested candidate reached 95%.
- legacy_25k, evaluations outside the cap: no tested candidate reached 95%.
- legacy_50k, shared seats: no tested candidate reached 95%.
- legacy_50k, evaluations outside the cap: no tested candidate reached 95%.

This is realized service against each policy’s own deaths. Starvation changes which accounts exist and therefore which deaths occur; it is not a replay of a fixed external replacement-demand stream or a forecast of 95% reliability.

## Smaller-budget checks

Selected shared-seat winners were replayed without retuning at the other three budgets. The following are replays of the **total-score** winners, not new budget-specific optima.

| Product | $1,000 + $0/month | $1,000 + $200/month | $5,000 + $0/month |
|---|---:|---:|---:|
| legacy_25k | $-997 (7 funded) | $416,583 (102 funded) | $-4,977 (27 funded) |
| legacy_50k | $-1,000 (4 funded) | $473,468 (63 funded) | $-4,970 (22 funded) |

These replays are not re-optimized for the smaller budgets; compare them with the budget-specific winners of the evaluation-supply study. The full budget table is in pipeline_capacity__REPORT.generated.md and budget_sensitivity.csv.

## Limits and reproducibility

The pipeline search screens three historical anchors before retuning a matched shortlist. It can miss a pipeline that needs an entirely different withdrawal policy to perform well. The same tape and starting date are used throughout. Different budgets are sensitivity replays, not independent samples. Increasing concurrency need not improve profit: it changes cohort timing, fees and the seats available to funded accounts. No constant-capacity, independent-pass or monotone-profit assumption is warranted.

See [full generated report](pipeline_capacity__REPORT.generated.md), [capacity table](frontier.csv), [screening rows](screening.csv), [all settings](all_settings.csv), [audit](AUDIT.json), and [run contract](contract.json). Rebuild this note with `venv/Scripts/python.exe scripts/explain_legacy_pipeline_capacity.py results/comparisons_blocking/legacy_25k_vs_50k/pipeline_capacity`.
