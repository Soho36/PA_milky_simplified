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

The main scheduled-purchase comparison now includes **quarterly-one,
monthly-one and weekly-one**. Monthly-two is a separate expansion policy;
replacement/reinvestment are separate operating-policy families. Quarterly-three
is retained as historical batch evidence and excluded from headline rankings.

Best tested terminal-inclusive bundle among the three main schedules:

| Initial cash | Monthly funding | Purchases | Withdrawals / reserve | Ongoing net cash | Total net cash |
|---|---:|---|---|---:|---:|
| $1,000 | $0 | monthly_one | daily_minimum_retain_31900 | $224,400 | $302,287 |
| $1,000 | $200 | weekly_one | daily_minimum_retain_31900 | $449,800 | $550,682 |
| $5,000 | $0 | weekly_one | daily_minimum_retain_31900 | $443,000 | $544,527 |
| $5,000 | $200 | weekly_one | daily_minimum_retain_31900 | $490,700 | $589,340 |

Source: [current grouped purchase report](../../results/study__full_rulebook__RR__account_purchases__cash_budgets/REPORT.generated.md).
This restricted ranking is not the best of every operating family. The tightest
budget still has a higher historical result under restarting reinvestment.

The earlier quarterly-three headline depended on its January purchase phase.
[User-supplied phase checks](../../results/study__full_rulebook__RR__account_purchases__cash_budgets/PHASE_SENSITIVITY.md)
showed large reversals and much smaller weekday variation for weekly-one in
the funded examples. Those additional simulations have not been independently
reproduced here. Weekly-one is a less phase-sensitive candidate on that evidence,
not a proven universally robust policy.

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
  the other budgets. Monthly-two remains an expansion comparison; weekly-one
  leads the three main schedules in the funded examples.
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
