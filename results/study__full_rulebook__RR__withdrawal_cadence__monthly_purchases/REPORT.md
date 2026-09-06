# Withdrawal cadence with monthly account purchases

93 settings: five policies, six cushions in the $31,600-$32,100 band, three request cadences, plus the minimum-policy $30,000 control.

## Ongoing cash: best tested cushion per policy and cadence
“Which reserve produced the most cash during trading?”

| Policy | Checks | Retain | Ongoing cash | Final receipt | Total cash | Alive | Same trading path |
|---|---|---:|---:|---:|---:|---:|:---:|
| fixed_750_backlog | calendar_month | $31,600 | $354,140.38 | $102,345.63 | $456,486.01 | 22 | True |
| fixed_750_backlog | weekly | $31,600 | $369,330.03 | $87,940.55 | $457,270.58 | 22 | True |
| fixed_750_backlog | daily | $31,900 | $354,075.72 | $89,267.71 | $443,343.43 | 19 | False |
| fixed_1000_backlog | calendar_month | $31,600 | $354,140.38 | $102,345.63 | $456,486.01 | 22 | True |
| fixed_1000_backlog | weekly | $31,600 | $369,330.03 | $87,940.55 | $457,270.58 | 22 | True |
| fixed_1000_backlog | daily | $31,900 | $354,534.02 | $100,254.99 | $454,789.01 | 21 | False |
| fixed_1500_backlog | calendar_month | $31,600 | $354,140.38 | $102,345.63 | $456,486.01 | 22 | True |
| fixed_1500_backlog | weekly | $31,600 | $369,330.03 | $87,940.55 | $457,270.58 | 22 | True |
| fixed_1500_backlog | daily | $31,900 | $354,534.02 | $100,254.99 | $454,789.01 | 21 | False |
| minimum_500_per_check | calendar_month | $30,000 | $266,200.00 | $194,311.75 | $460,511.75 | 22 | True |
| minimum_500_per_check | weekly | $30,000 | $355,450.00 | $4,532.84 | $359,982.84 | 3 | False |
| minimum_500_per_check | daily | $30,000 | $373,200.00 | $0.00 | $373,200.00 | 2 | False |
| maximum_excess_per_check | calendar_month | $31,600 | $354,140.38 | $102,345.63 | $456,486.01 | 22 | True |
| maximum_excess_per_check | weekly | $31,600 | $369,330.03 | $87,940.55 | $457,270.58 | 22 | True |
| maximum_excess_per_check | daily | $31,900 | $354,534.02 | $100,254.99 | $454,789.01 | 21 | False |
*“Same trading path” compares each candidate with the hold-everything benchmark.

## Cash including final request: best tested cushion per policy and cadence
“Which reserve produced the most cash during trading plus the final withdrawal?”

