# Auto Ontology Enterprise Evaluation

Status: draft
Slug: auto-ontology-enterprise-eval

## Roles
- implementer: builds the evaluation harness described here
- reviewer: checks the harness and its results against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
NVIDIA Auto Ontology claims it can build a semantic, graph-based reasoning layer over enterprise data: generate an ontology from the metadata of connected sources, reconcile conflicting definitions across systems, and expose the result to agents through MCP, a CLI and an API. This project tests those claims with an executed run, not with vendor material. The evaluation stands the upstream project up at a pinned commit, feeds it a small deterministic fixture with planted definition conflicts, measures how the generated ontology handles the conflicts, and runs an ablation that compares natural-language answers with and without the ontology layer. The only output is an evidence file, RESULTS.md, produced from the executed run. No real company data is used anywhere, and nothing is published from this work.

## Requirements
- Upstream is pinned to NVIDIA/auto-ontology commit cdaf61e1bd0cf3820d11d72b43bb460816aebbd3. The harness clones the official repository and checks out exactly that commit.
- The run executes on a Docker-capable runner (GitHub Actions), because the upstream stack is defined by its own Docker Compose file and needs a working Docker daemon.
- All evaluation data is synthetic. No real company data, no production system and no personal data is connected, copied or queried.
- The hosted NVIDIA NIM API key reaches the run only as the GitHub repository secret NVIDIA_API_KEY. It never appears in code, in committed files, in logs or in RESULTS.md.
- The fixture is deterministic: fixed seeds, fixed row sets, and ground truths that a human can recompute by hand from the fixture files.
- RESULTS.md is written from run artifacts only. Every number in it traces to a file the run produced. No claim in RESULTS.md may exceed what the fixture exercised.
- Nothing is published from this work order: no post, no article, no external announcement. RESULTS.md is an internal evidence artifact.
- The run fails closed. If the NVIDIA_API_KEY secret is absent or empty, or any scenario step cannot produce its evidence file, the run stops with a non-zero exit and RESULTS.md records the failed step; no later step substitutes estimates for missing evidence.
- Both ablation arms in S4 call the same chat model id with the same generation settings (temperature, max tokens, and any seed the API accepts). The harness records those settings in a run artifact.
- Done means: the run executed end to end in GitHub Actions, RESULTS.md and the run artifacts are committed by the line, and the reviews are counted per the line's normal rules.

## Scenarios

### Scenario: Stand up the upstream stack and prove it answers
- S1: Given the pinned upstream commit checked out on a Docker-capable GitHub Actions runner, when the harness starts the stack with the upstream project's own Docker Compose file, then the stack comes up and the harness records smoke evidence: a passing API health check, one catalog page or API response captured to a file, and an MCP server probe (a tools/list request, or the closest equivalent the pinned version exposes) with its response captured. The run fails closed if any of the three smoke checks fails.

### Scenario: A two-source fixture with planted conflicts
- S2: Given the evaluation needs definitions that disagree across systems, when the harness builds its fixture, then the fixture is deterministic and holds two sources with planted conflicts. Source A is a Postgres database, the sales mart: its net_sales excludes returns, and its product hierarchy is brand, then category. Source B is a DuckDB database, the ops mart: its net_sales is gross and includes returns, and its locations are identified by plant and distribution center codes that differ from the location names Source A uses for the same physical entities. The two sources share a set of SKUs. The fixture holds 8 to 10 tables across both sources, loads from fixed seed files, and documents its ground truths inside the fixture itself, so every expected answer in S4 can be recomputed by hand from the fixture files alone. The fixture includes a machine-readable planted-conflict checklist that lists at least these four conflicts, each with an id, the tables and columns involved, and the ground truth: (1) net_sales semantics, where A excludes returns and B includes them; (2) location identity, where B's plant and DC codes map to A's location names, and the mapping is recorded in the fixture; (3) product hierarchy, where A uses brand then category and B uses a different grouping or none; (4) shared SKU identity across both sources.

### Scenario: Generate the ontology and score the reconciliation
- S3: Given the S2 fixture connected as two sources, when the harness runs ontology generation with the default hosted NIM model configuration (chat model nvidia/nemotron-3.5-lightning-30b-a3b, embedding model nvidia/nemotron-3-embed-1b, reranking model nvidia/llama-nemotron-rerank-vl-1b-v2, key supplied only as the NVIDIA_API_KEY repository secret), then the generated catalog is exported to a file and scored against the planted-conflict checklist from the fixture. Every planted conflict is marked exactly one of detected, reconciled or ignored, and each mark carries a verbatim quote from the generated catalog as evidence. A mark without a quote does not count. The harness records time to first ontology: the wall-clock time from both sources being registered with the running stack to the first complete catalog export, measured from run timestamps.

