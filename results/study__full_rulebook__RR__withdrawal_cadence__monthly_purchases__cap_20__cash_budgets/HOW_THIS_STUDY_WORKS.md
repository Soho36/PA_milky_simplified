# How this study operates: capped cadence with cash budgets

**In everyday terms:** Start with the selected owner cash budget and no accounts.
At the start of each month, attempt to buy **one** new account if there is money
for its fee and fewer than 20 accounts are live. Trade all live accounts. From
each account's second calendar month, check for withdrawals at the tested
frequency. Take the policy's payout when eligible while retaining the selected
reserve; otherwise wait. Continue this process through the dataset, then score
one permitted closing request.

Reaching 20 live accounts **pauses** buying. If one dies, the next monthly date
can buy one. If several die, it still buys only one. There are no immediate
replacements, catch-up purchases, or permanent stop after first reaching 20.
A scheduled purchase that lacks cash or capacity is skipped.

The four budgets start with $1,000 or $5,000 and add either nothing or $200 per
month, beginning in the second calendar month. Received payouts can fund later
purchases; account paper balances cannot. Contributions are excluded from net
cash. Unused contributed cash remains part of ending owner cash.

The question is which withdrawal cadence and reserve work with this monthly
purchase rule under each budget. Actual purchases can differ because payout
timing affects available cash and deaths free capacity. Therefore this is not
necessarily the same portfolio with money merely arriving earlier.

The [current report](REPORT.generated.md) also includes purchase-strategy
comparisons imported from the purchase study. Those tables change acquisition
policy; the cadence experiment itself always uses monthly-one. Its 12 shared
monthly-one settings exactly match the purchase study.

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
