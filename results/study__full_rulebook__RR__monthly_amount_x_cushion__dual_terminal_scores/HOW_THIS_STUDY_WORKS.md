# How this study operates: withdrawal amount and reserve

**In everyday terms:** Buy one new account at the start of every calendar month
and trade all live accounts through the remaining dataset. For each tested
withdrawal policy, start checking monthly from each account's second calendar
month. Ask for the amount allowed by our policy and the firm's rules, leaving
the selected reserve. Continue trading when losses push an account below that
reserve, but withhold payouts that cannot leave enough behind. At the endpoint,
score both the cash already received and the cash including one permitted
closing request.

This is an **uncapped, purchase-unconstrained experiment**. It keeps buying one
account monthly even if 20 are already live, and does not require an owner cash
budget to finance purchases. All candidates purchased 79 accounts. A death does
not trigger an extra replacement; next month's scheduled purchase still happens.

The question is how withdrawal amounts and reserves interact under that same
monthly purchase schedule. Some policies accumulate unpaid monthly entitlement;
others ask only for the minimum or available excess. An accumulated target is
not a hard monthly payout ceiling. A minimum request does not build a backlog.
The hold benchmark makes no ongoing withdrawal.

The report selects useful representatives from a tested grid. Its reserve
levels are candidate choices, not a rule that every account must reach a single
universal balance. Read this alongside the [report](REPORT.md); do not compare
its total dollars directly with the capped, cash-funded studies.

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
