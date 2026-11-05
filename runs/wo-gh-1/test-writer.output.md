The new tests are uncommitted in the project repo (`/home/runner/work/auto-ontology-eval/auto-ontology-eval/tests/`). All of them currently fail, as they should before the builder runs: there is no `auto_ontology_eval` package, fixture or eval workflow yet. Every file compiles. Run them from the project root with `python -m unittest discover -s tests -t .`; they need only the standard library. They are offline and use fakes, so no NVIDIA calls and no Docker.

**What I wrote** (the full scenario-to-test map is in `tests/SCENARIOS.md`):
- **`_support.py`:** the values the spec pins (upstream commit, the three model ids) and a fake key short enough that the real-key scan can never flag it.
- **`test_requirements_config_secrets.py`:** the pin, the model ids, and secret handling. A missing or blank `NVIDIA_API_KEY` must stop the run, the key is masked in output, and the environment record never contains it. A scan also checks for real key strings in `src/`, `fixture/`, `tests/` and `.github/`.
- **`test_s1_upstream_smoke.py`:** clone and checkout of the exact commit, and the upstream project's own compose file comes first. The health, catalog and MCP checks each save an evidence file, and the step fails if any check fails, is missing or crashes.
- **`test_s2_fixture.py`:** 8–10 tables, each with a seed CSV and a `CREATE TABLE`. The four planted conflicts are recomputed straight from the CSVs, independently of the harness:
  - the two `net_sales` totals differ by exactly the returns total
  - plant and DC codes map to Source A names but never equal them
  - Source A's hierarchy is brand then category
  - the shared SKUs are exactly the overlap between the sources

  It also checks there are 12 questions, each conflict is covered, each recorded answer matches its reference SQL, and `GROUND_TRUTH.md` lists them. Two more checks: the data loads the same way every time, and the raw schema has no comments and leaks no answers.
- **`test_s3_reconciliation.py`:** each conflict gets exactly one mark. A mark counts only if its quote appears word for word in the catalog. The classifier gives the same result every time, and time to first ontology runs from the second source registering to the first complete export.
- **`test_s4_ablation.py`:**
  - numbers are compared after rounding to 2 decimals, and sets ignore order
  - correctness is scored per arm, with the delta
  - each arm's SQL is saved word for word, and every ontology answer gets a provenance flag
  - ground truth is written before any model call
  - both arms must use the same model and settings (including temperature and max tokens); the run is refused otherwise, and the settings are recorded
- **`test_s5_results_and_fail_closed.py`:** RESULTS.md has the sections in order and takes every value from a run file. Wrong SQL appears word for word in the failure gallery, and there is a limits section. Sections without evidence say "No run evidence", a stopped run names the failed step, and the key never appears. The pipeline stops at the first failed step or missing evidence file, including a missing key.
- **`test_workflow.py`:** `.github/workflows/auto-ontology-eval.yml` runs on ubuntu, gets the key only from the secret, never echoes it, and has no publish steps.

**Choices that limit how the builder can implement it:**
- **Interfaces:** I picked the module, function and file names the builder must use, such as `fixture/source_{a,b}/seeds/<table>.csv`, the `checklist.json` and `questions.json` formats, and `ablation.run(questions, ontology_arm, raw_arm, out_dir)`. The spec doesn't name any of these, so a reviewer should confirm they're acceptable.
- **Reference database:** `fixture.reference_connection()` can use any database engine. DuckDB isn't installed on this runner, so the one DuckDB-only test skips without it.

**Gaps:**
- **Not testable offline:** the live stack, real NIM calls, registering Source A in Postgres, and the real catalog export can only be shown by the executed Actions run.
- **"No claim beyond the fixture":** this is tested only weakly. The limits section must mention "synthetic" and say what was not exercised. A reviewer has to judge this one.
- **Retired chat model:** the earlier builder preflight (`runs/wo-gh-1/builder-preflight.md`) found that the spec's chat model `nvidia/nemotron-3-nano-30b-a3b` returns HTTP 410 (end of life). The tests keep the spec's model id. If the spec owner pins a replacement, change only `tests/_support.py`.

Approval belongs to a different station.
{"model": "claude-opus-5-5"}