| Policy | Checks | Retain | Ongoing cash | Final receipt | Total cash | Alive | Same trading path |
|---|---|---:|---:|---:|---:|---:|:---:|
| fixed_750_backlog | calendar_month | $31,600 | $354,140.38 | $102,345.63 | $456,486.01 | 22 | True |
| fixed_750_backlog | weekly | $31,600 | $369,330.03 | $87,940.55 | $457,270.58 | 22 | True |
| fixed_750_backlog | daily | $32,000 | $352,594.02 | $102,094.99 | $454,689.01 | 21 | False |
| fixed_1000_backlog | calendar_month | $31,600 | $354,140.38 | $102,345.63 | $456,486.01 | 22 | True |
| fixed_1000_backlog | weekly | $31,600 | $369,330.03 | $87,940.55 | $457,270.58 | 22 | True |
| fixed_1000_backlog | daily | $31,900 | $354,534.02 | $100,254.99 | $454,789.01 | 21 | False |
| fixed_1500_backlog | calendar_month | $31,600 | $354,140.38 | $102,345.63 | $456,486.01 | 22 | True |
| fixed_1500_backlog | weekly | $31,600 | $369,330.03 | $87,940.55 | $457,270.58 | 22 | True |
| fixed_1500_backlog | daily | $31,900 | $354,534.02 | $100,254.99 | $454,789.01 | 21 | False |
| minimum_500_per_check | calendar_month | $30,000 | $266,200.00 | $194,311.75 | $460,511.75 | 22 | True |
| minimum_500_per_check | weekly | $31,600 | $349,600.00 | $110,911.75 | $460,511.75 | 22 | True |
| minimum_500_per_check | daily | $31,900 | $357,800.00 | $102,711.75 | $460,511.75 | 22 | True |
| maximum_excess_per_check | calendar_month | $31,600 | $354,140.38 | $102,345.63 | $456,486.01 | 22 | True |
| maximum_excess_per_check | weekly | $31,600 | $369,330.03 | $87,940.55 | $457,270.58 | 22 | True |
| maximum_excess_per_check | daily | $31,900 | $354,534.02 | $100,254.99 | $454,789.01 | 21 | False |
*“Same trading path” compares each candidate with the hold-everything benchmark.
## Controlled comparison: maximum excess at $31,600

| Policy | Checks | Retain | Ongoing cash | Final receipt | Total cash | Alive | Same trading path |
|---|---|---:|---:|---:|---:|---:|:---:|
| maximum_excess_per_check | calendar_month | $31,600 | $354,140.38 | $102,345.63 | $456,486.01 | 22 | True |
| maximum_excess_per_check | weekly | $31,600 | $369,330.03 | $87,940.55 | $457,270.58 | 22 | True |
| maximum_excess_per_check | daily | $31,600 | $350,261.63 | $0.00 | $350,261.63 | 2 | False |

## Interpretation

At $31,600, weekly maximum-excess checks bring $15,189.65 more cash forward than monthly checks and add $784.57 to terminal-inclusive cash, with the same trading path. Daily maximum-excess checks at this cushion instead lose accounts and substantially reduce total cash.

Daily minimum-$500 checks at $31,900 receive $357,800 during trading and $460,511.75 including the terminal request. That is $91,600 more ongoing cash than monthly minimum checks at $30,000, with equal total cash. This comparison adapts BOTH cadence and cushion. Weekly minimum checks at $31,600 receive $349,600 with the same total.

The highest ongoing-only cash is $373,200 from daily minimum checks at $30,000, but only two accounts survive and nothing more is received at exit. It is not the strongest candidate for preserving earning capacity. These numbers are historical, not forecasts.

## Conventions and limits

Daily means one midnight check after completed exits; weekly means Monday midnight; monthly means the first midnight of the month. Checks start in the second calendar month for every cadence. Fixed-target entitlement accrues once per calendar month, never per check. Minimum means $500 per eligible check, not a $500 monthly budget; changing its cadence therefore changes desired extraction frequency. Maximum requests spare cash above the cushion. Firm gates still apply, including days since payout. A failed eligibility check is recorded as a denial by the existing ledger; this is not proof of an externally submitted application. Trades at an exact decision timestamp settle first. No post-midnight future trades are used. All policies permit one final request releasing the voluntary cushion, with zero processing delay.

The study holds the tape, account purchases, contract size and rulebook fixed. Candidate deltas in CSV/JSON are against the same policy and cushion with monthly checks. Trading-neutral means the per-account path fingerprint matches hold on this shared tape and activation schedule. The hold reference is not a guaranteed earnings maximum. These are in-sample comparisons over the chosen band; cadence-specific global cushion optima remain unsearched.

[best_ongoing detailed report](best_ongoing/report.txt) and its embedded config.json reproduce the leading run.

[best_terminal detailed report](best_terminal/report.txt) and its embedded config.json reproduce the leading run.

Reproduce: `venv/Scripts/python.exe scripts/study_withdrawal_cadence.py`.
