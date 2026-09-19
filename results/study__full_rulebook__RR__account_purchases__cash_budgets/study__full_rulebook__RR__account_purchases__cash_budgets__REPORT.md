# Account purchases under explicit cash budgets

108 candidates: nine purchase policies x three fixed withdrawal policies x four funding scenarios. Full configured payout rules; processing delay off; RR tape.

## $1,000 starting cash; $0/month thereafter

Every candidate receives $1,000 total contributions. Best tested withdrawal policy per purchase policy, ranked by terminal-inclusive net cash:

| Purchase policy | Withdrawal policy | Accounts | Alive | Purchase spend | Ongoing net cash | Total net cash | Ending owner cash |
|---|---|---:|---:|---:|---:|---:|---:|
| reinvest_restart_100pct | monthly_minimum_retain_30000 | 85 | 20 | $17,000 | $240,500.00 | $430,471.51 | $431,471.51 |
| reinvest_restart_50pct | monthly_minimum_retain_30000 | 70 | 20 | $14,000 | $213,500.00 | $376,626.56 | $377,626.56 |
| quarterly_three | daily_minimum_retain_31900 | 59 | 17 | $11,800 | $246,700.00 | $317,664.27 | $318,664.27 |
| monthly_one | daily_minimum_retain_31900 | 58 | 17 | $11,600 | $224,400.00 | $302,287.21 | $303,287.21 |
| quarterly_one | daily_minimum_retain_31900 | 23 | 6 | $4,600 | $91,400.00 | $116,610.36 | $117,610.36 |
| replace_one | daily_minimum_retain_31900 | 4 | 1 | $800 | $29,600.00 | $34,499.95 | $35,499.95 |
| reinvest_50pct | daily_minimum_retain_31900 | 1 | 0 | $200 | $-200.00 | $-200.00 | $800.00 |
| reinvest_100pct | daily_minimum_retain_31900 | 1 | 0 | $200 | $-200.00 | $-200.00 | $800.00 |
| replace_five | daily_minimum_retain_31900 | 5 | 0 | $1,000 | $-1,000.00 | $-1,000.00 | $0.00 |

NB!!! Replacement and reinvestment policies use daily purchase checks.

monthly_one - Try to buy one account every month.

quarterly_one - Try to buy one account every three months.

quarterly_three - Try to buy three accounts together every three months.

replace_one - Keep one account running; replace it when it dies.

replace_five - Try to keep five accounts running.

reinvest_50pct / 100pct - Start with one account. Use half or all received payouts as the budget for additional accounts.

reinvest_restart_50pct / 100pct - Same, but if all accounts die, use available cash to buy a fresh account and try again.

**Ongoing objective leader:** reinvest_restart_100pct / daily_minimum_retain_31900: $269,100.00. [Ongoing-cash leader ledger](budget_1000_monthly_0__best_ongoing/report.txt). **Terminal objective leader:** reinvest_restart_100pct / monthly_minimum_retain_30000: $430,471.51. [Terminal-cash leader ledger](budget_1000_monthly_0__best_terminal/report.txt). 

## $1,000 starting cash; $200/month thereafter

Every candidate receives $16,600 total contributions. Best tested withdrawal policy per purchase policy, ranked by terminal-inclusive net cash:

