# What realistic supply changes for blocked copying

**$1,000 initial + $200/month, Legacy25K, January 2020–July 2026.** Every free PA copies; busy PAs skip. Net cash excludes owner contributions and includes every procurement fee.

The instant-supply aggressive co-winner earned **$665,420.55**. With the same maximum-weekly withdrawal rule and $25,100 reserve, the original evaluation pipeline earns **$166,430.85**. Searching pipeline capacity while keeping that withdrawal rule fixed raises it to **$325,362.25** under the shared 20-seat cap (-51.1% against instant supply). Allowing evaluations outside the cap gives **$413,381.50**.

## Main comparison

| Case | Ongoing net | Terminal payout | Total net | Funded / deaths | All fees |
|---|---:|---:|---:|---:|---:|
| Instant aggressive control | $665,420.55 | $0.00 | $665,420.55 | 531 / 511 | $106,200.00 |
| Original supply / frozen aggressive | $166,430.85 | $0.00 | $166,430.85 | 215 / 205 | $40,042.00 |
| Best shared supply / frozen aggressive | $325,362.25 | $0.00 | $325,362.25 | 256 / 245 | $49,127.00 |
| Best shared ongoing / retuned | $444,839.00 | $0.00 | $444,839.00 | 92 / 87 | $18,661.00 |
| Best shared total / retuned | $300,165.00 | $150,161.65 | $450,326.65 | 114 / 94 | $22,335.00 |
| Outside-cap supply / frozen aggressive | $413,381.50 | $0.00 | $413,381.50 | 344 / 326 | $67,519.00 |

Instant supply starts one paid PA at a $200 purchase fee. Evaluation supply starts with no PAs and pays $33 per evaluation subscription month plus $125 per activated PA. Thus the comparison includes changed fees and startup as well as replacement delays. Persistent demand also carries missed monthly growth orders forward; the original pipeline lets them expire.

## What the selected shared-cap policies do

**Ongoing cash:** minimum  withdrawals checked weekly, retaining $26,900. Pipeline: day-only, 5 evals, batch, 10 spares. It averages 13.03 live PAs, takes 121,235 trade copies and participates in 66.39% of signals. 28.7% of deaths are replaced at the next daily check; completed waits have a median of 21.23 days and p95 of 123.02 days. 15 replacements remain unresolved at the horizon. Zero-live time is 220.67 days, including startup.

**Terminal-inclusive cash:** minimum  withdrawals checked calendar_month, retaining $25,100. Pipeline: persistent, 20 evals, one/1d, 0 spares. It averages 12.24 live PAs, takes 114,877 trade copies and participates in 69.69% of signals. 0.0% of deaths are replaced at the next daily check; completed waits have a median of 48.09 days and p95 of 166.05 days. 0 replacements remain unresolved at the horizon. Zero-live time is 124.67 days, including startup.

Retuning improves ongoing cash by **$119,476.75** over the best shared-cap frozen aggressive pipeline. The total-cash leader's **$150,161.65** terminal receipt should not be treated as recurring withdrawal income.

The ongoing winner gives up only **$5,487.65** of total cash while delivering **$144,674.00** more during the run. This is a more useful operating trade-off than selecting the terminal-inclusive winner solely by its final score. The spare number is a target, not guaranteed inventory; the ongoing winner ends with no spares and five live PAs.

## The exact reserve is sensitive

| Retained balance, same ongoing-winner pipeline | Ongoing cash | Deaths |
|---:|---:|---:|
| $26,700 | $328,107.00 | 146 |
| $26,800 | $349,477.00 | 135 |
| $26,900 | $444,839.00 | 87 |
| $27,000 | $430,259.00 | 92 |
| $27,100 | $342,512.00 | 112 |

These discontinuities mean $26,900 is a historical search winner, not a robust universal optimum. Reserve changes alter withdrawals, failures and the timing of subsequent evaluation cohorts. The frozen ongoing policy earns $384,215 with $5,000 + $200/month, below its primary-budget result; more starting capital does not guarantee a better path for a fixed policy. With $1,000 and no monthly funding, both main winners exhaust their usable accounts.

## Replaying the same policies without PA blocking

| Case | Pipeline | Withdrawal / reserve | Ongoing | Closing | Total | Funded / deaths | Copies | Coverage |
|---|---|---|---:|---:|---:|---:|---:|---:|
| shared / ongoing / blocked | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $444,839.00 | $0.00 | $444,839.00 | 92 / 87 | 121,235 | 66.39% |
| shared / ongoing / unrestricted | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $449,833.00 | $0.00 | $449,833.00 | 133 / 128 | 161,360 | n/a |
| shared / total / blocked | persistent, 20 evals, one/1d, 0 spares | minimum  / calendar_month / $25,100 | $300,165.00 | $150,161.65 | $450,326.65 | 114 / 94 | 114,877 | 69.69% |
| shared / total / unrestricted | persistent, 20 evals, one/1d, 0 spares | minimum  / calendar_month / $25,100 | $354,656.00 | $160,184.27 | $514,840.27 | 86 / 66 | 160,612 | n/a |
| outside cap / ongoing / blocked | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $448,922.00 | $0.00 | $448,922.00 | 101 / 96 | 122,463 | 66.63% |
| outside cap / ongoing / unrestricted | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $515,725.00 | $0.00 | $515,725.00 | 143 / 138 | 170,971 | n/a |
| outside cap / total / blocked | day-only, 10 evals, one/1d, 10 spares | minimum  / calendar_month / $25,100 | $308,009.00 | $152,699.50 | $460,708.50 | 151 / 131 | 129,606 | 69.91% |
| outside cap / total / unrestricted | day-only, 10 evals, one/1d, 10 spares | minimum  / calendar_month / $25,100 | $378,909.00 | $163,772.04 | $542,681.04 | 83 / 63 | 166,292 | n/a |

