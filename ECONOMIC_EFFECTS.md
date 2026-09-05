# Economic effects

Run the existing `--ablate` command. Each arm in `ablation.json` now has
`accounting`, `cash_bridge`, and `receipt_timing`. The console shows the bridge
and timing summary, also saved in `report.txt`. Historical saved outputs must be regenerated to gain these fields.

The canonical results for this experiment are in
`results/full_rulebook_monthly_500/`, including `INTERPRETATION.md`. Regenerate with:

```powershell
$env:PYTHONPATH = "src"
.\venv\Scripts\python.exe -m pa_milky --config config/scenarios/full_rulebook_monthly_500.json --ablate --out results/full_rulebook_monthly_500
```

## An exact cash bridge

For each run, after terminal payouts:

    pocket = booked net trading earnings
             - firm split
             - remaining live-account profit (signed)
             - positive failed-account ledger balances
             + negative failed-account ledger balances
             - purchase fees

All amounts exclude nominal starting balances. The bridge differences these
terms, arm minus baseline, and assigns their signs so its contributions sum to
the observed cash difference. `residual_usd` must be zero. Negative failed
balances are accounting offsets, not cash reimbursements from the firm.

The engine does not book the close or commission of a trade that kills an
account intratrade. Failed-account buckets therefore describe the last booked
ledger residual, not profit recoverable at the actual liquidation fill. A
positive bucket is booked profit removed when the account fails; some of that
profit may have been consumed by the unbooked killing excursion. It is not a
precise measurement of profit forfeited *after* liquidation losses.

Differences in booked earnings measure what the two simulated paths earned,
including differences at killing trades. They are not forecasts of profits an
account would have earned beyond the tape. Firm split can change cash without
changing survival. Equal combined cash and paper profit does not prove pure delay.

## Receipt timing

Within each account, match the first dollar received in the baseline to the
first dollar received in the arm, then the second, and so on (FIFO cumulative
receipt matching). Splitting one receipt into several does not lose money.
Report amounts earlier, later and simultaneous, signed dollar-days (positive
means the arm paid later), and unmatched dollars on each side. Matching uses
owner receipts after the split, including terminal receipts. Fees are in the
cash bridge, not in this payout-timing comparison.

This is a descriptive comparison of receipt schedules. It does not track a
specific denied request or prove causation, particularly when account paths
change. Unmatched receipts are unresolved amount differences at the horizon;
remaining equity is not labelled delayed cash. A $500 receipt moved ten days
later with no amount change produces $5,000 dollar-days, not a $500 permanent loss.
No discount rate or dollar opportunity cost is assumed.

## Terminal consistency

Cash and retained profit are both measured after terminal payouts. Historical
`equity_at_horizon_usd` still describes the pre-liquidation book for existing
reports; the economic layer must not add it to post-liquidation cash.

## Interpretation

Use the bridge to explain the arithmetic, the receipt schedule to describe
timing, and fate counts as supporting context. None alone establishes a causal
allocation of a rule's total effect. Adapted deltas remain differences between
best tested policies, not mathematical bounds on the unrestricted optimum.
