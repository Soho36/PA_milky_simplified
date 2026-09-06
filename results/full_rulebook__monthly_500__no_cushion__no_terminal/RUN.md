# Reproduce this result

Folder: `full_rulebook__monthly_500__no_cushion__no_terminal`. Historical scenario/config identifiers remain unchanged.

From the project root:

```powershell
$env:PYTHONPATH = 'src'
.\venv\Scripts\python.exe -m pa_milky --config config/scenarios/full_rulebook_monthly_500.json --ablate --out results/full_rulebook__monthly_500__no_cushion__no_terminal
```

The report lists the configured rules individually. `full_rulebook` means the
configured study rulebook; processing delay is disabled in these experiments.
Retained balance is a withdrawal target, not a guarantee against trading losses.
