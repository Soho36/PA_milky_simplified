# Routing at matched trade exposure

**Superseded procurement assumption:** this page preserves the original
five-seats-per-purchase experiment. See [corrected capacity reuse and fixed-R
pools](ROUTING_REUSE.md) for the current results. The old overbuying results must
not be presented as the performance of the corrected routing system.

The first controlled experiment is complete. **Full signal coverage does not
preserve the earlier economic rankings under unchanged withdrawal settings.**
The current RR 1.00 tape still has a five-position peak: **K = 5R remains its
historical interval-capacity boundary**, where R means account copies of a
signal, not reward:risk. Tests cover R=1 and R=2; four initial seats require a
fifth even when account death is disabled.

Start with the [paired tables](../../results/legacy_25k/routing_matched_exposure/REPORT.generated.md),
[machine-readable comparison](../../results/legacy_25k/routing_matched_exposure/comparison.csv),
or [independent audit](../../results/legacy_25k/routing_matched_exposure/AUDIT.generated.json).

## What was held fixed

There are 48 reference cases: two fresh starts (2020 and 2023), four inherited
funding schedules, monthly-one and weekly-one purchases, and three inherited
withdrawal settings. Each has two routed counterparts: max-headroom and
round-robin. No withdrawal or reserve setting was re-optimized.

Each reference first runs the existing unlimited-concurrency model. Its actual
trade-copy counts and actual purchase dates are then frozen. Both routed arms
receive exactly those copies of exactly those trades, one whole trade per
physical account, with the same contract size, commission, payout rulebook and
per-account withdrawal policy. Routing never adds to or reduces a position.
Entry priority uses entry time and stable source identifiers, never eventual
exit time or profit. Slots release on exit; a zero-duration exported trade
enters and immediately exits. Working-order lifetimes are not in the exports.

This is an **ex-post controlled replay**, not an executable prospective demand
policy. In particular, the reference's future survival path determines which
copies belong to the frozen comparison tape. A routed survivor does not continue
receiving extra copies after its reference exposure disappears. This prevents
survival improvements from silently increasing trade exposure.

## What was allowed to change

Each original purchase date provisions five routed accounts instead of one.
Additional funded accounts are provisioned and charged at entry only if deaths
would otherwise cause a missed copy. All 96 routed runs attained 100% coverage,
with no overlapping trades on any account. Max-headroom needed no emergency
seats; round-robin needed 37 in total across the 48 separate scenarios.

Physical account purchases, funding and live-account limits are therefore
**not equal**. The original purchase calendar is fixed, but its seat count is
multiplied. All seat costs are subtracted from cash, and the minimum additional
funding needed beyond the original owner contribution schedule is reported.
Owner contributions are not counted as trading income.

The five-per-purchase rule preserves the original acquisition events. It is
**not a minimum-capacity procurement policy**: routed survivors accumulate even
when the original book replaces dead accounts. K can therefore grow far above
five times current R. Peak live accounts ranged from 25 to 420 under max-headroom;
every routed scenario exceeded the reference's 20-live-account cap. These runs
are counterfactual capacity experiments, not feasible 20-account operating plans.

## Findings

- Both routed methods produced less ongoing and total net cash than their own
  reference in all 48 cases under this purchase transformation.
- Max-headroom beat round-robin on total net cash in 45 cases and tied in three.
- The highest-total-net tested policy bundle changed between the reference and
  max-headroom in all eight start/funding groups. These are descriptive rankings
  within the inherited shortlist, not a new optimization or independent tests.
- The 24 full-period reference cases exactly reproduced saved current-study
  totals, ongoing cash, accounts bought and survivors.

For example, with a 2020 start, $5,000 initially plus $200/month in the reference,
and weekly purchases, the same withdrawal settings gave:

| Withdrawal policy | Reference total net | Max-headroom total net | Round-robin total net |
|---|---:|---:|---:|
| Daily minimum, retain $31,900 | $589,340 | $339,583 | $132,345 |
| Weekly maximum, retain $31,600 | $589,140 | $463,274 | $163,033 |
| Monthly minimum, retain $30,000 | $589,140 | $474,799 | $373,347 |

Each row is an exposure-matched comparison; exposure may differ between rows
because each policy has its own reference survival and purchase path. These
totals span the full dataset and include a firm-permitted terminal request.

In the first row, each arm received exactly 208,872 copies. The reference bought
83 accounts; each routed arm bought 415. Account costs rose from $16,600 to
$83,000. Max-headroom required $70,800 of additional external funding on top of
the reference contribution schedule. This extra funding is not the same measure
as the $66,400 incremental purchase cost: receipts arrive at different times.

The loss of cash is not just the seat bill. Spreading the same exposure changes
which accounts accumulate enough profit and qualifying days for payouts, how
much remains in accounts at the horizon, and which trade excursions kill an
account. The saved accounting bridges reconcile these effects but are not
unique causal attributions. Identical entry-copy demand also does not force
identical booked P&L: the inherited model does not book the close of a killing
trade, and account placement changes which trades kill accounts.

## Interpretation and next decision

We should retain K=5R as the verified tape-capacity reference. We should **not**
carry over the best withdrawal/reserve setting unchanged on the assumption
that routing merely scales the old cash results down. That assumption failed
in this controlled replay.

We also should not infer that routing itself is uneconomic. This experiment
charges a deliberately fixed five-per-original-purchase schedule, which can
overbuy severely. A separate acquisition comparison should reuse surviving
free seats before buying new ones and specify a feasible exposure target under
the physical account cap. That would change the purchase policy and belongs
after this fixed-policy control, rather than being blended into its results.

The 2023 start is a sensitivity check, not untouched out-of-sample evidence:
the inherited policies were chosen using the wider dataset. The original
unlimited reference retains its non-aggregated concurrent floating-P&L
approximation. Routed accounts remove simultaneous-position aggregation, but
still apply trade extrema at exit; exact intratrade death times and payout
interactions during open trades remain unobserved.

## Reproduce

```powershell
$env:PYTHONPATH = 'src'
.\venv\Scripts\python.exe scripts/study_legacy_routing.py --profile config/studies/legacy_25k_routing.json
.\venv\Scripts\python.exe scripts/audit_legacy_routing.py --root results/legacy_25k/routing_matched_exposure
.\venv\Scripts\python.exe -m unittest tests.test_routing -v
```

The dedicated [profile](../../config/studies/legacy_25k_routing.json) records the
experiment. Each case has resolved configuration, account ledgers, payouts,
purchase events, and compressed CSVs for frozen demand and every assignment.
`study.json` includes input, engine and evidence hashes. The audit independently
checks each assignment, account occupancy and activation, purchase cost and
receipt total. The serialized router `copies=1` is only its fallback parameter;
in this study the per-trade demand CSV overrides it.
