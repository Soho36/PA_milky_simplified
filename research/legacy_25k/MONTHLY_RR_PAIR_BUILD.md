# Build the alternating RR pair from zero: monthly-start sensitivity

Confirmed plan, 2026-09-25: start on every month boundary in 2020–2025,
buy direct PAs without evaluations, alternate RR r/r 0.50 then 2.50 by actual
purchase number, and permit one open position per account. Compare daily
minimum and daily maximum withdrawals at the same $6,800 reserve headroom
($31,900 retained balance).

The first purchase happens on the start boundary. Then buy at most one PA
on each month boundary when fewer than 20 accounts are alive. Continue after
reaching 20 and subsequently losing accounts. Deaths do not trigger immediate
replacements. Months skipped at capacity do not advance the r/r sequence and
do not accumulate purchase entitlements. This is an equal-purchase plan;
surviving allocations can differ from 50/50.

Fresh account balance $25,000, trailing drawdown $1,500, frozen floor $25,100,
one MNQ per trade, $1.05 round-trip commission, inherited MAE-first accounting.
The reserve is a withdrawal threshold earned through trading, not initial
equity supplied to new accounts. Minimum requests $500, maximum requests all
permitted excess, and both check daily under the full historical rulebook.
Processing delay is zero. Terminal withdrawal is disabled.

Acquisition uses the ordinary monthly-one funded-account ledger with a live
cap of 20 and $200 purchase fee. An owner allowance of $200 initially and per
subsequent month guarantees the purchase schedule; no evaluation or cash
scarcity constraint is introduced. Report received payouts minus actual fees,
not contributions or idle cash as trading profit.

There are 144 primary runs: 72 starts × 2 policies, all ending at the last
common exit in the available tapes. Summaries by start year expose unequal
follow-up. Also extract complete first 6/12/24/36-month checkpoints, censoring
later starts instead of treating their shorter follow-up as complete. First
12 months is the principal matched-duration comparison.

Primary outcomes: account deaths, empty-book episodes and empty days. Also
record purchases, capacity at end, peak capacity, first reaching 20, r/r
composition, time below five/ten accounts, ongoing cash and retained equity.
An empty episode must last a positive duration after first activation; a
same-timestamp death and purchase are netted. Death times are exit-time
proxies, not known intratrade breach times. Record the historical peak size
before each episode to distinguish failures during establishment.

Starts overlap extensively; event totals are replay counts, not independent
observations or estimated future probabilities. This requested two-policy
study does not isolate diversification without homogeneous controls.

Audit actual fills against an independent while-flat selector, reconstruct
purchase eligibility and empty intervals independently, reconcile cash and
funding, and reproduce selected cases. Unit checks cover checkpoint boundaries,
terminal empty spells, cap pauses and purchase-order alternation. No shared
engine edits are needed.

- [Report](../../results/legacy_25k/monthly_rr_pair_build/monthly_rr_pair_build__REPORT.md)
- [All starts](../../results/legacy_25k/monthly_rr_pair_build/cases.csv)
- [Independent audit](../../results/legacy_25k/monthly_rr_pair_build/audit.json)

Run `venv/Scripts/python.exe scripts/study_monthly_rr_pair_build.py --workers 4`,
then `venv/Scripts/python.exe scripts/audit_monthly_rr_pair_build.py`.