### Scenario: Ablation, answers with and without the ontology
- S4: Given 12 natural-language questions whose ground-truth answers are computed by reference SQL over the fixture and recorded before any model runs, at least one question touching each planted conflict from S2, when each question is answered twice, once through the Auto Ontology chat API and once by the same chat model given only the raw schema of both sources, then the harness scores exact-answer correctness per question and per arm (an answer is correct only if it matches the reference result: numbers equal after rounding to 2 decimal places, sets of values equal regardless of order; anything else, including no answer, is incorrect), records the correctness delta between the arms, and records for every Auto Ontology answer whether it carries provenance or lineage information. The generated SQL from both arms is saved verbatim for the failure gallery in S5.

### Scenario: RESULTS.md from the executed run only
- S5: Given a completed run, when the harness writes RESULTS.md, then it contains only what the run produced: the environment (runner, upstream commit, model identifiers, run date), the measured time to first ontology, the planted-conflict checklist with its marks and quotes, the per-question correctness table for both arms with the delta, a failure gallery quoting the wrong SQL verbatim, and a limits section stating what the fixture did not exercise. The limits section also names every place where the run used an equivalent instead of the literal step in S1 to S4, and says why. Two known cases: the MCP probe in S1 listing tools in process rather than over the network (the pinned MCP server requires an OAuth token), and SQL from the raw-schema arm in S4 running on a copy of the fixture rather than on the live Postgres and DuckDB sources. If a section has no run evidence, the section says so instead of estimating.

## Amendments

### Amendment 1 (2026-11-05): chat model pin replaced

- Decided by: Eduardo Arana, spec owner, on 2026-11-05.
- Old pin: chat model `nvidia/nemotron-3-nano-30b-a3b`.
- New pin: chat model `nvidia/nemotron-nano-3-30b-a3b`.
- Reason: the old pin reached its end of life on the hosted NVIDIA endpoint on 2026-09-01. A direct call to the hosted chat completions endpoint during harness construction returned HTTP 410 Gone; the evidence is recorded in `runs/wo-gh-1/builder-preflight.md`. This spec forbids substituting a model without a spec owner amendment, and the harness fails closed, so S3 and S4 could not produce evidence until the pin was amended.
- Unchanged: the embedding model `nvidia/nemotron-3-embed-1b` pin, the reranking model `nvidia/llama-nemotron-rerank-vl-1b-v2` pin, the upstream commit pin, and every scenario. Both S4 arms use the new pin, as S4 requires the same chat model in both arms.
- Applied in the same change: `CHAT_MODEL` in `src/auto_ontology_eval/config.py` and `CHAT_MODEL` in `tests/_support.py` now carry the new pin, so spec and code agree.
- Work order text: the wo-gh-1 work order body still quotes the old pin `nvidia/nemotron-3-nano-30b-a3b`. This amendment governs; the harness uses the new pin.

### Amendment 2 (2026-11-05): chat model pin replaced after live probes of both remaining candidates

- Decided by: Eduardo Arana, spec owner, on 2026-11-05. His instruction: probe both remaining candidates live and pin the one that answers.
- Old pin: chat model `nvidia/nemotron-nano-3-30b-a3b` (set by Amendment 1).
- New pin: chat model `nvidia/nemotron-3.5-lightning-30b-a3b`.
- Reason: the Amendment 1 pin is listed in the hosted catalog but does not answer on the hosted endpoint for this account. The harness live preflight returned HTTP 404, function not found for account, proven twice (GitHub Actions runs 42089981909 and 42090168798); the evidence is recorded in `runs/eval/preflight.json`. Catalog presence is not endpoint availability, so the owner ordered live probes of both remaining candidates before this amendment.
- Probe method: each probe executed the harness's own preflight stage (`stage_preflight` in `src/auto_ontology_eval/live.py`) in GitHub Actions through the `auto-ontology-probe` workflow (registered on the default branch for dispatch only), with `config.CHAT_MODEL` set to the candidate and the spec pin unchanged. A probe is not an evaluation run and produced no RESULTS.md.
- Probe results: `nvidia/nemotron-3.5-lightning-30b-a3b` answered, chat HTTP 200 with embedding and rerank also HTTP 200 (Actions run 42125151787; evidence in `runs/probes/nvidia-nemotron-3-5-lightning-30b-a3b/preflight.json`). `nvidia/nemotron-3-super-120b-a12b` did not answer, chat HTTP 404, function not found for account, with embedding and rerank HTTP 200 in the same probe (Actions run 42126620573; evidence in `runs/probes/nvidia-nemotron-3-super-120b-a12b/preflight.json`).
- Rule applied: exactly one candidate answered, so the responder is pinned. The owner's rule also settled the both answer case in advance: pin the lightning model, because it keeps the 30B class of the original pin and the 120B model would change the scale of the experiment. That case did not arise.
- Unchanged: the embedding model `nvidia/nemotron-3-embed-1b` pin, the reranking model `nvidia/llama-nemotron-rerank-vl-1b-v2` pin, the upstream commit pin, and every scenario. Both S4 arms use the new pin, as S4 requires the same chat model in both arms.
- Applied in the same change: `CHAT_MODEL` in `src/auto_ontology_eval/config.py` and `CHAT_MODEL` in `tests/_support.py` now carry the new pin, so spec and code agree.

