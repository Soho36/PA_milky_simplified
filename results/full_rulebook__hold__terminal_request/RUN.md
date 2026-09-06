# Reproduce this result

Folder: `full_rulebook__hold__terminal_request`. Historical scenario/config identifiers remain unchanged.

From the project root:

```powershell
$env:PYTHONPATH = 'src'
.\venv\Scripts\python.exe -m pa_milky --config config/scenarios/hold_then_firm_permitted.json  --out results/full_rulebook__hold__terminal_request
```

The report lists the configured rules individually. `full_rulebook` means the
configured study rulebook; processing delay is disabled in these experiments.
Retained balance is a withdrawal target, not a guarantee against trading losses.
