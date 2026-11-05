# Test map: auto-ontology-enterprise-eval

Spec: `.openspec/specs/auto-ontology-enterprise-eval/spec.md`. These tests were written before the implementation existed. They define the harness contract the builder has to meet.

Run from the project root with the standard library only:

    python -m unittest discover -s tests -t .

| Spec item | Test file | What is checked offline |
|---|---|---|
| Requirements: pin, model ids, secret only as `NVIDIA_API_KEY`, never in code, logs or RESULTS.md | `test_requirements_config_secrets.py` | `config` constants, `secrets.require_api_key` fails closed, `secrets.redact`, `environment.collect`, and a scan for real key literals |
| S1 stand up and smoke | `test_s1_upstream_smoke.py` | clone and exact-commit checkout argv, HEAD verification, upstream compose file used first, three smoke evidence files, fail closed on any failed check |
| S1/S3/S4: the upstream stack runs on the spec model pins (added by the builder, regression for run 42127124473) | `test_s1_model_pins.py` | the generated upstream `.env` sets REASONING, NON_REASONING, EMBED and RERANK models to the pins and never contains the end-of-life default; the in-container resolver check passes only when every pin matches and fails closed on a fallback or unreadable output |
| S2 fixture | `test_s2_fixture.py` | layout, 8 to 10 tables, a seed CSV and DDL per table, the four conflicts recomputed from the CSVs, 12 questions whose `expected` matches the reference SQL, GROUND_TRUTH.md lists them, determinism, the raw schema leaks no semantics |
| S3 reconciliation | `test_s3_reconciliation.py` | exactly one mark per conflict, only verbatim quotes count, deterministic classifier, time to first ontology, fail closed on missing events |
| S4 ablation | `test_s4_ablation.py` | 2-decimal and order-free scoring, per-arm correctness and delta, verbatim SQL, provenance flag, ground truth written before any model call, same model and settings enforced and recorded |
| S5 RESULTS.md, plus the fail-closed requirement | `test_s5_results_and_fail_closed.py` | sections in order, every value comes from an artifact, failure gallery has the wrong SQL verbatim, limits section, "No run evidence" for missing sections, failed step recorded, no key, pipeline stops at the first failed step |
| S5 amended: the limits section names every equivalent the run used, and why (MCP tools listed in process, raw-schema arm SQL run on a copy of the fixture) | `test_s5_limits_equivalents.py` | steps record each equivalent in `equivalents.json` (`scenario`, `literal`, `equivalent`, `reason`); every recorded entry appears in `## Limits` with its reason; entries the run did not record are never named; a missing reason is flagged; a missing artifact says "No run evidence"; an empty list says no equivalents; the key is redacted |
| Committed executed run (`runs/eval/`) against S1 to S5 and the Requirements | `test_run_evidence.py` | The environment records the pinned commit and models plus a GitHub Actions run id. Both arms used the pinned model, and the generation settings are recorded. All five steps passed and each has an evidence file. The three S1 smoke checks passed and their evidence files are not empty. S3: one valid mark per checklist conflict; `counted` is true only for a verbatim catalog quote; rescoring and reclassifying the committed catalog reproduces `reconciliation.json`. Time to first ontology recomputes from `events.json`. S4: 12 questions match the fixture, and every conflict is touched. The ground truth recomputes from reference SQL. `correct` flags, totals and delta recompute. Each ontology answer has a provenance flag. Raw-arm SQL is verbatim from the saved model response. A no-answer keeps the upstream reason. RESULTS.md sections, values, table, gallery and limits all match the artifacts. Both known equivalents were recorded by the run itself. No key anywhere under `runs/`. Fails, not skips, if `runs/eval/` is missing |
| Requirements: Actions runner, nothing published | `test_workflow.py` | `.github/workflows/auto-ontology-eval.yml` runs on ubuntu, takes the key from the secret only, never echoes it, has no publish steps |

## Not testable offline

These need the executed GitHub Actions run, so they are evidence for the reviewers, not unit tests:

- The live stack coming up.
- Real NIM calls.
- Postgres registration of Source A.
- The real catalog export.
- RESULTS.md and the run artifacts being committed by the line.
- Re-running the live stack. `test_run_evidence.py` checks the evidence one executed run committed (run 42127124473). It cannot show a fresh run would reproduce it.

## Skipped test

`test_s2_fixture.DeterminismTests.test_build_duckdb_is_deterministic_and_holds_source_b` skips when the `duckdb` Python package is not installed, because the suite runs on the standard library only. It runs wherever `duckdb` is installed, for example `pip install duckdb`.
