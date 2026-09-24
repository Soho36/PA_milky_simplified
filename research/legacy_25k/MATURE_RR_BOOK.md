# Fully populated RR books: fixed allocations and recovery

Design recorded 2026-09-24 before results. Compare 10/0/10, 9/2/9 and 8/4/8
seats at RR r/r 0.50/1.00/2.50, plus 20-seat homogeneous controls at each
setting. One MNQ per PA, inherited $1.05 commission. No allocation search.
Initial seats are all populated at the quarter boundary, so first-seat
deployment cannot determine whether the portfolio is initially diversified.

## Matched starting states

Primary: all 20 accounts have a frozen floor at $25,100 and $6,800 headroom
(balance $31,900). Control: the same frozen floor and $1,500 headroom
(balance $26,600). These are already-owned accounts with identical balances,
not selected historical survivors. Initial retained equity is respectively
$138,000 or $32,000 across the book, explicitly an endowment, not run profit.
Do not attribute protection from the larger endowment to r/r diversification.

All accounts begin flat with zero prior payouts, no accrued withdrawal claim
and an empty trading-day record. Their floor is mature, but payout eligibility
must accrue from the new run; no fictitious profitable days are supplied.
This is a controlled initialized state, not a reconstruction of actual accounts.
Original seat acquisition costs are sunk and excluded from forward cash.

## Two phases across all 26 complete quarters

1. Hold: no withdrawals, purchases or replacements; run for the quarter.
   Record original survivors, surviving group composition and realized equity.
   The $1,500 control must reproduce previous fixed-floor component breaches.
2. Recovery: daily minimum withdrawals retaining $6,800 above the frozen floor;
   existing monthly-current-slot replacement rule, $5,000 replacement cash
   plus $200/month, RR 1.00 evaluations, five concurrent evaluations, seven-day
   initiation spacing, two-spare target and shared 20-slot cap. Original seats
   are supplied at time zero without charging them to replacement cash. New
   replacement PAs start with the normal fresh trailing floor and zero profit.
   Run up to 12 months; censor at July 1, 2026 for late cohorts. Mark the three
   shorter follow-ups and do not average unrecovered cases as zero days.

Replacement assignment fills the group with the lowest live-count/target-seat
ratio. Ties use RR 0.50, then RR 2.50, then RR 1.00, omitting absent groups.
This keeps the lower-r/r first convention fixed. No transfers or reassignments
of live accounts. Equal-state peers within a group can still fail together.

All phases use identical calendar boundaries and the union of the three RR
tapes as their clock. Entries before the horizon may remain open beyond it:
they continue to occupy the account, but their future P&L/MAE is not credited.
Deaths remain exit-time proxies with entry-to-exit uncertainty. No new
distance-threshold test. Cohorts overlap and have already been examined.

## Measurements and checks

Record full loss, original survivors after the first quarter, minimum live
accounts, account-days below 5/10/20, empty time, original and replacement
deaths, first recovery to 20 and recovery episodes with censoring. Report
recovery only conditional on an actual loss. Counts measure available seats,
not identical expected earnings per surviving account. Also report receipts,
replacement costs, forward net cash, retained equity, owner funding and
cash-limited decisions. Distinguish seat recovery from return to the target
composition and from recovery of initial retained equity.

Use a study-local adapter to the unchanged simulator: only calendar boundaries
and pre-owned seed inventory differ. Seeded account equity is injected before
any entry. All normal trade, withdrawal and replacement calculations remain
in the original engine. Economic reconciliation explicitly accounts for the
initial equity endowment. Validate horizon censoring, weighted assignment,
capacity, trade non-overlap, reserve enforcement, first markers, source hashes
and independent reconstruction of recovery metrics.

624 cases: 6 allocations x 26 starts x 2 starting states x 2 phases.

```powershell
.\venv\Scripts\python.exe scripts/study_mature_rr_book.py
.\venv\Scripts\python.exe scripts/audit_mature_rr_book.py
```

[Findings](../../results/legacy_25k/mature_rr_book/FINDINGS.md)
