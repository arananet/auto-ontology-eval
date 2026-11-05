I've built the harness, the fixture and the eval workflow, and all 89 scenario tests pass. But the evaluation itself still can't run, and there is no real RESULTS.md: the spec's chat model has been retired. Only the short model check at the start ran for real. S1, S3 and S4 have never run against the actual stack.

**The blocker:** a real run today returned HTTP 410 for `nvidia/nemotron-3-nano-30b-a3b`, which reached end of life on 2026-09-01. The embedding and rerank models answer normally (HTTP 200). The spec forbids switching models, so the run stops at that first check. It exits non-zero and writes a RESULTS.md that says "Run stopped" and gives the reason, with "No run evidence" in every later section. The key appeared in none of the output files, and a run with the key unset stops at the `secrets` step. That run's output is in `runs/wo-gh-1/evidence/preflight-run/`.

**Decision needed (spec owner):** pin a replacement chat model in the spec. After that, change it in `src/auto_ontology_eval/config.py` and `tests/_support.py` and re-run.

**What's built:**
- **Fixture (S2):** `fixture/` holds 8 tables. Source A is a Postgres sales mart, Source B a DuckDB ops mart.
  - Every B shipment mirrors an A sale, so B's `net_sales` total (1598.25) minus A's (1549.75) is exactly the returns total (48.50).
  - B's plant and DC codes link to A's location names only through a shared city column.
  - A groups products by brand then category; B has one `product_group` and no brand.
  - Six SKUs are shared between the sources.
  - It includes the conflict checklist and 12 questions whose answers come from reference SQL. `GROUND_TRUTH.md` explains how to recompute each one by hand, and `fixture/generate.py` rebuilds the files byte for byte.
- **Harness:** `src/auto_ontology_eval/`, with one module per test contract.
  - The run stops at the first step that fails or leaves no evidence file.
  - A reconciliation mark counts only if its quote appears word for word in the exported catalog.
  - RESULTS.md is built only from run files.
  - `live.py` drives the real stack in this order: model check, fixture, S1, S3, S4.
- **Workflow:** `.github/workflows/auto-ontology-eval.yml` is started manually and runs on ubuntu. It takes the key only from the secret and uploads the evidence as a workflow artifact, so nothing is published. The operator notes say the job token can't push workflow files, so the operator may have to push this one.

**Choices for reviewers to check:**
- **Matched settings:** both S4 arms use temperature 0.0 and max_tokens 8192 with no seed. That is what the pinned upstream chat client uses (`auto_ontology/utils/llm_invoke.py:258-262`), so the match is real.
- **Registering the sources:** both sources go through upstream's `CONNECTION_STRINGS` setting, because the pinned version can't register DuckDB through its API. A small compose override mounts the DuckDB file into the containers.
- **Starting ontology generation:** the harness turns generation on by writing the settings row itself instead of using the web UI, then triggers it through the API. Time to first ontology runs from both sources appearing in the stack to the first complete catalog export.
- **MCP probe:** the pinned MCP server needs an OAuth token, so S1 lists its tools in process, the same way upstream's own tests do.
- **Raw-schema arm:** the model's SQL is run on a SQLite copy loaded from the same seed files, not on the live Postgres and DuckDB.
- **Provenance:** an Auto Ontology answer counts as having provenance if its result contains a `provenance`, `lineage`, `citation(s)`, `sources` or `custom_analyses_used` field.
- **DuckDB version:** pinned to 1.5.5 in the workflow to match upstream's lock file, so its containers can read the file.

**Not done:**
- The S1, S3 and S4 code has never run against a real stack, so expect fixes on the first full run.
- Nothing is committed, and the spec header still says `Status: draft`.
- This change produces nothing visual, so the Quality Charter comparison doesn't apply.

Approval belongs to a different station.
{"model": "claude-opus-5-5"}