Across all 768 frozen-policy pairs, blocked copying earns more total net cash in 188. Unrestricted copying is therefore not a mathematical upper bound on cash.

These are paired policy replays under identical procurement rules and funding, not independently optimized unrestricted benchmarks. Trade coverage alone does not determine the cash ranking; execution changes PA deaths, receipts and subsequent supply demand.

## Capacity frontier after the staged search

| Case | Pipeline | Withdrawal / reserve | Ongoing | Closing | Total | Funded / deaths | Copies | Coverage |
|---|---|---|---:|---:|---:|---:|---:|---:|
| shared / 2 evals / ongoing | day-only, 2 evals, batch, 2 spares | minimum  / daily / $29,000 | $319,288.00 | $0.00 | $319,288.00 | 65 / 63 | 89,569 | 70.79% |
| shared / 2 evals / total | day-only, 2 evals, batch, 2 spares | fixed 1500 / weekly / $31,500 | $312,669.45 | $104,696.71 | $417,366.16 | 59 / 39 | 98,092 | 71.69% |
| shared / 5 evals / ongoing | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $444,839.00 | $0.00 | $444,839.00 | 92 / 87 | 121,235 | 66.39% |
| shared / 5 evals / total | day-only, 5 evals, batch, 5 spares | minimum  / calendar_month / $29,700 | $242,592.00 | $202,723.38 | $445,315.38 | 66 / 46 | 111,409 | 71.66% |
| shared / 10 evals / ongoing | persistent, 10 evals, one/7d, 5 spares | minimum  / weekly / $27,000 | $392,498.00 | $0.00 | $392,498.00 | 109 / 103 | 115,900 | 68.87% |
| shared / 10 evals / total | persistent, 10 evals, one/7d, 2 spares | fixed 1500 / weekly / $31,500 | $340,899.20 | $104,323.83 | $445,223.03 | 63 / 43 | 106,839 | 72.18% |
| shared / 20 evals / ongoing | persistent, 20 evals, one/1d, 0 spares | minimum  / weekly / $27,200 | $412,653.00 | $0.00 | $412,653.00 | 109 / 95 | 113,751 | 68.83% |
| shared / 20 evals / total | persistent, 20 evals, one/1d, 0 spares | minimum  / calendar_month / $25,100 | $300,165.00 | $150,161.65 | $450,326.65 | 114 / 94 | 114,877 | 69.69% |
| outside / 2 evals / ongoing | day-only, 2 evals, batch, 2 spares | minimum  / daily / $29,000 | $318,873.00 | $0.00 | $318,873.00 | 67 / 65 | 89,635 | 70.87% |
| outside / 2 evals / total | day-only, 2 evals, batch, 2 spares | fixed 1500 / weekly / $31,500 | $312,504.45 | $104,696.71 | $417,201.16 | 59 / 39 | 98,092 | 71.69% |
| outside / 5 evals / ongoing | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $448,922.00 | $0.00 | $448,922.00 | 101 / 96 | 122,463 | 66.63% |
| outside / 5 evals / total | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $448,922.00 | $0.00 | $448,922.00 | 101 / 96 | 122,463 | 66.63% |
| outside / 10 evals / ongoing | day-only, 10 evals, one/1d, 10 spares | minimum  / weekly / $26,900 | $444,768.00 | $0.00 | $444,768.00 | 135 / 121 | 124,537 | 68.77% |
| outside / 10 evals / total | day-only, 10 evals, one/1d, 10 spares | minimum  / calendar_month / $25,100 | $308,009.00 | $152,699.50 | $460,708.50 | 151 / 131 | 129,606 | 69.91% |
| outside / 20 evals / ongoing | persistent, 20 evals, one/1d, 10 spares | maximum  / weekly / $25,700 | $414,718.60 | $0.00 | $414,718.60 | 344 / 326 | 130,724 | 70.19% |
| outside / 20 evals / total | persistent, 20 evals, one/7d, 10 spares | minimum  / calendar_month / $29,600 | $244,166.00 | $204,755.38 | $448,921.38 | 65 / 45 | 108,973 | 72.25% |

## Historical sensitivity without retuning

