I've written the review to `runs/wo-gh-1/reviewer-tests.review.json` with verdict `changes_requested`. The offline tests are real and pass, but the live evaluation has not run.

- **Offline tests:** All 89 tests passed with `python -m unittest discover -s tests -t .`. They map to the spec scenarios in `tests/SCENARIOS.md`.
- **Live run:** The only executed run, GitHub run 41971180197, stopped at the preflight step. The spec's chat model `nvidia/nemotron-3-nano-30b-a3b` returned HTTP 410. NVIDIA retired it on 2026-09-01. The smoke check, reconciliation scoring, ablation and time to first ontology therefore have no evidence. The only RESULTS.md says "No run evidence" for each of those sections.
- **Fail-closed behaviour:** The harness recorded the failure and did not estimate any numbers.
- **Needed next:** Someone has to pick a chat model that is still served. Then the workflow can be rerun and the real RESULTS.md committed. I also suggested adding an offline test that treats a preflight 410 or 404 as its own failure type.
- **No checks gate:** The checks gate is `not_configured`, so nothing automated runs these tests.

I did not change any files other than the review file.
{"model": "claude-sonnet-5-5"}
