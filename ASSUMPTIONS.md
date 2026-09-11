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
- **MAE first — and the label was backwards here until 2026-09-04.** With a
  *trailing* threshold the intuition inverts. Reaching the favourable extreme
  first ratchets the floor up before the adverse move is tested, so MFE-first
  is the harsher pole and MAE-first is the one that flatters survival. The
  floor only ever rises, so every account MAE-first kills, MFE-first kills too;
  the converse is false, and `tests/test_account.py` pins both directions over
  a grid of states. *Bias: favours survival.*

  The orderings can only differ when a single trade's own range (MFE minus
  clamped MAE) covers the whole $1,500 drawdown, since the floor has to climb
  past the adverse point inside that one trade. Two of the 12,658 trades
  qualify and neither lands on an account in the narrow state where it bites:
  both orderings give 22 survivors on `ideal_world` and an identical $102,700
  on the full rulebook. **The choice is inert on this tape**, but it would not
  stay inert at a larger contract size, a smaller drawdown, or a wider tape,
  and `--path-order mfe_first` is then the pole to re-test. The parent resolved
  the same ambiguity with a seeded coin.
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

**The direction is not established, and an earlier version of this file wrongly
called the alive count an upper bound.** Two mechanisms pull opposite ways:

- Concurrent *losers* deepen the true floating drawdown beyond anything the
  per-trade test sees, which would kill accounts the model keeps alive.
- Concurrent *winners* hold the true floating equity above the level the model
  tests each MAE against, which would save accounts the model kills — and at
  the same time lift the true intratrade peak, ratcheting the floor higher and
  making every *later* drawdown deadlier.

The third effect is the awkward one: aggregation changes the floor's history,
not just one test, so the error compounds along a path rather than pointing one
way. Survival here is best described as **uncertain under the approximation**,
not bounded.

The gap is not small. Peak simultaneous exposure on this tape is **5 open
positions**, and **2,887 of 12,658 trades (22.8%)** overlap at least one other.
Closing it needs either an event-driven floating-equity walk or intrabar paths
the completed-trade export does not carry.

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

## Measuring a rule, and what a delta does not say

Two measurements, because they answer different questions. **Fixed-policy**:
remove the rule and change nothing else — this explains the arm being run.
**Adapted-policy**: re-optimise our cushion with and without the rule and
compare the two bests — this is how much the rule narrows what is achievable.
On this tape they disagree by two orders of magnitude, and the adapted number
is the one that describes the firm rather than our own policy.

A pocket delta alone conflates three things, so every arm also reports
**stranded** equity and **value = pocket + stranded**:

- value unchanged, pocket moved -> the rule blocked *access*; the money is
  still in the account;
- value moved -> accounts lived or died differently and the money was never
  earned;
- a **fate count** of zero forces a zero value delta, which is a tested
  invariant rather than an observation.

Denial counts cannot make this distinction, and neither can the withheld
counter on its own: under a cushion, fewer denials usually just means our own
policy stopped asking. `requests_withheld_by_policy` exists so the two are
never summed together.

The adapted number is a **lower bound and only as good as the search**. A
negative delta is always a search failure, never a finding: removing a
constraint cannot narrow what is achievable, so either the grid was too coarse
to follow the optimum as it moved, or the policy space cannot imitate the rule.
Both occur here on a deliberately coarse grid.

## The cushion is headroom, not a balance

`min_retained_balance_usd` is stated as a balance because that is what the
firm's own rules are stated in, but the quantity that matters is its distance
above the **frozen floor at $25,100** — the drawdown the account can absorb
before it liquidates. The winning $30,100 is $5,000 of headroom. Quoting it as
"$5,100 above the starting balance" would be arithmetically true and
economically meaningless: the start is not where the account dies.

The optimum does not transfer. GG peaks at $8,400 of headroom against RR's
$5,000, and both surfaces have $100k cliffs driven by single-account survival
flips. Treat the band, not the point.

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

## Closing the book

A live account at the end of the tape holds equity that has to be scored
somehow, and the choice is not neutral.

- **`liquidate_profit`** converts every dollar above the starting balance to
  cash with no gate, cap or split. This is a **counterfactual about value, not
  a claim about access** — it is the right upper bound and the wrong forecast.
  The $25,000 starting balance is never ours and is never withdrawn.
- **`firm_permitted`** makes **one** request through the rulebook. One, because
  the eight-trading-day gate counts trading days since the last request: a book
  that has stopped trading can never become eligible again. Modelling repeated
  closing requests would require assuming post-horizon trading the tape has no
  evidence for.
- A terminal withdrawal **does not test the threshold**. An account emptied at
  the horizon is closed, not blown, and the alive count is scored as it stood
  before the closing request.

*Bias:* `liquidate_profit` flatters a held book enormously — it reports
$472,299 where the rules permit $14,200.

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

