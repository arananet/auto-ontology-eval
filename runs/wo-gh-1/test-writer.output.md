I added one test file, `tests/test_run_evidence_live.py`. It checks the evidence that the live-internals run (spec Amendment 3) is supposed to commit under `runs/eval-live/`. That run hasn't happened yet, so the file has 39 tests and 34 of them fail right now. That's on purpose: like the existing `test_run_evidence.py`, they fail instead of skipping, because the spec only counts as done once the evidence is committed.

**Why this file:** the existing 149 tests already cover S1 to S5 and Amendment 3's harness code offline, and they all pass. Nothing tested the actual live-internals run or checked that the default run's evidence in `runs/eval/` stays unchanged. This file fills that gap. What it checks, by Amendment 3 clause:
- **Only the model slots change:** the run records `configuration: live-internals` and its own GitHub Actions run id, which must differ from the default run's 42127124473. `smoke/models.json` must show the three chat slots (`DEFAULT_MODELS_MODEL`, `REASONING_MODEL`, `NON_REASONING_MODEL`) running on the pinned chat model, with the embedding and rerank pins unchanged. That file also has to pass the harness's own `verify_resolved_models` check.
- **Same steps and fail-closed rule:** all five steps pass in order, and the three smoke checks each leave a file.
- **S3 scored the same way:** the conflict marks can be rescored and reclassified from the live catalog, and time to first ontology recomputes from the event timestamps.
- **S4 runs the Auto Ontology arm only:** all 12 fixture questions are present. The raw-schema arm is empty, with no raw responses saved. The correct flags and summary recompute, and the generation settings must match the earlier raw-schema run that now serves as the control.
- **RESULTS-LIVE.md:** it must come out byte for byte the same when rebuilt from the artifacts. Its sections must be in order. The description coverage counts recompute for both catalogs. The control result (8 of 12) and the default figures must cite run 42127124473, and both deltas must recompute. The failure gallery has to show each wrong answer's SQL verbatim, and the limits section has to name each recorded equivalent.
- **Default run untouched:** `runs/eval/` still records run 42127124473 with 0 of 12 correct for Auto Ontology and 8 of 12 for raw schema. Its `RESULTS.md` still rebuilds unchanged from its own artifacts, and no live files land in that directory.
- **API key:** no key or bearer token appears anywhere under `runs/eval-live/`.

**Checks I ran:**
- The full suite fails only in the new file (34 failures, 1 existing skip). Those 34 are all missing-artifact failures; the frozen-default checks already pass.
- I built a fake live run in a temp directory, and all 39 tests passed against it, so they can be satisfied.
- Two deliberate faults were both caught: one chat slot set to the end-of-life model, and an edited default `RESULTS.md`.

I also added a row for the new file to `tests/SCENARIOS.md` and noted under "Not testable offline" that it stays red until the run is committed. Nothing is committed. The other modified files under `runs/wo-gh-1/`, `work_orders/` and `line-output.log` were changed by the factory, not by me.
{"model": "claude-opus-5-5"}
