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

## What the ablation says

Full rulebook, $500 requested per account per month, 79 accounts over the
2020-2026 tape:

```
  arm                                pocket        delta  alive  payouts  denied
  all rules on                      102,700            -      7      195     116
  minus consistency                 106,700       +4,000      6      215      94
  minus profitable_days             103,200         +500      7      201     110
  minus safety_net                   90,200      -12,500      6      162     112
  (six other rules)                 102,700           +0      7      195     116
```

**Read a delta as what that rule did to *this* arm, not as its price.** The
other rules stay on and the policy stays fixed, so interactions are not
additive and a policy that adapted would answer differently. The safety net is
the case in point.

### The safety net is not worth $12,500 — having any cushion is

The −$12,500 above says removing the net *destroys* money, which reads as "the
firm protects us". It does not survive the obvious control. Give our own policy
a floor of its own — never take an account below $26,100, the same level the
net enforces — and re-run:

| arm | pocket | alive |
|---|---|---|
| no rules, no cushion | $95,700 | 5 |
| full rulebook, no cushion | $102,700 | 7 |
| **no rules, our own cushion** | **$107,200** | 6 |
| full rulebook, our own cushion | $102,700 | 7 |

The best arm is **no firm rules plus a cushion we chose**. Re-ablated against
that policy, `safety_net` measures **exactly $0** — the entire effect was our
policy having no cushion, not the rule having value. And with a cushion in
hand the rulebook is a net **cost of $4,500**, which is the sign the naive
comparison reported backwards.

What survives both framings: **consistency is the only expensive rule** at
$4,000, and six of ten cost nothing here because a $500 monthly ask never
reaches the $1,500 cap, never accumulates $25,000 for the split, and never
needs more than 8 trading days.

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

Deltas below are for the `$500/month, no cushion` arm only — see the caveat
above before quoting any of them as a rule's price.

| key | rule | params (25K) | delta, that arm |
|---|---|---|---|
| `minimum_balance` | $26,600 at the request, flat | 26600 | $0 |
| `trading_days` | ≥8 trading days since the last request | 8 | $0 |
| `profitable_days` | ≥5 of those with profit ≥ $50 | 5, 50 | $500 |
| `consistency` | no day > 30% of profit balance, through payout 5 | 0.30, 5 | **$4,000** |
| `safety_net` | payouts 1-3 may encroach by one $500 minimum | 500, 3 | −$12,500, but **$0** with a cushion |
| `minimum_payout` | $500, any account size | 500 | $0 |
| `maximum_payout` | $1,500 through payout 5, none after | 1500, 5 | $0 |
| `profit_split` | 100% of first $25,000 cumulative, then 90% | 25000, 0.9 | $0 |
| `processing_delay` | days between approval and cash | 0 (off) | — |
| `denial_on_shortfall` | denied if the balance falls before approval | — | $0 |

The trailing threshold also caps every payout, but it is **not** in the
rulebook — it is the account specification, always on, never switchable.

### Our policy

`cadence` (never / calendar month), `amount_rule` (fixed / maximum / minimum),
`amount_usd`, `shortfall` (skip / accrue backlog / partial), whether to round
down to whole asks, and `min_retained_balance_usd` — a cushion *we* choose to
leave in an account, independent of anything the firm requires. Brick 1's "hold
everything and imagine one withdrawal at the end" is not a special case in the
engine — it is `cadence: never`.

## Scenarios

| scenario | rules | policy | pocket | alive |
|---|---|---|---|---|
| `ideal_world` | none | hold | −$15,800 | 22 |
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
$env:PYTHONPATH = 'src'; .\venv\Scripts\python.exe -m pa_milky --ablate
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
- `src/pa_milky/ablation.py` — one arm per rule.
- `src/pa_milky/provenance.py` — sealing and verification.
- `tests/` — 117 tests, including every firm rule against the sentence it came
  from, the excursion-ordering property over a grid of states, delayed payouts
  proved causal, and all three sealed baselines reproducing.
- `ASSUMPTIONS.md` — every assumption and which way it bends the result.