## Supply of funded accounts

**Default: supply is instant and unlimited.** Every purchase is a funded account
available at the next daily check for the flat seat fee ($200 25K / $250 50K).
*Bias: favours any policy that replaces deaths quickly.* The fees are the
user's measured all-in average: evaluation attempts ($33 / $40 a month, one
attempt per month) plus $125 activation, which comes to about 2.3 attempts per
funded 25K and 3.1 per funded 50K.

**Optional spare shelf** (`spare_capacity`, `passes_per_month` on the
acquisition policy). This follows how the user actually operates:

- At most R funded accounts **pass per calendar month**, each paid in full when
  it passes.
- A pass goes live at once if an account is wanted. Otherwise it waits
  **dormant on the shelf**, up to K spares.
- Purchases and replacements draw on spares first, then on any passes left in
  the month. The shelf is restocked afterwards within the same daily check.
- **Spares count toward the 20-account cap.** Every spare held is a slot that
  is not trading.
- Spares never expire and cost nothing further while dormant. Spares still
  dormant at the end of the tape are sunk cost.
- There is no pass delay: evaluations traded at larger size can pass within
  days, and the shelf, not a delay, is how lumpy supply is absorbed.
- Because the fee is paid at pass time, a spare can go live when owner cash is
  zero.

The pass rate is **fixed and deterministic**. Real passes are lumpy, and they
are likely correlated with the book: evaluations trade the same signals, and
deaths cluster when the strategy loses. On the 25K replacement winner, 95% of
deaths fall on days when five or more accounts die together, which is also
when evaluations would be failing. *Bias: a fixed rate flatters replacement
policies in exactly the months they need supply most.* The shelf limits the
supply of funded accounts; it does not trade the evaluation itself.

**Optional evaluation supply** (`evaluation`, `evaluations_at_once`, with a
spare shelf and no pass rate). This replaces the fixed pass rate with
evaluations traded on the same tape. Lumpy months, and passes drying up while
accounts die, then come from the trades rather than from an assumption.

- **One position at a time**, as the owner trades evaluations: the next trade is
  the first to enter at or after the previous exit. Funded accounts still take
  every overlapping signal. Netting of concurrent positions therefore does not
  arise for evaluations.
- **Size and rules** follow the EODMAE study, which chose the sizes:
  - 25K at 3 MNQ, with a $1,500 target and $1,500 drawdown (ratio 1.0);
  - 50K at 5 MNQ, with $3,000 / $2,500 (ratio 1.2);
  - the drawdown trails peak equity, open profit included, and **never
    freezes**;
  - an evaluation passes when a closed balance reaches the target;
  - there are no other rules: no minimum days, no consistency rule.
- **Fees**: $33 / $40 at the start and at each monthly renewal on the start
  day. A blown evaluation is dormant until renewal, which resets it for free;
  a live one carries on. $125 activation on passing.
- **Only when needed**: up to 5 run at once, started only while the book is
  short. Short means deaths not yet replaced, a scheduled purchase missed that
  day, or spares below target. An evaluation no longer needed is cancelled at
  its renewal.
- **Seats**: each evaluation in flight holds one of the 20 seats. A pass is
  activated at the next daily check and joins the shelf, and the purchase
  policy deploys it from there. An order only counts as short on the day it is
  missed, so a monthly order that an evaluation cannot fill in time lets that
  evaluation lapse at renewal.
- **Scheduled purchasing needs spares here.** Without a shelf, a monthly or
  weekly order filled from a spare starts no evaluation for the next order,
  so the book funds only about every other order. On 25K with $5,000 + $200 a
  month, monthly purchasing funds 25 accounts with no spares and 74 with five.
  The study therefore gives every purchase policy the same spare options.
- **Evaluations started together are one draw.** Evaluations that start on the
  same day at the same size trade identical paths and pass or blow together.
  This is the lumpiness the owner reports (about 10 passes in a good month,
  none in a bad one), and it makes outcomes sensitive to start dates.
- **Same path order as the funded accounts** (worst point first). *Bias:
  flatters evaluations.* EODMAE's favourable-first bound is 2–3 points lower
  at these sizes.

**Calibration.** One evaluation started on every weekday, with a 180-day
horizon, passes 97.1% (25K × 3) and 93.3% (50K × 5). EODMAE's
worst-point-first bounds are 97.3% and 93.7%, and the median days to pass
(35.3 and 39.7) are within a day of EODMAE's. The implied cost per activation,
$202 and $239, matches the owner's measured $200 / $250.

## Not modelled

Slippage and partial fills; contract caps and scaling plans; daily loss limits;
evaluation rules beyond drawdown and target, and evaluations for any product
other than Legacy (see the evaluation supply above); pending-order and broker fill
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
