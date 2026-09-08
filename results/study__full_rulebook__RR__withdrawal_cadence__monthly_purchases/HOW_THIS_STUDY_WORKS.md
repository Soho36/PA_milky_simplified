# How this study operates: withdrawal-check cadence

**In everyday terms:** Keep buying one new account every calendar month and
trade every live account. From each account's second calendar month, check for
withdrawals on the tested schedule: monthly, weekly or daily. When the account
has enough spare balance and meets the firm's rules, take the amount specified
by the policy while leaving its reserve. Otherwise wait for another scheduled
check. At the dataset endpoint, make the permitted closing request for scoring.

Purchases remain monthly regardless of how often withdrawals are checked.
This historical study has **no 20-live-account cap and no owner-cash funding
constraint**. Every candidate purchased 79 accounts. Deaths do not cause extra
purchases between monthly dates, and more than 20 accounts may survive.

The question is whether changing withdrawal opportunities changes cash timing,
survival and total extraction. Fixed-target entitlement still accrues monthly,
not once per check. Minimum-policy checks can ask for $500 each time eligibility
permits, so changing their cadence changes the opportunities to extract money.
Weekly means Monday midnight; monthly means the first day of the month.

Comparisons at the same reserve isolate the change in check schedule within
that policy. Tables selecting a best reserve also change the reserve, so they
compare policy combinations. The [report and reader notes](REPORT.md) describe
this uncapped experiment; its 22-survivor examples are not the capped model.

## What the reserve and money figures mean

The retained balance is money we choose to leave **after a withdrawal**. It is
not a guaranteed minimum balance and it is not a trading stop. Trading losses
can take the account below it; trading continues while withdrawals wait for
sufficient spare balance to return. Reaching the reserve once does not permanently
qualify the account for payouts. For example, leaving $31,900 after a $500
withdrawal requires at least $32,400 before that withdrawal, plus firm eligibility.

Checks begin in each account's second calendar month. A check is an opportunity
to assess eligibility, not a guaranteed payout or evidence of an external
application. The configured firm's gates still apply. Daily checks occur at
midnight after the simulation has settled completed trades; they are not
continuous intraday monitoring.

Ongoing net cash is money received during trading minus account purchase fees.
Total net cash also includes **one permitted terminal request** per eligible
surviving account. That closing request releases our voluntary reserve but still
obeys the configured payout rules; it does not automatically empty the accounts.
Remaining paper profit is separate from cash received. Accounts means all
purchased accounts; Alive means survivors before the terminal request.

These are historical full-dataset totals for Legacy 25K on the RR tape, with
configured payout rules and processing delay off. They are not annual income,
forecasts, or promises that every account reaches its reserve. The terminal
request is a scoring convention, not a recurring operating instruction.
