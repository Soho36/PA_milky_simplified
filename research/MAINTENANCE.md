# Project organization and maintenance

The reader hierarchy is product -> overview -> question -> evidence. Physical
result paths are deliberately unchanged to preserve links, provenance and user
notes. Long historical filenames need not be exposed in the normal reading path.
New product output locations belong in its study profile.

Keep these roles distinct:

- `research/`: curated interpretation and reading order.
- `results/`: generated evidence and original reader commentary.
- `baselines/`: sealed regression evidence, not disposable duplicate reports.
- `archives/`: prior output snapshots; current rankings should not link here.
- `config/studies/`: reproducible study design; `products/` and `firm/` remain
  separate so a product can use a distinct verified rulebook.
- `src/`, `tests/`: one shared implementation and validation suite.
- `1_sweeps/`, `venv/`, `.idea/`: local data/runtime/editor state; already ignored.

The old brick runs, ablations and coarse/fine sweeps are historical evidence.
They are not deleted merely because the final operating study does not use
all of them. Delayed-payout logic and tests remain useful despite delay being
off in headline experiments. No core module has been established as redundant.

Known legacy limitations to address deliberately, rather than during navigation:

- `replace_on_death` is serialized but does not drive simulator purchases.
  Use acquisition policies for replacements; do not treat that flag as active.
- `max_accounts` limits the legacy monthly purchase sequence, not live seats.
  Funded acquisition uses `max_live_accounts`.
- The standalone historical sweep runner and audit's historical-study matching
  are not generic multi-product orchestration. Adapt them when needed.
- Study prose and policy families still have domain conventions. A future
  product requires reviewed report interpretation and boundary tests, not just
  changing starting balance.

No EOD implementation or project split is decided here. That decision waits
for its verified mechanics and rulebook.
