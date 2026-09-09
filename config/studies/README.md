# Study profiles

The study runners accept `--study PATH`. Paths inside a profile resolve
from the repository root. The default is `config/studies/legacy_25k.json`.
Existing commands and output locations are retained.

```powershell
.\venv\Scripts\python.exe scripts/study_withdrawal_amount.py --study config/studies/legacy_25k.json
.\venv\Scripts\python.exe scripts/study_withdrawal_cadence.py --study config/studies/legacy_25k.json
.\venv\Scripts\python.exe scripts/study_account_purchases.py --study config/studies/legacy_25k.json
.\venv\Scripts\python.exe scripts/study_budgeted_withdrawal_cadence.py --study config/studies/legacy_25k.json
```

Run purchases before budgeted cadence, which verifies shared controls against
its saved source. The amount runner also supports `--workers` and `--out`.
Worker processes read the same command-line profile. New simulation outputs
embed the profile and its hash alongside resolved scenario/input provenance.
Older saved outputs retain their original provenance; this refactor does not
retroactively label them as reruns.

Profiles specify scenario, output folders, budgets, live cap, amount-policy
family, headroom/refinement grid, cadence grid and purchase withdrawal shortlist.
The eleven acquisition algorithms and common simulation conventions remain code;
this is not an arbitrary workflow language. Use separate output locations for a
new product or changed experiment design. A ready profile must use distinct
folders for its studies.

`legacy_50k.json` is a placeholder and fails before loading data or writing
results. It must not be enabled simply by changing `status`: all verified
product/rulebook/scenario and experiment settings must first be supplied.

Reader-maintained REPORT.md and report_breakdown.txt are not replaced by runs.
Current generated reports live in REPORT.generated.md. Budgeted cadence's
`--refresh-purchase-tables` refreshes presentation from saved cadence rows and
rechecks purchase controls; it is not a new cadence simulation.

The replacement comparison uses the `replacements` output key:
`venv/Scripts/python.exe scripts/study_monthly_replacements.py --study config/studies/legacy_25k.json`.
