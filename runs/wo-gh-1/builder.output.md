The committed run (`runs/eval/`, Actions run 42127124473) can't be used as evidence for S3 or S4. Auto Ontology ran on the end-of-life chat model, not the pinned one. I fixed the cause in the harness, but the evaluation has to run again in GitHub Actions before RESULTS.md means anything. I couldn't run it from here.

**What went wrong.** Every Auto Ontology answer (0 of 12) was "LLM failed to produce a response". The run's compose logs show why: the upstream container's own model calls got `[410] Gone`, which is what the hosted endpoint returns for the retired `nvidia/nemotron-3-nano-30b-a3b`.
- When the harness wrote the upstream `.env`, it removed every `*_MODEL` line so the upstream defaults would apply.
- At the pinned commit, the default chat model for an `nvapi-` key is that retired model.
- So the raw-schema arm used the pinned `nvidia/nemotron-3.5-lightning-30b-a3b`, while the Auto Ontology arm used the retired model. That breaks the spec rule that both arms use the same model.
- `ablation.json` and RESULTS.md still list the pinned model for both arms, because they record what was configured, not what the stack actually called.
- S3 ontology generation used the same `.env`, which probably explains why all four conflicts came out "ignored". I can't confirm it: the committed logs only show the 410 errors from the S4 questions onward.

I reproduced the bug with the pinned upstream's own model lookup: with no pins set it picks the retired model, and with the fix it picks the pinned one.

**What changed (not committed):**
- **`src/auto_ontology_eval/live.py`:** the upstream `.env` now sets all four model variables (`REASONING_MODEL`, `NON_REASONING_MODEL`, `EMBED_MODEL`, `RERANK_MODEL`) to the spec pins.
- **New check in S1:** once the stack is healthy, the harness asks the running container which models it will use and saves the answer to `smoke/models.json`. If any differs from the pins, the run stops before producing scenario evidence. The helpers are in `src/auto_ontology_eval/upstream.py`.
- **`tests/test_s1_model_pins.py`:** five new offline tests for this, with a row in `tests/SCENARIOS.md`. Writing tests is normally the test writer's job, so reviewers may choose not to keep them.

All tests pass: 138 passed, 1 skipped (the skipped one needs DuckDB, which isn't installed here). I left the committed evidence untouched, because RESULTS.md may only come from run artifacts. My report for the review stations is in `runs/wo-gh-1/builder.output.md`.

**Still to do:**
- Rerun the evaluation in GitHub Actions with the `NVIDIA_API_KEY` secret, so the new `runs/eval/` and RESULTS.md replace the current ones.
- `tests/test_run_evidence.py` passes on the bad run, because it checks the configured model rather than the one actually used. After the rerun it could also check `smoke/models.json`; that's for the test writer to decide.
- The spec header still says "Status: draft", which is for the spec owner to fix.

Approval belongs to the review stations.
{"model": "claude-opus-5-5"}
