I added `tests/test_run_evidence.py` (37 tests), which checks the committed executed run in `runs/eval/` against the spec. The full suite passes: 134 tests, 1 skipped. I haven't committed anything.

The tests already in the repo cover S1–S5 and the requirements, but only offline with fakes. Reviewers had flagged that nothing checked what the live run actually produced. The new tests recompute every number they can from the raw run files and the fixture, and compare:

- **Requirements:** the recorded environment matches the pinned commit and models (chat model per Amendment 2), with a GitHub Actions run id. Both S4 arms used the pinned model, and the generation settings are recorded. All five steps passed and each left its evidence file. There is no API key anywhere under `runs/`.
- **S1:** health, catalog and MCP checks each passed and left a non-empty evidence file.
- **S3:** there is exactly one valid mark per planted conflict, and a mark counts only if its quote appears verbatim in `catalog.yaml`. Re-scoring the committed catalog reproduces `reconciliation.json` exactly. Time to first ontology recomputes from `events.json`.
- **S4:** the 12 questions match the fixture and each planted conflict is touched by at least one. The ground truths recompute from the reference SQL. Correctness flags, per-arm totals and the delta all recompute. Every Auto Ontology answer has a provenance flag. Raw-schema SQL matches the saved model response exactly, and a missing answer keeps the upstream reason.
- **S5:** `RESULTS.md` sections are in the right order, and its environment, timing, checklist, per-question table, failure gallery and limits all match the run files. Both known substitutes for the literal spec steps (in-process MCP probe, SQLite copy for the raw-schema arm) were recorded by the run itself, with their reasons.

These tests fail rather than skip if `runs/eval/` is missing, because the spec's Done condition requires committed evidence. I also updated `tests/SCENARIOS.md` with the new mapping. It now explains the skipped test: a DuckDB determinism check that only runs when the `duckdb` package is installed.

Two results pass the tests but the reviewers should look at them, because they're weak evidence rather than harness bugs I can prove:
- **Auto Ontology arm scored 0/12** against 8/12 for raw schema (delta −8). Every Auto Ontology answer is the same upstream message, "LLM failed to produce a response." It could be a real failure of the upstream tool or a problem with how the harness calls its chat API; the tests can't tell which.
- **All four planted conflicts are marked "ignored".** The supporting quotes are just table names (`name: fact_sales`, `name: dim_product`). They are verbatim, so they count under the spec, but they show little about how the generated ontology treated each conflict.
{"model": "claude-opus-5-5"}