| Purchase policy | Withdrawal policy | Accounts | Alive | Purchase spend | Ongoing net cash | Total net cash | Ending owner cash |
|---|---|---:|---:|---:|---:|---:|---:|
| quarterly_three | daily_minimum_retain_31900 | 45 | 20 | $9,000 | $493,100.00 | $592,747.41 | $609,347.41 |
| monthly_one | daily_minimum_retain_31900 | 60 | 20 | $12,000 | $361,600.00 | $464,311.75 | $480,911.75 |
| reinvest_restart_100pct | monthly_minimum_retain_30000 | 85 | 20 | $17,000 | $240,500.00 | $430,471.51 | $447,071.51 |
| reinvest_restart_50pct | monthly_minimum_retain_30000 | 70 | 20 | $14,000 | $213,500.00 | $376,626.56 | $393,226.56 |
| quarterly_one | daily_minimum_retain_31900 | 27 | 9 | $5,400 | $172,800.00 | $212,946.34 | $229,546.34 |
| replace_five | daily_minimum_retain_31900 | 26 | 5 | $5,200 | $135,550.00 | $160,123.08 | $176,723.08 |
| replace_one | daily_minimum_retain_31900 | 4 | 1 | $800 | $29,600.00 | $34,499.95 | $51,099.95 |
| reinvest_50pct | daily_minimum_retain_31900 | 1 | 0 | $200 | $-200.00 | $-200.00 | $16,400.00 |
| reinvest_100pct | daily_minimum_retain_31900 | 1 | 0 | $200 | $-200.00 | $-200.00 | $16,400.00 |

**Ongoing objective leader:** quarterly_three / weekly_excess_retain_31600: $505,248.40. [Ongoing-cash leader ledger](budget_1000_monthly_200__best_ongoing/report.txt). **Terminal objective leader:** quarterly_three / daily_minimum_retain_31900: $592,747.41. [Terminal-cash leader ledger](budget_1000_monthly_200__best_terminal/report.txt). 

## $5,000 starting cash; $0/month thereafter

Every candidate receives $5,000 total contributions. Best tested withdrawal policy per purchase policy, ranked by terminal-inclusive net cash:

| Purchase policy | Withdrawal policy | Accounts | Alive | Purchase spend | Ongoing net cash | Total net cash | Ending owner cash |
|---|---|---:|---:|---:|---:|---:|---:|
| quarterly_three | daily_minimum_retain_31900 | 50 | 20 | $10,000 | $460,900.00 | $561,060.90 | $566,060.90 |
| monthly_one | daily_minimum_retain_31900 | 59 | 20 | $11,800 | $361,800.00 | $464,511.75 | $469,511.75 |
| reinvest_restart_100pct | monthly_minimum_retain_30000 | 85 | 20 | $17,000 | $240,500.00 | $430,471.51 | $435,471.51 |
| reinvest_restart_50pct | monthly_minimum_retain_30000 | 70 | 20 | $14,000 | $213,500.00 | $376,626.56 | $381,626.56 |
| quarterly_one | daily_minimum_retain_31900 | 27 | 9 | $5,400 | $172,800.00 | $212,946.34 | $217,946.34 |
| replace_five | daily_minimum_retain_31900 | 20 | 5 | $4,000 | $148,000.00 | $172,499.75 | $177,499.75 |
| replace_one | daily_minimum_retain_31900 | 4 | 1 | $800 | $29,600.00 | $34,499.95 | $39,499.95 |
| reinvest_50pct | daily_minimum_retain_31900 | 1 | 0 | $200 | $-200.00 | $-200.00 | $4,800.00 |
| reinvest_100pct | daily_minimum_retain_31900 | 1 | 0 | $200 | $-200.00 | $-200.00 | $4,800.00 |

**Ongoing objective leader:** quarterly_three / weekly_excess_retain_31600: $472,613.69. [Ongoing-cash leader ledger](budget_5000_monthly_0__best_ongoing/report.txt). **Terminal objective leader:** quarterly_three / daily_minimum_retain_31900: $561,060.90. [Terminal-cash leader ledger](budget_5000_monthly_0__best_terminal/report.txt). 

## $5,000 starting cash; $200/month thereafter

Every candidate receives $20,600 total contributions. Best tested withdrawal policy per purchase policy, ranked by terminal-inclusive net cash:

