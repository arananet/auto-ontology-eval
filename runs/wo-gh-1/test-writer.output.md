I added one test file, `tests/test_requirements_key_outside_evidence.py`, with 12 tests. 11 pass and 1 fails on purpose: it needs a guard the builder still has to add. Nothing is committed.

**Why only this:** the project repo already has the harness and 188 tests for S1–S3. The spec writer changed one thing that applies to this work order: the `NVIDIA_API_KEY` rule now also covers uploaded workflow artifacts. It also says any file that carries the key, such as the Compose `.env`, must be written outside the run evidence directory. Nothing tested that part, so the new tests cover it.

**What the tests check:**
- **Where S1 writes the key file:** I ran `stage_s1` with Docker and git calls faked. It writes the `.env` holding the key into the upstream checkout, readable by the owner only. Afterwards the run directory has no `.env` and no key.
- **The red test:** if `--upstream-dir` points inside the run directory, S1 must stop with a failure before it writes the `.env`. Today it doesn't, so the key file would be uploaded with the evidence. The builder's fix is to make S1 refuse that setting up front.
- **Log redaction:** the helper that captures command output and error messages removes the key.
- **Workflow:** the artifact upload covers only the run directory, and the upstream checkout lives under `RUNNER_TEMP`, outside it.
- **Committed evidence:** `.env` is git-ignored, and nothing under `runs/` is a `.env` file or contains a real `NVIDIA_API_KEY=` value. Redacted and empty values are allowed.

**Checks I ran:**
- As a deliberate fault, I made S1 also write the `.env` into the run directory. The location tests caught it, and I restored the source unchanged.
- I checked that the key-value pattern flags a real value but not the workflow's secret reference or a redacted value.

**Full suite:** 200 tests, 35 failures, 1 skip. 34 of the failures were already there: they check evidence from the live-internals run, which hasn't been committed and is outside this work order. The 35th is the red test above.

I also added a row for the new file to `tests/SCENARIOS.md`.

**Inputs:** S1–S3 had everything I needed. The work order still names the chat model `nvidia/nemotron-3-nano-30b-a3b`, but the spec's Amendment 2 replaces it with `nvidia/nemotron-3.5-lightning-30b-a3b`. The tests follow the amendment. Approving this belongs to another station.
{"model": "claude-opus-5-5"}
