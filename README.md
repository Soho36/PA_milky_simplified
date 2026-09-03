# PA milky, simplified

A Legacy 25K Performance Account book simulator built **one rule at a time**.

Its parents (`Eval_PA_optimal_path`, `Eval_PA_optimal_path_milky`) modelled the
whole economic path in one go — Evaluation phase, purchase cadence, payout
policy, treasury — and the result was hard to attribute: when a number moved,
nothing said which rule moved it.

This project starts from the opposite end. Brick 1 is an **ideal world**: the
strategy's own trading rules and the Legacy 25K trailing drawdown, and nothing
else. No slippage, no payout rules, no Evaluation phase, no contract caps, no
capital constraint. Each later brick adds exactly one obstacle and is measured
against the brick before it.

The question the whole study answers: **does this strategy stay financially
sound once every real rule is switched on?**

## Brick 1 — the ideal world

| | |
|---|---|
| Tape | `1_sweeps/RR` at RR = 1.00, all 23 hourly windows, 12,658 trades, 2020-01-02 → 2026-07-13 |
| Account | Apex Legacy 25K PA: $25,000 start, $1,500 trailing drawdown measured intratrade, floor freezes at $25,100, touching it kills |
| Book | One new PA on the first instant of every calendar month — 79 months, 79 accounts, never replaced when they die |
| Exposure | 1 MNQ per copy, **unlimited concurrency**: every live account takes every trade from every window, overlapping or not |
| Execution | $1.05 round-turn commission per MNQ, charged in the close only. Zero slippage |
| Cost | $200 per account, charged once at purchase |
| Not modelled | payouts, consistency rules, slippage, contract caps, daily loss limits, the Evaluation phase, order lifecycle |

## Run

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -t .
```

```powershell
$env:PYTHONPATH = 'src'; .\venv\Scripts\python.exe -m pa_milky
```

Useful overrides — each one is a preview of a future brick, not a study result:

```powershell
$env:PYTHONPATH = 'src'; .\venv\Scripts\python.exe -m pa_milky --strategy GG --commission 0 --path-order mfe_first --no-write
```

Every run writes `summary.json`, `accounts.csv` and `report.txt` under
`results/<timestamp>_<strategy>_rr<rr>/`.

## Layout

- `config/runtime.json` — every value the simulator reads. Edit here, not in code.
- `src/pa_milky/loader.py` — reads the UTF-16 sweep exports and reconciles each
  window against the tester's own `_stats` file.
- `src/pa_milky/account.py` — the trailing-drawdown state machine.
- `src/pa_milky/simulator.py` — the monthly book.
- `src/pa_milky/report.py` — summary, ledger and rendering.
- `tests/` — 44 tests: tape integrity, drawdown mechanics, book construction,
  and end-to-end invariants on the real tape.
- `ASSUMPTIONS.md` — what brick 1 assumes, and which way each assumption bends
  the result.
- `results/` — generated. Never hand-edited.