### Amendment 3 (2026-11-05): second configuration, live internal models

- Decided by: Eduardo Arana, spec owner, on 2026-11-05, after the default configuration evaluation was published as a LinkedIn article that states plainly the live internal model configuration was not run. His stated reason for ordering this run: he does not want to talk beyond his evidence.
- This amendment adds a second configuration of the same evaluation, named `live-internals`. It changes one thing and nothing else: the Auto Ontology stack is launched with every internal chat model slot of the pinned upstream set to the pinned chat model `nvidia/nemotron-3.5-lightning-30b-a3b`.
- The complete internal chat model slot list, verified against the pinned upstream's own configuration surface at commit cdaf61e1 (`.env.example` and `auto_ontology/utils/model_config.py`): `DEFAULT_MODELS_MODEL`, `REASONING_MODEL`, `NON_REASONING_MODEL`. Every internal LLM consumer in the pinned upstream (the chat graph, question extraction, SQL generation, and the ingestion and semantic compilation steps such as key inference, column descriptions and table terms) builds its client through `auto_ontology/utils/llm_invoke.py`, which resolves the `REASONING` and `NON_REASONING` triplets; each triplet field falls back to the matching `DEFAULT_MODELS_` value when unset, and to a built in default when that is unset too. Wiring all three slots therefore wires every internal role. The `EMBED_MODEL` and `RERANK_MODEL` pins are unchanged: they are not chat roles and both already answer on the hosted endpoint.
- Identical to the default configuration: the upstream commit pin, the fixture and its seeds, the four planted conflicts, the reconciliation checklist and its scorer, the 12 questions and their ground truths, the stage structure, and the fail closed rule. In S1, the resolved models verification covers every wired slot in this configuration and fails closed on any mismatch, exactly as it covers the four default slots.
- The raw schema control arm is not rerun. Its result from the default configuration run (GitHub Actions run 42127124473: 8 of 12 correct, same chat model, temperature 0.0, max tokens 8192) stands as the control, and the live results document cites it with that provenance.
- Evidence for this configuration goes to `runs/eval-live/`, and its results document is `runs/eval-live/RESULTS-LIVE.md`, written from the live run's artifacts only, plus the control figures and the default configuration figures it cites from the `runs/eval/` artifacts of run 42127124473. The default configuration's `runs/eval/RESULTS.md` and its evidence are frozen: this configuration never modifies them and never reruns the default configuration.
- The live results document additionally reports catalog description coverage for the live catalog and, computed by the same counting rule, for the frozen default catalog: the number of `description:` fields in the exported catalog, split into authored (a real definition), blank (an empty value), and template (the upstream's own templated lines, of the form "Business entity represented by table ..." or a `format: ...` note). This is the counting rule the S4 diagnosis used on the default catalog (88 fields, 77 blank, 11 template, 0 authored).
- Applied in the same change: the harness takes a `--configuration` flag (`default` or `live-internals`); `model_env` in `src/auto_ontology_eval/upstream.py` returns the wired slot map for the selected configuration; in this configuration S4 runs the Auto Ontology arm only; the results writer for this configuration is `write_live_results` in `src/auto_ontology_eval/results.py`; and the eval workflow takes `configuration` and `run_dir` dispatch inputs whose defaults reproduce the default configuration run exactly.