| Case | Pipeline | Withdrawal / reserve | Ongoing | Closing | Total | Funded / deaths | Copies | Coverage |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 2020 / $1000+$0/mo | persistent, 20 evals, one/1d, 0 spares | minimum  / calendar_month / $25,100 | $-976.00 | $0.00 | $-976.00 | 6 / 6 | 2,000 | 10.11% |
| 2020 / $1000+$0/mo | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $-980.00 | $0.00 | $-980.00 | 20 / 20 | 7,317 | 13.40% |
| 2020 / $5000+$0/mo | persistent, 20 evals, one/1d, 0 spares | minimum  / calendar_month / $25,100 | $-4,968.00 | $0.00 | $-4,968.00 | 29 / 29 | 9,589 | 12.11% |
| 2020 / $5000+$0/mo | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $432,787.00 | $0.00 | $432,787.00 | 86 / 81 | 117,954 | 66.39% |
| 2020 / $5000+$200/mo | persistent, 20 evals, one/1d, 0 spares | minimum  / calendar_month / $25,100 | $302,282.00 | $150,301.30 | $452,583.30 | 149 / 129 | 130,525 | 68.21% |
| 2020 / $5000+$200/mo | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $384,215.00 | $0.00 | $384,215.00 | 131 / 121 | 118,578 | 65.64% |
| 2021 / $1000+$200/mo | persistent, 20 evals, one/1d, 0 spares | minimum  / calendar_month / $25,100 | $299,442.00 | $150,085.75 | $449,527.75 | 86 / 66 | 106,246 | 69.36% |
| 2021 / $1000+$200/mo | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $434,123.00 | $0.00 | $434,123.00 | 65 / 60 | 108,131 | 68.03% |
| 2022 / $1000+$200/mo | persistent, 20 evals, one/1d, 0 spares | minimum  / calendar_month / $25,100 | $284,443.00 | $147,947.75 | $432,390.75 | 53 / 33 | 89,902 | 70.42% |
| 2022 / $1000+$200/mo | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $366,894.00 | $0.00 | $366,894.00 | 66 / 57 | 84,649 | 70.29% |
| 2023 / $1000+$200/mo | persistent, 20 evals, one/1d, 0 spares | minimum  / calendar_month / $25,100 | $225,520.00 | $116,537.80 | $342,057.80 | 36 / 16 | 71,946 | 69.14% |
| 2023 / $1000+$200/mo | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $232,747.00 | $0.00 | $232,747.00 | 54 / 35 | 65,263 | 68.48% |
| 2024 / $1000+$200/mo | persistent, 20 evals, one/1d, 0 spares | minimum  / calendar_month / $25,100 | $91,273.00 | $47,128.30 | $138,401.30 | 53 / 37 | 41,267 | 71.84% |
| 2024 / $1000+$200/mo | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $113,318.00 | $0.00 | $113,318.00 | 62 / 47 | 43,579 | 69.97% |
| 2025 / $1000+$200/mo | persistent, 20 evals, one/1d, 0 spares | minimum  / calendar_month / $25,100 | $5,867.00 | $13,500.00 | $19,367.00 | 37 / 27 | 14,621 | 60.81% |
| 2025 / $1000+$200/mo | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $11,377.00 | $0.00 | $11,377.00 | 41 / 36 | 8,891 | 53.86% |

Later starts overlap the full-tape selection history. They are fresh-account historical replays, not forward or unseen validation. Other funding budgets keep the selected policy unchanged.

## Search resolution and evidence

- shared / ongoing: 1 tested settings tie on the primary objective. Within the selected pipeline/withdrawal family, tested reserves within $1 of that score: $26,900.
- shared / total: 7 tested settings tie on the primary objective. Within the selected pipeline/withdrawal family, tested reserves within $1 of that score: $25,100, $25,200, $25,300, $25,400, $25,500, $25,600, $26,100.
- outside cap / ongoing: 1 tested settings tie on the primary objective. Within the selected pipeline/withdrawal family, tested reserves within $1 of that score: $26,900.
- outside cap / total: 7 tested settings tie on the primary objective. Within the selected pipeline/withdrawal family, tested reserves within $1 of that score: $25,100, $25,200, $25,300, $25,400, $25,500, $25,600, $26,100.

4,896 unique runs, including controls within the new checkpoint, paired execution screens and frozen transfers. Three earlier headline controls separately reproduce exactly. The audit independently checks 728,903 selected PA trade assignments across 6 detailed ledgers, including no overlap, paid activation provenance, cash, fees, seat caps and search-domain completeness. The existing 279-test suite and the new evaluation-plus-blocking timeline test pass.

This is the best result within a staged search, not a global optimum. The main procurement family is current-slot monthly growth plus replacement; other acquisition families are not reoptimized. All supply assumptions are inherited, including indefinite waiting for activation, no spare expiry and no payout-processing delay. The outside-cap arm is a sensitivity, not a statement about firm rules. Evaluation launch dates share the tape and do not create independent pass probabilities.

[Full generated report](blocked_pipeline__REPORT.generated.md), [all settings](all_settings.csv), [independent audit](AUDIT.generated.json), [study protocol](../../../research/legacy_25k/BLOCKED_PIPELINE.md).
