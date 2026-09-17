# Fixed initial accounts: separate resources from exposure

The allocation ranking depends on the starting period and survival rule.
With no death replacements, both 20-account copying books fail in March 2020;
routing survives and continues withdrawing. A fresh 2023 start reverses the
cash ranking: blocked copying earns more with the same 20 initial accounts.
The matched-exposure comparison also confirms that identical trade copies
can produce different cash extraction because profits reside in different accounts.

[Full tables](../../results/legacy_25k/routing_fixed_inventory/REPORT.generated.md),
[comparison CSV](../../results/legacy_25k/routing_fixed_inventory/comparison.csv),
[independent audit](../../results/legacy_25k/routing_fixed_inventory/AUDIT.generated.json).

## Experiment

All seats are paid for at the first calendar boundary before trading. There
are no later purchases, replacements or owner contributions. Fixed K means
fixed initial inventory, not a constant number of survivors. Every arm in a
case uses the same daily minimum withdrawal rule, retained balance and
firm-permitted terminal request. The main retained balance is $31,900; $30,000
is a separate sensitivity. No withdrawal policy was re-optimized.

The unrestricted benchmark preserves the existing study model. The blocked
and routed arms allow only one exported entry-to-exit interval per account,
consistent with the EA's single-entry execution constraint. The 20-account
routed arms target four copies per signal even after deaths, so lost capacity
appears as missing copies rather than a silently reduced target.

The fresh 2023 start checks sensitivity to the starting period. It is not an
independent validation sample or a date selected as optimal. All cases finish
at the dataset's July 2026 horizon.

## Same resources: 20 initial accounts

Daily minimum withdrawals, retain $31,900. Dollar amounts below subtract the
same $4,000 initial fees. Total net includes terminal receipts.

| Start | Allocation | Copies | Deaths | Signals traded | Ongoing net | Total net |
|---|---|---:|---:|---:|---:|---:|
| 2020 | Unrestricted reference | 7,520 | 20 | 2.97% | -$4,000 | -$4,000 |
| 2020 | Blocked copying | 5,640 | 20 | 2.23% | -$4,000 | -$4,000 |
| 2020 | Max-headroom, R=4 | 49,168 | 12 | 97.11% | $104,000 | $110,891.16 |
| 2020 | Round-robin, R=4 | 50,392 | 8 | 99.53% | $84,000 | $121,938.52 |
| 2023 | Unrestricted reference | 138,640 | 0 | 100% | $406,000 | $508,679 |
| 2023 | Blocked copying | 101,420 | 0 | 73.15% | $356,000 | $356,000 |
| 2023 | Max-headroom, R=4 | 27,728 | 0 | 100% | $68,000 | $68,000 |
| 2023 | Round-robin, R=4 | 27,616 | 8 | 99.60% | $44,000 | $68,284.96 |

Identical copying accounts started together receive the same sequence and
fail together: March 12 for blocked copying and March 13 for unrestricted
copying in 2020. A pool of 20 does not diversify identical trade histories.
Routing spreads those histories and survives, but its unreplaced deaths
cause coverage gaps. Max-headroom misses 1,464 requested copies in that case.

Round-robin beats max-headroom on terminal-inclusive cash at the $31,900
retained balance, but max-headroom delivers more ongoing cash. At $30,000,
max-headroom wins total cash in both starts. Neither allocator has a stable
advantage on every objective or setting. These comparisons are among the
tested policies, not a search of every possible way to operate 20 accounts.

## Same exposure: freeze the unrestricted model's realized copies

This replay uses the unrestricted reference's per-trade modeled copy counts,
not simply its total count. Accounts are all purchased initially and reused.
No new five-account block is purchased when another trade arrives.

For the 2020 start, the reference dies after only 376 exported signals. Its
7,520 copies need at least 60 simultaneous slots; 60 initially funded routed
accounts reproduce them exactly with zero deaths. Both portfolios receive
zero withdrawals. Net cash is therefore -$4,000 for unrestricted versus
-$12,000 for routing. The routed replay deliberately stops accepting signals
when the reference demand stops, despite retaining 60 live accounts. This
is an exposure counterfactual, not a proposed live trading policy.

