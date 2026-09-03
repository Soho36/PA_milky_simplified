# Assumptions

Values live in `config/runtime.json`; this file explains why they are what they
are and which way each one bends the answer. Code is stronger evidence than
this file.

## Brick 1 — decided by the user

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

## Brick 1 — chosen here, and defensible

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
- **Naive local timestamps.** The source labels are used as exported, with no
  timezone attached. Brick 1 has no daily-boundary rule, so nothing depends on
  it. A brick that adds daily loss limits or payout days must fix the clock
  first — the parent used Europe/Tallinn with historical DST.

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

## Brick 2 — taking cash out

Decided by the user: **$100 per account per month**, with a backlog, and the
first prop-firm rule of the study as the gate.

- **The gate is $26,600**, stated by the user as starting balance plus the
  $1,500 safety net plus the $100 being requested. It is tested on the balance
  at the decision, exactly as the parent study's section 8 gate was.
- **The safety net caps the amount, not just the request.** A withdrawal may
  not cut the balance below $26,500. This is an *interpretation*: the user
  named the gate, not the cap, and the alternative reading — once the gate
  opens, take the whole backlog regardless — would let an account pay a large
  backlog out of protected money. The coherent reading was chosen and the
  alternative is one config field away (`safety_net_balance_usd: null`). It
  binds rarely: only when a backlog is larger than the cushion above $26,500.
- **Entitlement accrues from the account's second month**, whether or not the
  account can pay. An account owes the owner $100 a month from the day after it
  opens; unpayable months stay owed and are paid later in whole $100 blocks.
  *Bias: aggressive extraction.* An account that spends three years below the
  gate and then crosses it hands over three years of backlog at once, subject
  to the net.
- **Whole months only.** An account that could pay $250 of a $500 backlog pays
  $200, so the pocket stays a clean multiple of $100.
- **A withdrawal never lowers the trailing floor.** The floor follows the peak
  and only ever rises. Taking cash out therefore spends cushion permanently,
  which is the entire economic mechanism of this brick.
- **Under these numbers a withdrawal cannot itself kill an account.** The gate
  implies a peak of at least +$1,600, so the floor is already frozen at
  $25,100, and the net stops the balance $1,400 clear of it. Withdrawals kill
  *indirectly*, by leaving less room for the next drawdown — which is what
  happened to the 2020-04 and 2024-12 accounts.
- **Cash is atomic and instant.** Request, approval, balance removal and
  receipt are one event at the month boundary. No delay, no denial, no split.

## Ordering within a month boundary

One canonical order, declared rather than discovered: trades exiting at or
before the boundary settle first, then withdrawals are decided, then that
month's new account opens. The owner is therefore never paid out of money that
had not yet been realized, and a brand-new account cannot pay in its opening
month.

## Not modelled

Payout request counts, the $1,500-per-request cap, the 90/10 split above
$25,000 cumulative, consistency rules, denials and processing delays; slippage
and partial fills;
contract caps and scaling plans; daily loss limits; the Evaluation phase and its
$35/$125 fees; pending-order and broker fill lifecycle; prop-firm rule change or
failure; any capital constraint on buying the next account.

## Reading the headline numbers

- **Combined balance** and **profit above start** are *paper* equity inside
  funded accounts. Only what a withdrawal moved is the owner's money.
- **In our pocket** is the only real cash line: withdrawals received minus
  account fees paid. In brick 1 it is negative by construction. In brick 2 it
  is the headline result.
- Accounts overlap in time and share one tape. They are not independent samples,
  so no confidence interval across them is valid.
