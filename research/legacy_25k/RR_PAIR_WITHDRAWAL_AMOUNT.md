# Monthly withdrawal amounts and reserves: RR 0.50 / 2.50

Requested adaptation of the original [amount x cushion study](../../results/study__full_rulebook__RR__monthly_amount_x_cushion__dual_terminal_scores/study__full_rulebook__RR__monthly_amount_x_cushion__dual_terminal_scores__REPORT.md).
User selected all-signals while flat on 2026-09-25.

New accounts alternate RR r/r 0.50, 2.50, starting with 0.50. Assignment stays
fixed for life and does not respond to earlier deaths. This targets equal
monthly purchases; it does not force the surviving allocation to stay equal.
Fixing assignment across withdrawal settings preserves the meaning of the
no-withdrawal path comparison.

The original acquisition assumptions remain: one funded account each calendar
month, uncapped inventory, $200 externally funded purchases, no additional
replacements or evaluation queue. Accounts start fresh at $25,000 with a
$1,500 trailing drawdown, which eventually freezes at $25,100. One MNQ per
account, $1.05 round-trip commission, inherited MAE-first accounting and full
historical payout rulebook with zero processing delay.

Each account accepts only its own variant's eligible entries while flat.
The old study allowed overlapping positions, so its totals are not a matched
control for the effect of the RR mixture.

The eight policy families and search grid come unchanged from
`config/studies/legacy_25k.json`: fixed $250/500/750/1,000/1,500 backlog,
minimum monthly, maximum excess monthly, and legacy $500 blocks. Search
headroom $0 through $10,000 in $500 increments, plus no voluntary cushion;
refine each family's coarse winner for each cash objective within $500 in
$100 steps. Include no-withdrawal hold. This is an in-sample local search.

Report ongoing net cash and net cash including one final firm-permitted
request on the same trading path. The final request releases the voluntary
cushion but retains firm restrictions. Purchase fees and firm split are
deducted. Compare against a common hold-path accounting ceiling; do not call
the ceiling an achievable payout policy. Test neutrality using actual
per-account accepted trade keys and death keys, rather than aggregate P/L.

Validate the two input tapes against stats and coverage pins; record their
hashes and spans. Check each candidate's economic identity and each accepted
copy's variant, activation, occupancy, trade count and killing trade. Reproduce
hold and both objective winners; check their per-account entry paths against
an independent greedy while-flat selector. No shared simulation source changes.

- [Full report](../../results/legacy_25k/rr_pair_monthly_amount_x_cushion/rr_pair_monthly_amount_x_cushion__REPORT.md)
- [Candidate scores](../../results/legacy_25k/rr_pair_monthly_amount_x_cushion/candidates.csv)
- [Independent audit](../../results/legacy_25k/rr_pair_monthly_amount_x_cushion/audit.json)

Reproduce with `venv/Scripts/python.exe scripts/study_rr_pair_withdrawal_amount.py --workers 4`,
then `venv/Scripts/python.exe scripts/audit_rr_pair_withdrawal_amount.py`.
The mixed allocation requires this runner, not the single-tape CLI.
