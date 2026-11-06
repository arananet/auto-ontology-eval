I added no new scenario tests: the spec now puts S1–S5 back in scope for wo-gh-1, and every scenario already has tests. I fixed the one test that was failing, and the full suite now passes (201 tests, 1 skipped).

**The fix:** the test that scans committed run files for an API key was flagging prose rather than a key. In `runs/wo-gh-1/builder.output.md`, the text "a real `NVIDIA_API_KEY=` value" got through because the pattern read the closing backtick as a key value. The builder had already reported this.
- In `tests/test_requirements_key_outside_evidence.py`, the pattern now ignores a lone closing quote or backtick, an empty quoted pair, and masked values.
- It still catches real values, whether bare, quoted or in backticks.
- A new test checks both directions so the pattern can't drift either way.

The one skip is the DuckDB determinism test, which runs only when the `duckdb` package is installed. I also updated the matching row in `tests/SCENARIOS.md` and wrote the station report to `runs/wo-gh-1/test-writer.output.md`. Nothing is committed.

**Decision needed from the product owner before the builder starts:** the spec leaves open whether wo-gh-1 should:
- **(a)** accept the existing default run (GitHub Actions run 42127124473, in `runs/eval/`) as its evidence. The current tests already cover that run.
- **(b)** run the default configuration again into a new folder. The spec doesn't name that folder, so I wrote no test for it.

Whichever is chosen, note that the eval workflow still saves to `runs/eval` by default. Running it with default settings would overwrite the evidence that Amendment 3 says must stay unchanged. If the owner picks (b), a test for the new folder can be added once its name is set.
{"model": "claude-opus-5-5"}
