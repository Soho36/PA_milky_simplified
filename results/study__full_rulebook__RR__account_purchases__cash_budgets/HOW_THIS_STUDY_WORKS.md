# How this study operates: account purchases with cash budgets

**In everyday terms:** Start with the selected owner cash budget and follow one
purchase policy throughout the dataset. Buy only when the policy calls for a
purchase, there is enough available owner cash, and there is space below 20 live
accounts. Trade every live account. Starting in its second calendar month, check
for withdrawals according to the selected withdrawal policy, leaving its reserve.
Use received payouts for future purchases as that purchase policy permits.
At the endpoint, score one permitted closing request; do not reinvest that receipt.

For the familiar **monthly-one** example: attempt one purchase on each monthly
date. Buy none at 20 live accounts. Below 20, buy one if affordable—even if
several accounts died. Buying resumes when space becomes available; it does
not stop permanently after first reaching 20.

Other tested purchase policies change that instruction: scheduled batches,
weekly buying, maintaining a target number of live accounts, or expanding from
received payouts. Scheduled attempts expire if blocked. Replacement and
reinvestment policies check at midnight; they are not instantaneous responses
to an intraday death. Strict reinvestment does not restart after its only seed
fails; restart variants can buy one new seed from available cash when empty.
Not all purchase policies are trying to fill all 20 seats.

Every comparison uses $1,000 or $5,000 initially, with either $0 or $200 monthly
from the second calendar month. Contributions are excluded from net cash and
unused principal remains in ending owner cash. All accounts cost $200 in this
study. A 20-live-account cap can coexist with far more than 20 total purchases.

The question is which buying approach works with each budget. The
[current report](REPORT.generated.md) compares both whole bundles (best of the
three tested withdrawal settings for each purchase policy) and purchases under
a fixed withdrawal setting. These answer different questions. No policy's
withdrawal settings were optimized over every possible cadence and reserve.

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

## Current comparison scope

The main scheduled-purchase family is quarterly-one, monthly-one and weekly-one.
Monthly-two is an expansion comparison; replacement and reinvestment are separate
operating families. Quarterly-three remains historical batch-purchase evidence
and is excluded from main rankings. No historical cash results have been deleted.