| Purchase policy | Withdrawal policy | Accounts | Alive | Purchase spend | Ongoing net cash | Total net cash | Ending owner cash |
|---|---|---:|---:|---:|---:|---:|---:|
| quarterly_three | daily_minimum_retain_31900 | 45 | 20 | $9,000 | $493,100.00 | $592,747.41 | $613,347.41 |
| monthly_one | daily_minimum_retain_31900 | 60 | 20 | $12,000 | $361,600.00 | $464,311.75 | $484,911.75 |
| reinvest_restart_100pct | monthly_minimum_retain_30000 | 85 | 20 | $17,000 | $240,500.00 | $430,471.51 | $451,071.51 |
| reinvest_restart_50pct | monthly_minimum_retain_30000 | 70 | 20 | $14,000 | $213,500.00 | $376,626.56 | $397,226.56 |
| quarterly_one | daily_minimum_retain_31900 | 27 | 9 | $5,400 | $172,800.00 | $212,946.34 | $233,546.34 |
| replace_five | daily_minimum_retain_31900 | 20 | 5 | $4,000 | $148,000.00 | $172,499.75 | $193,099.75 |
| replace_one | daily_minimum_retain_31900 | 4 | 1 | $800 | $29,600.00 | $34,499.95 | $55,099.95 |
| reinvest_50pct | daily_minimum_retain_31900 | 1 | 0 | $200 | $-200.00 | $-200.00 | $20,400.00 |
| reinvest_100pct | daily_minimum_retain_31900 | 1 | 0 | $200 | $-200.00 | $-200.00 | $20,400.00 |

**Ongoing objective leader:** quarterly_three / weekly_excess_retain_31600: $505,248.40. [Ongoing-cash leader ledger](budget_5000_monthly_200__best_ongoing/report.txt). **Terminal objective leader:** quarterly_three / daily_minimum_retain_31900: $592,747.41. [Terminal-cash leader ledger](budget_5000_monthly_200__best_terminal/report.txt). 

## Reading the comparison

The ranking changes with the budget: restarting reinvestment leads terminal-inclusive cash with $1,000 and no contributions; quarterly batches of three lead the other scenarios. The ongoing-cash objective can select a different withdrawal policy. Strict reinvestment loses its initial seat before receiving a payout and never restarts, so its -$200 result diagnoses startup dependence rather than the merits of the reinvestment fraction.

Three quarterly purchases and one monthly purchase have the same planned purchase count per quarter, but enter different cohorts. Their difference combines entry timing, funding constraints, survival and capacity occupancy. It does not establish that quarterly buying is generally superior. Test alternative calendar phases, starting dates and live-account caps before treating these rankings as robust.

Net cash is received payouts minus account fees, never owner contributions. Ending owner cash equals cumulative owner contributions plus net cash, and includes unused principal. Ongoing net cash excludes the final receipt. Live account paper balances are never purchase funds. Cash cannot go negative. Contributions are scheduled equally, even when unused; no $200 contribution is added in the opening month.

Monthly buys one at each month boundary; quarterly buys one or three every third month. Missed scheduled buys expire. Replacement retries at midnight to maintain one or five live accounts, including the opening purchase. Strict reinvestment starts with one account and never restarts; the restart variants buy one replacement from available owner cash when the portfolio is empty. Both then spend 50% or 100% of cumulative received payouts on additional accounts; unused payout allocation carries forward. Other purchase policies may use both contributed cash and received payouts. All share a modelled capacity of 20 live accounts; it is not a verified firm limit. Capacity and funding blocks are in candidates.csv.

Trades settle before requests and purchases. Purchases use only already-received payouts, with activation at the check time, so earlier entries are excluded. All account types are the same $200 seat. No evaluation cost, personal trading margin, or economic firm-failure model is added. All withdrawal policies begin requests in the second calendar month of each account. Midnight reinvestment can buy near the endpoint; the experiment does not add a hindsight stop-buying rule. Terminal proceeds are never reinvested.

Changing acquisition changes cohorts and the offered book of trades, so the old fixed-acquisition hold fingerprint and reference capture are not comparable here. The withdrawal choices are held at previously tested settings; this is not a joint global optimization. Results are in-sample and conditional on the starting date, cash budget and capacity cap. Reproduce with `venv/Scripts/python.exe scripts/study_account_purchases.py`. Each leading run has an experiment.json containing both run configuration and acquisition policy; replay through run_book(..., acquisition=AcquisitionPolicy(...)).
