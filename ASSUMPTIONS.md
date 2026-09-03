# Assumptions — brick 1

Values live in `config/runtime.json`; this file explains why they are what they
are and which way each one bends the answer. Code is stronger evidence than
this file.

## Decided by the user for this brick

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

## Chosen here, and defensible

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

*Bias: favours survival.* The alive count in brick 1 is therefore an upper
bound. Closing this gap needs either an event-driven floating-equity walk or
intrabar paths the completed-trade export does not carry, and it is a candidate
brick of its own.

## Not modelled at all in brick 1

Payout eligibility, caps, splits and consistency; slippage and partial fills;
contract caps and scaling plans; daily loss limits; the Evaluation phase and its
$35/$125 fees; pending-order and broker fill lifecycle; prop-firm rule change or
failure; any capital constraint on buying the next account.

## Reading the headline numbers

- **Combined balance** and **profit above start** are *paper* equity inside
  funded accounts. No payout rule exists yet, so none of it has been withdrawn
  and none of it is the owner's cash.
- **Owner cash position** is the only real cash line in brick 1, and it is
  negative by construction: fees out, nothing in. It turns into a real answer
  only when a payout brick lands.
- Accounts overlap in time and share one tape. They are not independent samples,
  so no confidence interval across them is valid.