The 2023/$31,900 case is the cleaner full-period exposure comparison:

| Metric | Unrestricted copying | Matched max-headroom routing |
|---|---:|---:|
| Initial accounts | 20 | 100 |
| Trade copies | 138,640 | 138,640 |
| Signals traded | 100% | 100% |
| Deaths | 0 | 0 |
| Booked net trading P&L | $516,088 | $516,088 |
| Initial account costs | $4,000 | $20,000 |
| Ongoing receipts, after split | $410,000 | $360,000 |
| Ongoing net, after costs | $406,000 | $340,000 |
| Terminal receipts | $102,679 | $0 |
| Total net cash | $508,679 | $340,000 |
| Net retained account profit after terminal request | $2,000.20 | $156,088 |

The $168,679 cash difference consists of $16,000 additional fees, $50,000
less ongoing receipts and $102,679 less terminal receipts. Trading P&L is
identical here; the effect comes from extraction and extra fees. Retained
profit is a net ledger figure across survivors, not immediately withdrawable
cash. Terminal withdrawal follows the configured rules, not free liquidation.

For both 2020 policies, 60 is the required slot minimum for the truncated
reference demand and the replay fills it. For both 2023 policies, the slot
minimum is 100 and the replay fills it. Thus these four exact replays attain
their concurrency lower bounds. The 2023/$30,000 reference eventually dies,
so its exact replay covers 91% of exported signals rather than the full tape.

## Can 100 initial accounts take 20 copies of every signal?

K=5R describes simultaneous occupancy for this tape before account losses.
It does not provide replacement inventory. A separate diagnostic requests
R=20 on every signal, even after the unrestricted reference dies.

| Start | Retained balance | Missed copies with K=100 | First successful tested K | Initial fees | Deaths at that K | Total net at that K |
|---|---:|---:|---:|---:|---:|---:|
| 2020 | $31,900 | 7,320 | 140 | $28,000 | 40 | $576,447.80 |
| 2020 | $30,000 | 8,920 | 180 | $36,000 | 60 | $574,000 |
| 2023 | $31,900 | 0 | 100 | $20,000 | 0 | $340,000 |
| 2023 | $30,000 | 320 | 140 | $28,000 | 0 | $372,000 |

Capacity was tested in steps of 20, with no assumption that survival is
monotonic in K. These are sufficient historical inventories for max-headroom;
140 and 180 are not proven global minima. Choosing K using this entire tape
is an in-sample capacity calibration, not a future coverage guarantee.
Inventories above 20 deliberately omit the operating cap for this experiment.

The 2020 full-target results must not be called matched realized reference
exposure: they include 253,160 copies while the unrestricted book stops at
7,520. The extra initial capacity also supplies additional account-level
loss tolerance; it does not hold aggregate drawdown allowance constant.

## Validation and reproduction

The independent artifact audit checks 27 reported arms, 2,486,064 modeled
copies and 228,148 routed entry offers. It checks initial-only purchases,
account eligibility, no overlapping positions, per-signal targets and exact
exposure matching, account trade counts, fees and cash reconciliation.

```powershell
$env:PYTHONPATH = 'src'
.\venv\Scripts\python.exe scripts/study_routing_fixed_inventory.py
.\venv\Scripts\python.exe scripts/audit_routing_fixed_inventory.py
.\venv\Scripts\python.exe -m unittest discover -s tests -t .
```

The unrestricted model remains a settlement-time counterfactual: overlapping
floating P&L is not aggregated. Failures use exported per-trade extrema at
exit, and working-order reservations are absent. Exact exposure matching
means matching modeled copies, not a reconstructed executable unrestricted
order book. These limitations matter when interpreting mortality and risk.

The preceding [funded growth study](ROUTING_GROWTH.md) remains separate.
Replacements, purchase timing and the 20-account cap materially change the
operating question; these fixed-inventory results do not supersede its dollars.
