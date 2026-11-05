The harness, the fixture and an eval workflow are all in the project repo, and all 92 scenario tests pass with duckdb installed. But the live evaluation can't produce results yet: the spec's chat model has been retired on NVIDIA's hosted endpoint. So there is no RESULTS.md in the repo, and none of S1 to S5 has run against the real stack.

**The blocker:** on 2026-11-05 the hosted NIM endpoint answered a chat call to `nvidia/nemotron-3-nano-30b-a3b` with `HTTP 410 Gone`. The message said the model "reached its end of life on 2026-09-01". The same key works for the embedding model and the rerank model (both HTTP 200). This chat model is the upstream default for ontology generation and chat, and the spec forbids switching models. So S3 and both S4 arms can't run until the spec owner pins a replacement. The hosted catalog currently lists possible successors, including `nvidia/nemotron-3.5-lightning-30b-a3b` and `nvidia/nemotron-nano-3-30b-a3b`. After that decision, the model id changes in `config.CHAT_MODEL` and `tests/_support.CHAT_MODEL`. The full note is in `runs/wo-gh-1/builder-preflight.md`.

I added a preflight check before S1 so the run stops in seconds instead of after a long stack build. I ran the real command into `/tmp`: it stopped at preflight with the 410 error, wrote a RESULTS.md marked "Run stopped early" with "No run evidence" in the empty sections, and the key appeared in none of the output files.

**What's built:**
- **Code:** `src/auto_ontology_eval/`, one module per contract in the tests, plus `live.py`, which drives the real stack.
- **S2 fixture:** in `fixture/`. Source A is a Postgres sales mart and Source B is a DuckDB ops mart, 8 tables in total.
  - Each ops-mart shipment mirrors a sales-mart sale, so the two `net_sales` totals differ by exactly the returns (580.00).
  - Locations are names in A and plant/DC codes in B; the only link between them is a shared `city` column.
  - The 12 expected answers were computed from reference SQL before any model call, and they match the hand derivations in `GROUND_TRUTH.md`.
- **Workflow:** `.github/workflows/auto-ontology-eval.yml`, run manually on ubuntu. It takes the key only from the secret and uploads the evidence as a workflow artifact; nothing is published.

**Choices reviewers should check:**
- **DuckDB connection:** the pinned upstream version can only connect DuckDB through its `CONNECTION_STRINGS` setting. Both sources are configured there, and a small compose override mounts the DuckDB file.
- **Ontology generation switch:** generation stays off until a web-UI setting row exists. The harness writes that same row itself instead of building the frontend, and RESULTS.md records this.
- **MCP probe:** the pinned MCP server requires a frontend OAuth token for every request, including `tools/list`. The harness lists tools in-process (the closest equivalent the spec allows) and records the unauthenticated HTTP probe's response as evidence of the auth requirement.
- **Reconciliation marks:** these come from fixed pattern rules in `conflicts.json`, written before any run. Every quote is checked word for word against the exported catalog. A test against a made-up catalog caught a false positive in the `net_sales` rule, which I tightened.

**Not done:**
- **Live run:** I did not attempt the full run here. This station has a 25-minute limit and only about 15 minutes were left. I also chose not to leave a run going in the background with the secret.
- **Spec status:** the spec header still says `Status: draft`.
- **Commits:** nothing is committed.
{"model": "claude-opus-5-5"}
