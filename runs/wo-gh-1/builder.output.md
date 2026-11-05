RESULTS.md now lists every place the run substituted an equivalent for the literal spec step, with the reason, as the amended S5 requires. The full test suite passes: 97 tests, 1 skipped because it needs DuckDB, which isn't installed here. That fixes the 9 failures from the new limits test. This pass didn't run against the live stack, so the end-to-end GitHub Actions run (the work order's "Done" condition) still hasn't happened, and there is no executed RESULTS.md yet.

**What changed** (in the project repo, not committed):
- **New `src/auto_ontology_eval/equivalents.py`:** records each substitution in a run file, `equivalents.json`. Each entry says which scenario, what the spec asked for, what the run did instead, and why.
- **`pipeline.py`:** a rerun deletes the previous run's file. A fresh, empty one is started once the API key passes its check.
- **`live.py`:** the two known cases are recorded at the point the live steps use them:
  - **S1:** MCP tools are listed in process. The pinned MCP server isn't part of the upstream Docker Compose stack, and its network endpoint needs an OAuth token from the web login.
  - **S4:** the raw-schema arm's SQL runs on an in-memory SQLite copy of the fixture. The two live sources are separate engines, so one query from the model can't join across them. The reference answers are also computed on SQLite.

  These reasons come from the code and replace the placeholder S4 reason the test writer used.
- **`results.py`:** the Limits section keeps its existing list of what wasn't tested and adds a subsection built from `equivalents.json`:
  - Each recorded entry is shown; an entry with no reason shows "reason not recorded".
  - An empty file says the run used no equivalents; a missing file says "No run evidence".
  - Nothing the run didn't record is shown.

**Still open:**
- Whether the live S1 and S4 steps actually write their entries can only be confirmed by the Actions run.
- If a future step substitutes something without recording it, RESULTS.md won't mention it.
- Earlier review requests not handled here because they belong to the spec owner or the factory:
  - The spec header still says "Status: draft".
  - The new chat-model pin isn't yet recorded as a numbered decision in `brain/decisions`.
  - There's no offline test that a model returning HTTP 410 or 404 at the preflight check is reported as its own kind of failure.
  - Stale artifacts from another work order are still in `.anvil-factory/runs/wo-gh-1`.

The station report is in `runs/wo-gh-1/builder.output.md`. Approval is up to the review station.
{"model": "claude-opus-5-5"}
