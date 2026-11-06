I added the missing guard to the S1 step. The one remaining failure in this work order's scope is a false positive in another station's file, and I haven't touched that file.

**The change:** in `src/auto_ontology_eval/live.py`, `stage_s1` now stops with a `StepFailed` error if the upstream checkout directory is inside the run evidence directory. The check runs before anything is cloned, before the Postgres password is generated, and before the Compose `.env` that carries the key is written. This covers the amended key rule in the spec, since anything under the run directory gets committed and uploaded. The error message doesn't include the key. The workflow already points the checkout under `RUNNER_TEMP`, so a normal run isn't affected. The change is 9 lines, and I didn't modify any tests.

**Test results:** the full suite has 200 tests, with 35 failures and 1 skip. The red test the test-writer left for me, `test_upstream_dir_inside_run_dir_fails_closed_before_writing_the_key`, now passes. The 35 failures are:
- **34 in `test_run_evidence_live.py`:** they need the `runs/eval-live/` evidence from a live-internals run (spec Amendment 3). Amendment 3 isn't part of wo-gh-1, so these were expected to stay red.
- **1 false positive in `test_no_key_assignment_in_any_committed_run_artifact`:** it flags `runs/wo-gh-1/test-writer.output.md` line 10. That line only describes the rule: "a real `NVIDIA_API_KEY=` value". The test's pattern treats the closing backtick after `=` as a key value. No key is in the file.

**Decision for you:** that last failure needs either the test-writer to allow a backtick in the pattern, or that output file to be reworded. Both belong to another station, so I left them alone.

The S1–S3 harness, fixture and scoring were already in the repo and their tests pass, so no other code change was needed. I haven't committed anything.
{"model": "claude-opus-5-5"}
