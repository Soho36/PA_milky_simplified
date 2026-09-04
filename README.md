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
  minus denial_on_shortfall         102,700           +0      7      195     116
  minus maximum_payout              102,700           +0      7      195     116
  minus minimum_balance             102,700           +0      7      196     115
  minus minimum_payout              102,700           +0      7      195     116
  minus profit_split                102,700           +0      7      195     116
  minus trading_days                102,700           +0      7      195     116
  minus safety_net                   90,200      -12,500      6      162     112
```

Three findings, none of which the brick ladder would have produced:

1. **The 30% consistency rule is the only expensive rule** — $4,000. Everything
   else is worth $500 or nothing under this policy.
2. **The safety net is worth +$12,500 *to us*.** Removing it does not free
   money, it destroys it: without the net a $500 request is capped only by the
   trailing threshold, so the book pays itself down to $25,105 — a nickel above
   liquidation — and the accounts do not survive to pay again. The firm's rule
   refuses exactly that trade.
3. **Six of ten rules cost nothing here**, because a $500 monthly ask never
   reaches the $1,500 cap, never accumulates $25,000 for the split to bite,
   and never needs more than 8 trading days to accrue.

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

| key | rule | params (25K) | costs |
|---|---|---|---|
| `minimum_balance` | $26,600 at the request, flat | 26600 | $0 |
| `trading_days` | ≥8 trading days since the last request | 8 | $0 |
| `profitable_days` | ≥5 of those with profit ≥ $50 | 5, 50 | $500 |
| `consistency` | no day > 30% of profit balance, through payout 5 | 0.30, 5 | **$4,000** |
| `safety_net` | payouts 1-3 may encroach by one $500 minimum | 500, 3 | **−$12,500** |
| `minimum_payout` | $500, any account size | 500 | $0 |
| `maximum_payout` | $1,500 through payout 5, none after | 1500, 5 | $0 |
| `profit_split` | 100% of first $25,000 cumulative, then 90% | 25000, 0.9 | $0 |
| `processing_delay` | days between approval and cash | 0 (off) | — |
| `denial_on_shortfall` | denied if the balance falls before approval | — | $0 |

The trailing threshold also caps every payout, but it is **not** in the
rulebook — it is the account specification, always on, never switchable.

### Our policy

`cadence` (never / calendar month), `amount_rule` (fixed / maximum / minimum),
`amount_usd`, `shortfall` (skip / accrue backlog / partial), and whether to
round down to whole asks. Brick 1's "hold everything and imagine one withdrawal
at the end" is not a special case in the engine — it is `cadence: never`.

## Scenarios

| scenario | rules | policy | pocket | alive |
|---|---|---|---|---|
| `ideal_world` | none | hold | −$15,800 | 22 |
| `no_rules_monthly_500` | none | $500/month | $95,700 | 5 |
| `full_rulebook_monthly_500` | all | $500/month | **$102,700** | 7 |
| `full_rulebook_monthly_maximum` | all | max allowed | — | — |

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
- `tests/` — 108 tests, including every firm rule against the sentence it came
  from and both sealed baselines reproducing.
- `ASSUMPTIONS.md` — every assumption and which way it bends the result.
