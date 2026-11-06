I wrote the review to `runs/wo-gh-1/reviewer-architecture.review.json` with the verdict `changes_requested`.

- **Fits the structure:** The eval sits in the product repo (`src/auto_ontology_eval`, `fixture/`, `tests/`, `runs/eval`, `runs/eval-live`), apart from `.anvil-factory`. It is split by spec scenario S1–S5.
- **No decision records:** The product repo has no `brain/decisions/` directory, so I could not check the change against recorded decisions. The key choices aren't recorded: the in-process MCP probe, the SQLite copy for the raw-schema arm, freezing `RESULTS.md`, and the hosted NIM configuration.
- **Amendment 3 unfinished:** `runs/eval-live/RESULTS-LIVE.md` is missing. That is why the 22 tests in `tests/test_run_evidence_live.py` fail.
- **Two sources of truth:** `runs/eval/RESULTS.md` reports the Auto Ontology arm as 0/12 with no answers because of the retired-model HTTP 410. `S4-DIAGNOSIS.md` says it won't modify `RESULTS.md`. No rule says which document wins.
- **Provenance:** The builder step failed. Its `builder.output.md` described an unrelated design-system feature. Several `runs/wo-gh-1` envelopes and `line-output.log` are modified in the working tree.
- **Not verified:** I did not run the tests or the harness. I relied on the other reviewers' results (166 passed, 22 failed) and read the directory layout, not the source modules.
{"model": "claude-sonnet-5-5"}
