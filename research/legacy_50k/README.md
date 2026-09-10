# Legacy 50K research

The product is now configured, using the user's $250 seat fee and a separately
verified Legacy rulebook. Start with [sources and model limits](SOURCES.md), then
[current findings](OVERVIEW.md).

The focused operating study uses matched 25K controls, a fresh funded reserve/
withdrawal search, and monthly, weekly and current-month replacement policies.
The old uncapped ablation ladder is not repeated. Full study settings are in
[the 50K profile](../../config/studies/legacy_50k.json).

All output is under `results/legacy_50k/`. A loader guard rejects overlapping
25K/50K output directories, including nested paths. Existing 25K evidence stays
at its original locations. The `*.template.json` rulebook placeholder is
historical scaffolding; the scenario uses `config/firm/legacy_50k.json`.

Run from the repository root:

```powershell
.\venv\Scripts\python.exe scripts/study_legacy_50k_operating.py
```

The translated 25K withdrawal anchors in the profile are equal-headroom controls,
not presumed 50K optima. EOD accounts remain deferred.
