# PA milky, simplified

A Legacy 25K Performance Account book simulator built **one rule at a time**.

Its parents (`Eval_PA_optimal_path`, `Eval_PA_optimal_path_milky`) modelled the
whole economic path in one go — Evaluation phase, purchase cadence, payout
policy, treasury — and the result was hard to attribute: when a number moved,
nothing said which rule moved it.

This project starts from the opposite end. Brick 1 is an **ideal world**. Each
later brick switches on exactly one obstacle and is measured against the sealed
baseline of the brick before it.

The question the whole study answers: **does this strategy stay financially
sound once every real rule is switched on?**

## The bricks so far

| | Brick 1 — ideal world | Brick 2 — $100 a month out |
|---|---|---|
| New rule | — | Withdrawals, gated at $26,600 |
| Accounts alive at end | 22 of 79 | **20 of 79** |
| Withdrawn | $0 | **$76,400** |
| Spent on accounts | −$15,800 | −$15,800 |
| **In our pocket** | **−$15,800** | **+$60,600** |
| Equity left in live accounts | $1,038,099 | $871,781 |
| Copies filled | 150,403 | 137,200 |

Brick 2 is the first brick where the owner is ahead. It is also the first brick
where a rule kills accounts: two that survived the whole tape in brick 1 —
2020-04 and 2024-12 — die once cash is taken out, because a withdrawal spends
cushion the trailing floor never gives back.

## Shared by every brick

| | |
|---|---|
| Tape | `1_sweeps/RR` at RR = 1.00, all 23 hourly windows, 12,658 trades, 2020-01-02 → 2026-07-13 |
| Account | Apex Legacy 25K PA: $25,000 start, $1,500 trailing drawdown measured intratrade, floor freezes at $25,100, touching it kills |
| Book | One new PA on the first instant of every calendar month — 79 months, 79 accounts, never replaced when they die |
| Exposure | 1 MNQ per copy, **unlimited concurrency**: every live account takes every trade from every window, overlapping or not |
| Execution | $1.05 round-turn commission per MNQ, charged in the close only. Zero slippage |
| Cost | $200 per account, charged once at purchase |

## Brick 2 in detail

Withdrawals are $100 per account per month, decided at each calendar month
boundary after the account's opening month.

- **Gate:** the account must show **$26,600** — the $25,000 start, plus the
  $1,500 safety net, plus the $100 being asked for. This is the study's first
  real prop-firm rule.
- **Safety net:** a withdrawal may not cut the balance below **$26,500**, so a
  backlog can never be paid out of protected money.
- **Backlog:** a month the account cannot pay stays owed and is paid later, in
  whole $100 months, once the balance allows.
- Everything else is still ideal — no request counts, no consistency rule, no
  90/10 split, no processing delay.

Of $80,800 accrued over 808 account-months, $76,400 was paid, $4,400 died with
the accounts that owed it, and $0 was still owed at the end.

## Sealed baselines

Each brick's result is sealed under `baselines/<name>/` and becomes the standard
the next brick is measured against. A seal holds the **config embedded rather
than referenced** (so editing `config/` cannot rewrite history), SHA-256 digests
of all 46 input CSVs, every engine module and every output file, the git
revision, and the headline numbers written out in full.

Verification re-runs the sealed config against *today's* engine:

```powershell
$env:PYTHONPATH = 'src'; .\venv\Scripts\python.exe -m pa_milky --verify-all
```

Engine drift is expected as later bricks land and is reported, not failed. What
must not move is the measurement: every pinned value must still come back.
Later bricks may add fields; they may not change one that was sealed.
`tests/test_baseline.py` runs the same check, so a brick that silently moves an
earlier brick's number fails the suite.

## Run

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -t .
```

```powershell
$env:PYTHONPATH = 'src'; .\venv\Scripts\python.exe -m pa_milky
```

`--config config/bricks/brick1_ideal_world.json` re-runs an earlier brick.
`--seal NAME` writes a new baseline. Overrides — each a preview of a future
brick, not a study result:

```powershell
$env:PYTHONPATH = 'src'; .\venv\Scripts\python.exe -m pa_milky --withdraw 250 --no-write
```

Every run writes `summary.json`, `accounts.csv`, `report.txt` and, when cash
moves, `withdrawals.csv` under `results/<timestamp>_<strategy>_rr<rr>/`.

## Layout

- `config/runtime.json` — the current brick. `config/bricks/` — one file per
  sealed brick. Edit config, not code.
- `src/pa_milky/loader.py` — reads the UTF-16 sweep exports and reconciles each
  window against the tester's own `_stats` file.
- `src/pa_milky/account.py` — trailing-drawdown and withdrawal state.
- `src/pa_milky/withdrawals.py` — the monthly decision.
- `src/pa_milky/simulator.py` — the book, walked as one causal stream.
- `src/pa_milky/provenance.py` — sealing and verification.
- `baselines/` — sealed standards. Never hand-edited.
- `tests/` — 76 tests: tape integrity, drawdown mechanics, book construction,
  withdrawal rules, end-to-end invariants, and baseline reproduction.
- `ASSUMPTIONS.md` — what each brick assumes and which way it bends the result.
- `results/` — generated. Never hand-edited.
