# Assumptions

Values live under `config/` — `products/` is stone, `firm/` is switchable,
`policies/` is ours, `scenarios/` binds them. This file explains why they are
what they are and which way each one bends the answer. Code is stronger
evidence than this file.

## The tape and execution — decided by the user

- **Tape: `RR` at RR = 1.00.** 12,658 trades. This is the exact tape the parent
  study pinned, so brick 1 can be differenced against it. `GG` (21,563 trades at
  RR = 1.00) is available behind `--strategy GG` but is unstudied.
- **Unlimited concurrency.** Every live account takes every trade from all 23
  windows, including trades that overlap in time. There is no one-position slot
  and no contract cap. *Bias: favours the book.* Real Legacy 25K contract limits
  would cut exposure at exactly the moments several windows agree.
- **MAE first.** When a trade touches both extremes, the adverse excursion is
  assumed to land first, so the drawdown is tested against the floor before the
  peak has a chance to lift it. Deterministic and never flatters survival.
  *Bias: conservative.* The parent resolved the same ambiguity with a seeded
  coin; `--path-order mfe_first` is the optimistic pole.
- **$1.05 round-turn commission per MNQ**, charged only in the closing figure.
  MAE and MFE stay gross, matching the parent. *Bias: mildly conservative* —
  a real intratrade low includes the commission already paid.

## The book — chosen here, and defensible

- **One PA per calendar month, activated at the month's first instant.** 79
  months in the tape gives 79 accounts and $15,800 of fees. An account never
  takes a trade whose *entry* precedes its activation, even if that trade exits
  after it.
- **Deaths are not replaced.** The cadence is the only source of accounts, so
  the book shrinks monotonically between purchases. This makes "how many are
  alive at the end" a clean read on survival rather than on a replacement rule.
- **Settlement order is exit time.** Realized P&L lands at the exit, so the book
  is walked in exit order with entry time, window and row as deterministic
  tie-breaks.
- **The killing trade pays no commission.** An account that dies on an
  intratrade excursion never books that trade's close, so no round turn is
  charged for it. The account is already at its threshold, so this changes no
  economics; it is stated because it makes `commission = trades x $1.05` hold
  for survivors only.
- **A positive MAE is clamped to zero.** 555 of the 12,658 trades never traded
  underwater. Their MAE is the worst point reached, still in profit; it must not
  be read as an equity gain that lifts the trailing floor early.

## The one known modelling gap

**Floating P&L across concurrent positions is not aggregated.** Each trade's
excursion is measured against the account's *realized* equity at the moment that
trade settles, not against realized equity plus every other position open at the
same time. With unlimited concurrency this understates the true intratrade
drawdown whenever several losing positions are open together.

*Bias: favours survival.* The alive count in every brick is therefore an
upper bound. Closing this gap needs either an event-driven floating-equity walk or
intrabar paths the completed-trade export does not carry, and it is a candidate
brick of its own.

## The firm rulebook

Every Apex payout rule is implemented and switchable. Where the supplied text
is ambiguous the reading is a named option, not a silent choice.

- **The safety net caps the amount, not just the request.** For the first three
  payouts the balance may not fall below $26,100 — the $26,600 net less one
  $500 minimum. That is the firm's own worked example, scaled from 50K to 25K:
  a $1,200 request needs $26,600 + $700 of balance and leaves $26,100.
- **Rules that "end at the sixth payout" apply to requests 1 through 5.** That
  covers `consistency` and `maximum_payout`. The document says "until the sixth
  payout"; this is the reading that matches "First Five Payouts" in the same
  table. `applies_through_payout` makes it a parameter.
- **The profit split has two contradictory readings in one document.** The
  "Payout Split Percentage" section says 100% of the first $25,000 cumulative
  per account then 90%; the "100% Payout Eligibility" section says 90% until
  five payouts are complete then 100%. The first is the default and matches the
  parent; the second is `mode: after_n_payouts`. On this tape neither bites —
  no account was ever paid $25,000 cumulatively.
- **Consistency counters reset at each approved payout**, per "Once a payout is
  approved, any single day after the approval can not be more than 30%".
- **`denial_on_shortfall` is inert without a processing delay.** With
  same-instant approval there is no window in which a balance can fall. The two
  rules are a pair and only mean anything together.
- **The trailing threshold is not in the rulebook.** It caps every payout at one
  cent above the frozen floor, always, because it is the account specification.
  Switching every firm rule off does not let a payout kill an account outright —
  it lets a payout leave it one cent from death, which on this tape is nearly
  the same thing.

## Our policy, which is not a rule

- **$500 per account per calendar month**, accruing as a backlog when unpayable,
  paid in whole $500 blocks. $500 rather than $100 because the firm will not
  process anything smaller — once the minimum is real, the ask is the minimum.
- **Entitlement accrues from the account's second month**, whether or not the
  account can pay. *Bias: aggressive extraction.* An account that spends three
  years below the gate and then crosses it hands over the backlog at once,
  subject to the caps.
- **A payout never lowers the trailing floor.** The floor follows the peak and
  only rises, so taking cash out spends cushion permanently. That is the entire
  economic mechanism.

## The clock

Source labels are read as Europe/Tallinn wall-clock, the parent's convention.
Because they are *already* in that zone, a trading day is the label's own
calendar date — attaching the zone cannot move it. What the zone buys is
validation, and the tape passes: zero DST-nonexistent and zero ambiguous labels
across all 25,316 timestamps.

The modelled session is 01:00-23:59 local, and following the parent it
*describes* rather than filters: the 2 entries and 11 exits outside it are
authoritative completed fills and are kept, as are the 97 trades whose exit date
differs from their entry date. PA profit is credited on the **exit** date.

Windows Python ships no IANA database, so `clock.py` carries a minimal
Europe/Tallinn and prefers `zoneinfo` whenever a real database is installed.

## Ordering within a month boundary

One canonical order, declared rather than discovered: trades exiting at or
before the boundary settle first, then withdrawals are decided, then that
month's new account opens. The owner is therefore never paid out of money that
had not yet been realized, and a brand-new account cannot pay in its opening
month.

## Not modelled

Slippage and partial fills; contract caps and scaling plans; daily loss limits;
the Evaluation phase and its $35/$125 fees; pending-order and broker fill
lifecycle; prop-firm rule change or failure; any capital constraint on buying
the next account; transfer to a Live Prop account, which the supplied text names
as an alternative end to the consistency rule.

Every *payout* rule is now modelled. What remains unmodelled is execution-side
and lifecycle, not payout mechanics.

## Reading the headline numbers

- **Combined balance** and **profit above start** are *paper* equity inside
  funded accounts. Only what a withdrawal moved is the owner's money.
- **In our pocket** is the only real cash line: withdrawals received minus
  account fees paid. In brick 1 it is negative by construction. In brick 2 it
  is the headline result.
- Accounts overlap in time and share one tape. They are not independent samples,
  so no confidence interval across them is valid.
