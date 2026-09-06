# PA milky, simplified

A Legacy 25K Performance Account book simulator where **the account is stone
and the firm's rules are switches**.

Its parents (`Eval_PA_optimal_path`, `Eval_PA_optimal_path_milky`) modelled the
whole economic path at once, and when a number moved nothing said which rule
moved it. The first answer here was a brick ladder — add one obstacle, measure,
repeat. The ladder works but only ever yields *marginal* effects in the order
rules happened to be added.

The rulebook does better. Every Apex payout rule is implemented and
independently switchable, so each rule's own price is an **ablation** away: run
everything on, then everything-minus-one, and read the deltas. The ladder is
still reproducible — it is just a series of scenarios.

## The headline: holding is a trap

"Hold everything, then withdraw at the end" was the study's original ideal. It
only means anything once the closing withdrawal is explicit, and there are two
honest readings of it:

| arm | pocket | what it means |
|---|---|---|
| hold → idealized liquidation | **$472,299** | what the equity was *worth* |
| hold → one firm-permitted request | **$14,200** | what could actually be taken |

The held book ends with $488,099 of equity in 22 live accounts and can extract
**6.2% of it**. Twenty accounts get $1,500 each and stop; two get nothing.
That is the worst arm in the entire study — worse than taking $500 a month.

**Why:** the safety net expires after payout three and the $1,500 maximum after
payout five. A held book's closing request is payout number *one*, so both
bind. There is no second request either: the eight-trading-day gate counts
trading days *since the last request*, and a book that has stopped trading
never earns another.

So a payout history is not just income — it is the thing that makes the account
liquidatable at all:

| arm | pocket | closing request takes |
|---|---|---|
| hold → firm-permitted | $14,200 | 6.2% of equity |
| monthly $500, no cushion → firm-permitted | $134,342 | 88.1% |
| monthly $500 + $30k cushion → firm-permitted | **$436,444** | 94.0% |
| monthly $500 + $30k cushion → idealized | $446,063 | 100% |

The tested $30,000 retained-balance arm reaches **$436,444** — within 8% of the $472,299
idealized hold benchmark, and 31× the held book. Once the history exists, the
rules barely bind at liquidation.

## What the rulebook costs, measured two ways

A rule can be measured against a **fixed** policy or an **adapted** one, and
they answer different questions. Both are reported.

### Fixed policy — why *this* arm earns what it earns

$500 a month, no cushion, pocket $102,700:

```
  arm                            pocket   d.pocket    d.value  alive  fates
  all rules on                  102,700          -          -      7      -
  minus consistency             106,700     +4,000     +1,234      6      7
  minus profitable_days         103,200       +500       +500      7      1
  minus safety_net               90,200    -12,500    -19,245      6      4
  (six other rules)             102,700         +0         +0      7      0
```

`d.value` is cash plus **remaining paper profit after any terminal payout**.
It is not withdrawable wealth and cannot identify delayed cash by itself.
Every fixed-policy arm now includes an exact cash bridge and per-account receipt
timing. See [ECONOMIC_EFFECTS.md](ECONOMIC_EFFECTS.md) for definitions and limits.

### Adapted policy — how much the rules narrow what is achievable

Re-optimising the cushion over 21 levels for every arm:

```
  arm                          best pocket        delta   best headroom
  all rules on                     358,000            -           5,000
  minus profit_split               360,200       +2,200           5,000
  minus consistency                358,050          +50           4,500
  minus maximum_payout             358,050          +50           4,500
  (six other rules)                358,000           +0           5,000
```

**The entire firm rulebook costs $2,200.** `consistency`, which looks like a
$4,000 rule against a fixed policy, costs $50 once the policy may adapt.
`safety_net`, which looked worth −$12,500, costs nothing.

Set against that: choosing the cushion at all is worth **$255,300**
($102,700 → $358,000). The lever we control matters roughly 116× more than
every rule the firm imposes. The fixed-policy table was largely measuring our
own policy's inadequacy.

**Caveat on the adapted number.** This is a difference between grid optima,
not a lower or upper bound. Either side may miss a better policy. A restricted
policy family may also be unable to reproduce the behaviour of a removed rule.

### The cushion is headroom, not a balance

The frozen floor sits at **$25,100** — the $25,000 start plus the $100 the
trailing drawdown stops at. So the winning $30,100 retained balance is
**$5,000 of headroom above liquidation**, and that is the number that means
something: it is the drawdown the account can absorb before it dies. On the GG
tape the peak is $8,400 of headroom, so the level genuinely does not transfer.

## The four layers

```
config/
  products/legacy_25k.json           STONE. balance, trailing DD, freeze, seat cost
  firm/apex_payout_rules.json        SWITCHABLE. every rule: enabled + params
  policies/monthly_500.json          OURS. what we ask for and how often
  scenarios/full_rulebook_...json    a named run binding the three to a tape
```

Only scenarios are sealed, and a scenario resolves to one fully embedded
payload at seal time, so provenance is unaffected by the layering.

### The firm rulebook

