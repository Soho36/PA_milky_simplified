# Blocked copying with evaluation supply

**Legacy25K; $1,000 initial + $200/month; January 2020–July 2026.** One MNQ per free funded account; occupied accounts skip new setups. No free starting PAs: every funded account must pass an evaluation and pay activation. Same evaluation model as the earlier pipeline-capacity study: 3 MNQ, $1,500 target/drawdown, $33 per subscription month and $125 activation. These are inherited study assumptions, not newly verified firm terms.

Main capacity: live PAs + activated spares + in-flight evaluations <=20. The separate outside-cap sensitivity excludes evaluations only. Concurrency is 2/5/10/20; launches batch/one per day/one per seven days; spare targets 0/2/5/10. Current-slot monthly growth/replacement demand is held fixed; missed growth demand either expires or persists as a FIFO queue. Death replacements have priority. Renewals, failed evaluations, cash shortages, pass delays and dormant activated spares all cost time or money.

## Frozen aggressive policy: supply impact

The instant-supply current-slot + maximum-weekly co-winner retained $25,100, started with one paid PA, and produced **$665,420.55**, 531 purchases and 511 deaths. The evaluation rows below retain its withdrawal and current-slot purchase rules. They change procurement fees, lead time and initial inventory; persistent rows additionally change how missed monthly orders are carried forward. This is a combined supply-scenario comparison, not an attribution to delay alone.

| Case | Pipeline | Withdrawal / reserve | Ongoing | Closing | Total | Funded / deaths | Copies | Coverage |
|---|---|---|---:|---:|---:|---:|---:|---:|
| original supply | day-only, 5 evals, batch, 5 spares | maximum  / weekly / $25,100 | $166,430.85 | $0.00 | $166,430.85 | 215 / 205 | 87,114 | 61.84% |
| best frozen / shared | persistent, 20 evals, one/1d, 0 spares | maximum  / weekly / $25,100 | $325,362.25 | $0.00 | $325,362.25 | 256 / 245 | 110,208 | 67.29% |
| best frozen / outside cap | persistent, 20 evals, one/1d, 10 spares | maximum  / weekly / $25,100 | $413,381.50 | $0.00 | $413,381.50 | 344 / 326 | 130,514 | 70.19% |

## Retuned winners

| Case | Pipeline | Withdrawal / reserve | Ongoing | Closing | Total | Funded / deaths | Copies | Coverage |
|---|---|---|---:|---:|---:|---:|---:|---:|
| shared / ongoing | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $444,839.00 | $0.00 | $444,839.00 | 92 / 87 | 121,235 | 66.39% |
| shared / total | persistent, 20 evals, one/1d, 0 spares | minimum  / calendar_month / $25,100 | $300,165.00 | $150,161.65 | $450,326.65 | 114 / 94 | 114,877 | 69.69% |
| outside cap / ongoing | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $448,922.00 | $0.00 | $448,922.00 | 101 / 96 | 122,463 | 66.63% |
| outside cap / total | day-only, 10 evals, one/1d, 10 spares | minimum  / calendar_month / $25,100 | $308,009.00 | $152,699.50 | $460,708.50 | 151 / 131 | 129,606 | 69.91% |

## Same supply and withdrawals, changing only PA blocking

| Case | Pipeline | Withdrawal / reserve | Ongoing | Closing | Total | Funded / deaths | Copies | Coverage |
|---|---|---|---:|---:|---:|---:|---:|---:|
| unrestricted / outside cap | day-only, 10 evals, one/1d, 10 spares | minimum  / calendar_month / $25,100 | $378,909.00 | $163,772.04 | $542,681.04 | 83 / 63 | 166,292 | n/a |
| unrestricted / shared | persistent, 20 evals, one/1d, 0 spares | minimum  / calendar_month / $25,100 | $354,656.00 | $160,184.27 | $514,840.27 | 86 / 66 | 160,612 | n/a |
| unrestricted / outside cap | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $515,725.00 | $0.00 | $515,725.00 | 143 / 138 | 170,971 | n/a |
| unrestricted / shared | day-only, 5 evals, batch, 10 spares | minimum  / weekly / $26,900 | $449,833.00 | $0.00 | $449,833.00 | 133 / 128 | 161,360 | n/a |

Rows are frozen-policy replays, not separately optimized unrestricted winners. Evaluation outcomes use the same one-position engine in both arms; resulting procurement and funding decisions remain endogenous to PA receipts and deaths.

## Replacement service at the selected winners

| Case | Next-check replacement | Resolved wait median / p95 days | Unresolved deaths | Unfilled account-days | Mean live | Zero-live days | Eval / activation fees |
|---|---:|---:|---:|---:|---:|---:|---:|
| shared / ongoing | 28.7% | 21.23 / 123.02 | 15 | 4,831.4 | 13.03 | 220.67 | $7,161 / $11,500 |
| shared / total | 0.0% | 48.09 / 166.05 | 0 | 5,275.0 | 12.24 | 124.67 | $8,085 / $14,250 |
| outside cap / ongoing | 41.7% | 6.15 / 114.05 | 15 | 4,699.9 | 13.16 | 212.67 | $7,953 / $12,625 |
| outside cap / total | 47.3% | 5.26 / 98.12 | 0 | 3,896.2 | 13.86 | 111.67 | $11,616 / $18,875 |

Zero-live days includes startup. Wait percentiles cover completed replacements; unresolved deaths remain censored through the horizon.

## Frozen main-winner budget and starting-date transfers

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

## Search and validation

768 blocked screening rows across four frozen policies and 192 pipelines; 15 nominated pipelines; 4,108 coarse/refined search settings. For each seat mode and concurrency, both cash leaders nominate a pipeline; the original pipeline is always retained. Each selected pipeline gets minimum/maximum/fixed-$1,500 monthly-accrual backlog withdrawals at three check cadences and the configured reserve grid. Local reserve refinement holds pipeline and withdrawal family fixed. An entire paired unrestricted screen supplies the same-policy execution control. This is a staged best-tested search, not an exhaustive optimum over all pipelines and policies. Other acquisition families, contract sizing, launch phases and signal filters are not optimized.

Net cash subtracts every evaluation and activation fee and excludes owner contributions. Ongoing excludes the single permitted terminal payout; total includes it. Terminal cash is not recurring income. All runs reconcile cash, P&L, fees and seat caps; selected winners have full ledgers and entry allocations. Historical controls replay both previous engines. Transfers overlap the selection history and are not unseen validation. Evaluations share one historical tape, not independent pass-rate draws. Exported trade extrema are booked at exits; pending-order reservations and payment-processing delays are not modeled.
