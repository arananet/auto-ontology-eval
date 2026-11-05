I added tests for the S5 change in the spec. They fail for now, which is expected until the builder implements it. The change now says the Limits section of RESULTS.md must name every place the run used an equivalent instead of the literal step, and say why.

The tests and harness from the earlier pass were already in the repo and passed. None of them covered this change.

**Test run:** 97 tests. 89 pass, 1 is skipped because it needs DuckDB, which isn't installed here, and 7 fail, all in the new file. One new test, the key-redaction check, passes today only because nothing is printed in that spot yet.

**What the new tests require** (`tests/test_s5_limits_equivalents.py`):
- **Recording:** a step that uses an equivalent writes an entry to a new run file, `equivalents.json`, with what the spec asked for, what the run did instead, and why.
- **Both known cases:** the Limits section shows the two cases the spec names, each with its reason:
  - S1: MCP tools were listed in process, because the pinned server needs an OAuth token.
  - S4: the raw-schema arm's SQL ran on a copy of the fixture.
- **Recorded entries only:** every recorded entry appears, and nothing the run didn't record is named.
- **Incomplete or missing records:**
  - An entry with no reason is marked "reason not recorded".
  - If the file is missing, the section says "No run evidence".
  - If the file is an empty list, it says there were no equivalents.
  - The API key is removed if it appears in an entry.

I also added the new scenario to the test map in `tests/SCENARIOS.md`, and wrote my station report to `runs/wo-gh-1/test-writer.output.md`. Nothing is committed.

**For a reviewer to confirm:**
- **New file and its fields:** the spec doesn't name a file for this. I chose `equivalents.json` so the Limits text comes from the run rather than being hard-coded.
- **No automatic fallback:** if a live step uses an equivalent but doesn't record it, RESULTS.md won't mention it.
- **Not checkable offline:** whether the live S1 and S4 steps actually write their entries depends on Docker and the NVIDIA endpoints, so only the GitHub Actions run can show it.
- **Placeholder reason for S4:** the spec doesn't say why the raw-schema arm runs on a copy of the fixture, so the reason in the test is mine. The test only checks that whatever reason is recorded gets printed. The builder has to record the real one.
{"model": "claude-opus-5-5"}
