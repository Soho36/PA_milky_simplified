# Legacy 25K: current findings

We have a coherent in-sample picture of the tested operating policies. The best
choice depends on funding, purchase timing and whether the objective is cash
received during trading or cash including the terminal request. We have not
established a universally optimal policy.

This wrap-up covers the current 132-candidate purchase study and 372-candidate
budget-matched cadence study. Earlier uncapped studies explain mechanisms;
their dollars must not be ranked directly against funded, capped portfolios.
See the [study guide](STUDIES.md) for the underlying reports.

## The operating comparison

The funded studies use the RR tape from January 2020 through July 2026, $200
per purchased seat, at most 20 live accounts, and four owner-funding scenarios.
Monthly contributions start in the second calendar month. Full configured
payout rules apply with processing delay off. Net cash subtracts seat costs
and the applicable split and excludes owner contributions. Paper balances
cannot fund purchases. Terminal cash means one firm-permitted closing request,
not unrestricted liquidation. These are full-dataset totals, not annual income.

Best tested purchase/withdrawal bundle by terminal-inclusive net cash:

| Initial cash | Monthly funding | Purchases | Withdrawals / retained balance | Ongoing net cash | Total net cash |
|---|---:|---|---|---:|---:|
| $1,000 | $0 | Restart and reinvest 100% | Monthly minimum / $30,000 | $240,500 | $430,472 |
| $1,000 | $200 | Three quarterly | Daily minimum / $31,900 | $493,100 | $592,747 |
| $5,000 | $0 | Three quarterly | Daily minimum / $31,900 | $460,900 | $561,061 |
| $5,000 | $200 | Three quarterly | Daily minimum / $31,900 | $493,100 | $592,747 |

Source: [132 purchase candidates](../../results/study__full_rulebook__RR__account_purchases__cash_budgets/REPORT.generated.md).
These winners are selected among three withdrawal settings per purchase policy.
They are not the result of optimizing every possible policy combination.

## What the studies support

- **Payout history matters.** In the earlier uncapped hold experiment, one
  closing request extracts far less than an idealized liquidation. That explains
  a mechanism; it does not mean holding is always inferior under every horizon.
- **Reserves matter alongside withdrawal cadence.** A $31,900 retained balance
  is a request-policy threshold, not a guaranteed minimum account balance.
  Losses can take an account below it. Faster checks are not guaranteed payouts.
- **The objective changes the preferred policy.** With monthly purchases in the
  capped cadence study, daily minimum requests at $30,000 maximize ongoing cash
  but leave only two survivors in each budget. A terminal-inclusive leader can
  preserve more accounts while receiving less during trading.
- **Faster scheduled buying is funding-sensitive.** Monthly-two and weekly-one
  both lose $1,000 on five accounts with no top-ups. They beat monthly-one in
  the other budgets but do not change the overall total-cash winners above.
- **Restarting is economically distinct from reinvesting.** Strict one-seed
  reinvestment stops after a $200 initial loss before receiving any payout.
  Restart variants can use available owner cash to buy a new seed when empty.
- **Rule-effect numbers need their policy context.** Fixed-policy removal and
  cushion-adapted removal answer different questions. Individual removal deltas
  are not additive costs of the full rulebook. The historical $2,200 adapted
  result must not be presented as a universal price of all firm restrictions.
- **Economic bridges are accounting, not unique causal attribution.** Retained
  profit is not guaranteed future cash. Dead-account booked deficits describe
  the ledger; they do not prove that a firm financed our withdrawals.

## Which comparisons are trustworthy together?

The uncapped amount/cushion and cadence studies agree at 27 common settings.
The funded cadence and purchase studies agree at all 12 common monthly-purchase
settings. All 108 original purchase candidates reproduced exactly when the two
faster schedules were added. The [consistency audit](../../results/CONSISTENCY_AUDIT.md)
checks arithmetic and saved controls; it is not an out-of-sample validation.

A fixed-withdrawal purchase table holds withdrawal settings constant. A table
selecting the best withdrawal setting per purchase policy compares whole bundles.
Both are useful, but they answer different questions. A cap or funding limit can
change cohorts when withdrawal behaviour changes; no fixed-cohort hold-ceiling
claim is made for those comparisons.

## What remains before stronger conclusions

1. Test other starting dates and quarterly/weekly calendar phases. The same
   underlying tape drives all account cohorts, so accounts are not independent trials.
2. Test whether the preferred schedules survive less favourable periods and
   whether sufficient owner cash remains available before the first payouts.
3. Reconsider the withdrawal shortlist under other purchase policies. The wider
   capped cadence grid was run with monthly-one purchases, not every strategy.
4. Keep terminal-inclusive and ongoing objectives separate. An endpoint chosen
   by the dataset is not evidence that waiting for that date is an executable forecast.

The next product should have its own verified configuration, policy grid and
results. The 25K thresholds and rankings are not transferable findings for 50K.
