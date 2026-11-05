# Test map: auto-ontology-enterprise-eval

Spec: `.openspec/specs/auto-ontology-enterprise-eval/spec.md`. These tests were written before the implementation existed. They define the harness contract the builder has to meet.

Run from the project root with the standard library only:

    python -m unittest discover -s tests -t .

| Spec item | Test file | What is checked offline |
|---|---|---|
| Requirements: pin, model ids, secret only as `NVIDIA_API_KEY`, never in code, logs or RESULTS.md | `test_requirements_config_secrets.py` | `config` constants, `secrets.require_api_key` fails closed, `secrets.redact`, `environment.collect`, and a scan for real key literals |
| S1 stand up and smoke | `test_s1_upstream_smoke.py` | clone and exact-commit checkout argv, HEAD verification, upstream compose file used first, three smoke evidence files, fail closed on any failed check |
| S2 fixture | `test_s2_fixture.py` | layout, 8 to 10 tables, a seed CSV and DDL per table, the four conflicts recomputed from the CSVs, 12 questions whose `expected` matches the reference SQL, GROUND_TRUTH.md lists them, determinism, the raw schema leaks no semantics |
| S3 reconciliation | `test_s3_reconciliation.py` | exactly one mark per conflict, only verbatim quotes count, deterministic classifier, time to first ontology, fail closed on missing events |
| S4 ablation | `test_s4_ablation.py` | 2-decimal and order-free scoring, per-arm correctness and delta, verbatim SQL, provenance flag, ground truth written before any model call, same model and settings enforced and recorded |
| S5 RESULTS.md, plus the fail-closed requirement | `test_s5_results_and_fail_closed.py` | sections in order, every value comes from an artifact, failure gallery has the wrong SQL verbatim, limits section, "No run evidence" for missing sections, failed step recorded, no key, pipeline stops at the first failed step |
| Requirements: Actions runner, nothing published | `test_workflow.py` | `.github/workflows/auto-ontology-eval.yml` runs on ubuntu, takes the key from the secret only, never echoes it, has no publish steps |

## Not testable offline

These need the executed GitHub Actions run, so they are evidence for the reviewers, not unit tests:

- The live stack coming up.
- Real NIM calls.
- Postgres registration of Source A.
- The real catalog export.
- RESULTS.md and the run artifacts being committed by the line.
