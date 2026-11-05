I've written the tests for wo-gh-1: 92 tests in seven files under `tests/` in the project repo, plus `tests/README.md` mapping each file to its spec scenario. They all fail right now, because neither `src/auto_ontology_eval/` nor `fixture/` exists yet. Every file compiles. Nothing is committed.

Since there was no code to test against, the tests also define what the builder has to create: module names, function signatures and the fixture file layout. Each test file's docstring spells this out.

| Spec item | File | What it checks |
|---|---|---|
| Secret, pin and model requirements | `test_secrets_and_config.py` | The exact pinned commit and the three model ids. A missing, empty or whitespace `NVIDIA_API_KEY` stops the run, with no fallback to other variables. The key is redacted and never appears in committed files. An eval workflow on ubuntu reads `secrets.NVIDIA_API_KEY` and never echoes it. |
| Stop before S1 | `test_harness_fail_closed.py` | No stage runs without the key, and the run stops at the first stage that fails. |
| S1 | `test_s1_smoke.py` | The clone checks out the exact commit, and a short or different SHA is rejected. The MCP `tools/list` request and response are checked. Each of the three smoke checks fails closed. |
| S2 | `test_s2_fixture.py` | Two sources with 8 to 10 tables in total. The four required conflicts are checked against the CSV data: location names appear only in Source A, plant/DC codes only in Source B, and shared SKUs in both. 12 questions together cover every conflict. The ground-truth and normalization docs exist. The reference SQL reproduces the recorded answers. The Postgres load SQL and the DuckDB build are deterministic. |
| S3 | `test_s3_reconciliation.py` | Each conflict gets exactly one mark. Quotes must match the catalog exactly, including case and whitespace. A missing or non-matching quote turns the mark into `ignored`, with the failed check recorded. |
| S4 | `test_s4_ablation.py` | Rounding to two decimals; rows compared in any order unless the question asks for one. Both arms use the same model, endpoint and temperature. The raw-schema prompt contains no ontology or ground-truth text. Each question is asked once, with no retry. Errors and answers without SQL score as wrong. Provenance and the delta are recorded. |
| S5 | `test_s5_results.py` | RESULTS.md has all six sections, built only from run artifacts. Wrong SQL appears exactly as generated in the failure gallery. A missing artifact gives "No run evidence" and no made-up number. The key is redacted. |

Things the builder and reviewers should know:
- **Standard library only:** pytest and duckdb aren't installed here, so the tests use `unittest` and run with `python -m unittest discover -s tests -t .`.
- **Two checks can skip:** the DuckDB build and the reference-answer check skip when duckdb is missing. The eval workflow must install duckdb, or those checks silently skip in CI.
- **Choices I made that the spec doesn't:** the fixture file names (`fixture/source_a|source_b/*.csv`, `conflicts.json`, `questions.json`, `GROUND_TRUTH.md`, `NORMALIZATION.md`), the run artifact names, the reference SQL naming tables as `source_a.<table>` / `source_b.<table>`, and per-arm totals shown as `1/2`. The builder can propose changes to any of these.
- **Not unit-testable:** bringing up the real Docker stack, the hosted NIM calls and the measured time to first ontology only happen in GitHub Actions. Reviewers have to check those against the run artifacts.
- **Spec still says draft:** its header reads `Status: draft` even though the work order calls it approved. Approving it belongs to another station, not this one.
{"model": "claude-opus-5-5"}