| key | rule | params (25K) | fixed | adapted |
|---|---|---|---|---|
| `minimum_balance` | $26,600 at the request, flat | 26600 | $0 | $0 |
| `trading_days` | ≥8 trading days since the last request | 8 | $0 | $0 |
| `profitable_days` | ≥5 of those with profit ≥ $50 | 5, 50 | $500 | $0 |
| `consistency` | no day > 30% of profit balance, through payout 5 | 0.30, 5 | $4,000 | $50 |
| `safety_net` | payouts 1-3 may encroach by one $500 minimum | 500, 3 | −$12,500 | $0 |
| `minimum_payout` | $500, any account size | 500 | $0 | $0 |
| `maximum_payout` | $1,500 through payout 5, none after | 1500, 5 | $0 | $50 |
| `profit_split` | 100% of first $25,000 cumulative, then 90% | 25000, 0.9 | $0 | **$2,200** |
| `processing_delay` | days between approval and cash | 0 (off) | — | — |
| `denial_on_shortfall` | denied if the balance falls before approval | — | $0 | $0 |

The trailing threshold also caps every payout, but it is **not** in the
rulebook — it is the account specification, always on, never switchable.

### Our policy

`cadence` (never / calendar month), `amount_rule` (fixed / maximum / minimum),
`amount_usd`, `shortfall` (skip / accrue backlog / partial), whether to round
down to whole asks, `min_retained_balance_usd` — a cushion *we* choose to leave
in an account, independent of anything the firm requires — and
`terminal_withdrawal` (`none` / `liquidate_profit` / `firm_permitted`), what to
do with a live account when the tape runs out. Brick 1 is `cadence: never` with
no closing withdrawal; the two hold benchmarks are the same with one.

## Result folders

See [the results index](results/README.md) for descriptive folder names, report
links, original scenario IDs, and regeneration commands. Config filenames and
sealed baseline names remain stable.

## Scenarios

| scenario | rules | policy | pocket | alive |
|---|---|---|---|---|
| `ideal_world` | none | hold, no closing | −$15,800 | 22 |
| `hold_then_liquidate` | none | hold → idealized | $472,299 | 22 |
| `hold_then_firm_permitted` | all | hold → one request | $14,200 | 22 |
| `monthly_500_cushion_liquidated` | all | $500/mo + $30k cushion → request | **$436,444** | 17 |
| `no_rules_monthly_500` | none | $500/month | $95,700 | 5 |
| `full_rulebook_monthly_500` | all | $500/month | **$102,700** | 7 |
| `full_rulebook_monthly_maximum` | all | max allowed | — | — |
| `no_rules_monthly_500_cushion` | none | $500/month + our $26,100 floor | **$107,200** | 6 |
| `full_rulebook_monthly_500_cushion` | all | $500/month + our $26,100 floor | $102,700 | 7 |

## Sealed baselines

Each result is sealed under `baselines/<name>/` with the config **embedded
rather than referenced**, SHA-256 of all 46 input CSVs, every engine module and
every output, the git revision, and the headline numbers in full.

```powershell
$env:PYTHONPATH = 'src'; .\venv\Scripts\python.exe -m pa_milky --verify-all
```

Verification re-runs the sealed config against *today's* engine. Engine drift is
reported, not failed; a moved number is a failure. `brick1_ideal_world` and
`brick2_monthly_100` were sealed under the old flat schema and still reproduce
bit-for-bit through the rulebook — the legacy payload is translated onto the
same layers, not run down a second code path.

## Run

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -t .
```

```powershell
$env:PYTHONPATH = 'src'; .\venv\Scripts\python.exe -m pa_milky --ablate --ablate-adapted
```

`--config config/scenarios/<name>.json` picks a scenario, `--rule-off KEY`
(repeatable) switches one rule off ad hoc, `--withdraw N` overrides the monthly
ask, `--seal NAME` writes a baseline.

## Layout

- `src/pa_milky/clock.py` — Europe/Tallinn, trading-day identity, DST validation.
- `src/pa_milky/loader.py` — UTF-16 sweep exports, reconciled per window.
- `src/pa_milky/account.py` — drawdown state and the daily P&L ledger.
- `src/pa_milky/firm.py` — the ten rules and the decision pipeline.
- `src/pa_milky/policy.py` — what we ask for.
- `src/pa_milky/payouts.py` — the monthly decision and its denial ledger.
- `src/pa_milky/simulator.py` — the book, walked as one causal stream.
- `src/pa_milky/ablation.py` — one arm per rule, fixed and adapted, with the
  pocket/stranded/value decomposition.
- `src/pa_milky/provenance.py` — sealing and verification.
- `scripts/sweep_cushion.py` — sweep our retained cushion on either policy or tape.
- `tests/` — 145 tests, including every firm rule against the sentence it came
  from, the excursion-ordering property over a grid of states, delayed payouts
  proved causal, both closing benchmarks, and all five sealed baselines
  reproducing.
- `ASSUMPTIONS.md` — every assumption and which way it bends the result.
