I wrote the review to `runs/wo-gh-1/reviewer-tests.review.json` with verdict **pass**.

- **Tests:** `python -m pytest` gives 138 passed, 1 skipped, 280 subtests, 0 failures. The skip is the DuckDB determinism test, which needs the `duckdb` package.
- **Mapping:** `tests/SCENARIOS.md` ties spec items S1–S5, the secrets/pin requirements and the workflow check to specific test files. The spec file now exists, and the earlier wrong-feature and missing-spec problems no longer apply.
- **Committed run:** `test_run_evidence.py` recomputes the checklist marks, time to first ontology, ground truths, scoring and `RESULTS.md` from the artifacts in `runs/eval/`. It fails instead of skipping if that directory is missing.
- **Run outcome:** the Auto Ontology arm scored 0/12. Every answer was "LLM failed to produce a response.", and the cause wasn't diagnosed. The raw-schema arm scored 8/12, so the delta is -8. All four reconciliation marks are "ignored", with table-name quotes only. `RESULTS.md` reports this honestly, so I treated it as an observation rather than a test defect.
- **Minor:** `tests/test_s4_ablation.py` still defines the end-of-life chat model as a local constant, while the spec and `_support.py` pin `nemotron-3.5-lightning-30b-a3b`. It doesn't affect results but should be aligned.
- **Limit:** the offline tests can't show that a fresh live run would reproduce the evidence. It rests on the one committed run, 42127124473.
{"model": "claude-sonnet-5-5"}
