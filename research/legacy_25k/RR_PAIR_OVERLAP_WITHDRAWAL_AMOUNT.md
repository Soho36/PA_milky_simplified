# RR 0.50 / 2.50: overlapping-position amount x cushion study

Requested 2026-09-25 after the while-flat study. Repeat the same eight monthly
withdrawal families, coarse reserve grid and per-family/objective refinement,
allowing every eligible own-variant signal even if an account is occupied.

Keep the same monthly purchases, alternating RR r/r 0.50 then 2.50, fixed for
life. No cap, cash constraint, evaluation queue or additional replacements.
One MNQ **per trade**, so concurrent account exposure can exceed one MNQ.
Fresh $25,000 accounts, $1,500 trailing drawdown, $25,100 frozen floor,
$200 purchase fee, $1.05 round-trip commission and the inherited payout rules.

The implementation deliberately matches the original unlimited-concurrency
study's accounting abstraction: process whole-trade P/L, MAE and MFE in exit
order. It does not reconstruct aggregate mark-to-market across simultaneous
open positions. After a death, later settlements are ignored even if their
entries preceded death. This is the legacy model, not a tick-level margin
simulation. The comparison must be described accordingly.

`rr_overlap_support.py` copies the existing event-loop functions into isolated
bindings and changes only the account filter for each variant. The shared
engine and existing studies remain unchanged. Fixed assignments preserve the
hold-path benchmark across withdrawal policies. Fingerprints use exact booked
trade keys per account and killing trades.

Validate every candidate's cash identity and settled-copy membership. Reproduce
hold and both winners, independently selecting all native settlements from
activation through death. Reproduce the original RR1 hold and both leaders,
and check the single-variant adapter against the unmodified legacy engine.

Compare the new results with both the mixed while-flat study and the original
RR1 overlapping study. Include common policy/reserve settings as well as each
study's separately selected winners. Local winning thresholds remain in-sample;
different outcomes do not establish a uniquely optimal r/r allocation.

- [Findings and comparison](../../results/legacy_25k/rr_pair_overlap_monthly_amount_x_cushion/FINDINGS.md)
- [Full report](../../results/legacy_25k/rr_pair_overlap_monthly_amount_x_cushion/rr_pair_overlap_monthly_amount_x_cushion__REPORT.md)
- [Audit](../../results/legacy_25k/rr_pair_overlap_monthly_amount_x_cushion/audit.json)

Reproduce: `venv/Scripts/python.exe scripts/study_rr_pair_overlap_withdrawal_amount.py --workers 4`,
then `venv/Scripts/python.exe scripts/audit_rr_pair_overlap_withdrawal_amount.py`.
