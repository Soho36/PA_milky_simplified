# Corrected routing: reuse existing capacity

**The purchase error is fixed.** Routing already used one global account pool;
it did not divide accounts into separate five-seat groups. The error was buying
five more seats on every reference purchase date regardless of the available
pool. Those earlier results are retained as the superseded procurement control.

The corrected entry rule is:

```text
shortfall = max(0, requested copies - free eligible accounts)
buy only the shortfall, subject to any configured live-account cap
route the trade through existing and newly available seats
```

Five usable accounts plus six concurrent trades therefore needs one extra seat,
not another five. Five reusable accounts across six calendar months trigger no
calendar purchases. Both examples have regression tests. Deaths can still
require replacement purchases: K measures concurrent capacity, not lifetime
accounts bought.

## Two comparisons, answering different questions

| Experiment | Trade-copy demand | Initial pool and purchases | Live cap |
|---|---|---|---|
| [Corrected matched replay](../../results/legacy_25k/routing_capacity_reuse/REPORT.generated.md) | Identical to each earlier reference run | Start empty; buy only the entry-time shortfall | Relaxed, to preserve the earlier exposure exactly |
| [Fixed-R shared pool](../../results/legacy_25k/routing_fixed_pool/REPORT.generated.md) | R copies of every exported trade; R=1,2,3,4 | Start once with K=5R; reuse seats and buy only shortfalls | 20 live accounts |

The corrected replay isolates the procurement correction. It keeps the same
frozen trade demand, contract size, commissions and withdrawal settings. The old
purchase calendar only affects the reference demand; it no longer orders
physical routed accounts. All 48 reference cases and their demand fingerprints
match the previous experiment, and the 24 full-period references also reproduce
the original saved controls.

The fixed-R experiment removes the inherited growth in exposure. It uses no
future reference survival path and no monthly/weekly acquisition schedule.
Capacity starts at 5, 10, 15 or 20; the pool is shared across all windows.
Initial capacity is paid for. Replacements are bought only when existing free
capacity is insufficient. The configured live cap is enforced: a hypothetical
21st simultaneous requirement is recorded as blocked, not silently purchased.

## Effect of fixing procurement

Both allocation methods improved total net cash in **all 48 paired cases**
relative to the earlier five-per-purchase result. Full trade-copy coverage was
retained. Max-headroom exceeded the original unlimited-account reference in six
cases, so the earlier blanket cash shortfall was not invariant to procurement.
This is not a claim that either router is universally superior.

For the 2020 start, reference funding of $5,000 + $200/month, weekly reference
purchases and max-headroom routing:

| Unchanged withdrawal setting | Previous accounts bought | Corrected accounts bought | Previous total net | Corrected total net |
|---|---:|---:|---:|---:|
| Daily minimum; retain $31,900 | 415 | 110 | $339,583.40 | $434,000.00 |
| Weekly maximum; retain $31,600 | 420 | 120 | $463,274.18 | $552,702.43 |
| Monthly minimum; retain $30,000 | 420 | 120 | $474,799.33 | $556,019.85 |

These are exposure-matched comparisons within each row, not identical demand
between different withdrawal policies. Peak live inventory in these corrected
examples is 100, because the old reference can demand up to 20 copies per signal.
The same-exposure replay cannot honestly be described as a five-account system
or a 20-live-account plan. Its max-headroom peak live counts range from 15 to 100.
The additional owner funding in each of the three examples above is $9,400,
versus $70,800–$71,800 before the correction.

## What one copy with five seats produces

For the 2020 start and **R=1, initial K=5**, all 12,658 exported trades were
filled once under every tested withdrawal setting and both allocation methods.

| Withdrawal setting | Max-headroom: ongoing net | Max-headroom: total net | Round-robin: total net |
|---|---:|---:|---:|
| Daily minimum; retain $31,900 | $25,400.00 | $27,133.54 | $34,614.62 |
| Weekly maximum; retain $31,600 | $28,290.15 | $33,327.25 | $34,159.18 |
| Monthly minimum; retain $30,000 | $19,900.00 | $34,298.93 | $32,598.28 |

Max-headroom bought eight accounts over the entire period: five initial seats
and three replacements, with a peak of five live accounts. Round-robin bought
17 over time, also peaking at five live accounts. These are lifetime purchases,
not 8 or 17 simultaneous accounts.

The full 48-arm fixed-R matrix attained 100% requested coverage and stayed
within the configured 20-live-account cap. Peak live inventory was 5R. The
max-headroom total-net leader among the three inherited settings was monthly
minimum/$30,000 for the 2020 starts, but weekly maximum/$31,600 for the 2023
starts. For R=1 in 2020, the best round-robin total slightly exceeded the best
max-headroom total. Neither the withdrawal policy nor router has a universal
winner here.

The daily and monthly settings have **different retained balances as well as
different timing**. Their cash gap does not isolate the effect of cadence. This
study did not re-optimize either parameter.

## Assumptions that remain

- Funded seats are assumed available immediately when a shortfall appears, at
  the configured $200 cost. Evaluation lead time, activation delays and working
  entry-order reservations are not included.
- Funding needs are measured, not capped. Initial seat funding and the additional
  external cash needed before receipts can finance purchases are reported. Full
  coverage is conditional on that account supply and funding being available.
- The fixed-R live cap is enforced; the matched replay's cap is relaxed and
  explicitly reported. The latter is an ex-post counterfactual, not a live
  strategy driven by future reference outcomes.
- K=5R describes the overlap on this tape. It is not a future capacity guarantee
  and does not remove the need to replace unusable accounts.
- MAE/MFE are still applied at the exported exit time. Exact intratrade failures
  and payout interactions while a trade is open remain approximations.
- Total net includes a firm-permitted terminal request, not unrestricted
  liquidation. All account fees are subtracted; owner funding is excluded from
  income. The 2023 starts are sensitivity checks, not independent policy selection.

## Evidence and reproduction

[Corrected replay CSV](../../results/legacy_25k/routing_capacity_reuse/comparison.csv),
[fixed-R CSV](../../results/legacy_25k/routing_fixed_pool/comparison.csv),
[replay audit](../../results/legacy_25k/routing_capacity_reuse/AUDIT.generated.json),
[fixed-R audit](../../results/legacy_25k/routing_fixed_pool/AUDIT.generated.json).
Each result folder includes configuration, input/engine/evidence hashes, account
ledgers, purchase events, payouts, frozen demand and every routed assignment.
The audit reconstructs free capacity from account lifetimes and earlier fills
to verify that each incremental purchase equals the actual shortfall.

```powershell
$env:PYTHONPATH = 'src'
.\venv\Scripts\python.exe scripts/study_legacy_routing.py --profile config/studies/legacy_25k_routing_reuse.json
.\venv\Scripts\python.exe scripts/study_fixed_routing_pool.py
.\venv\Scripts\python.exe scripts/audit_legacy_routing.py --root results/legacy_25k/routing_capacity_reuse
.\venv\Scripts\python.exe scripts/audit_legacy_routing.py --root results/legacy_25k/routing_fixed_pool
.\venv\Scripts\python.exe -m unittest discover -s tests -t .
```

The previous [five-per-purchase results](ROUTING.md) are preserved for comparison.
Charts that use `routing_matched_exposure` still describe that earlier experiment.
