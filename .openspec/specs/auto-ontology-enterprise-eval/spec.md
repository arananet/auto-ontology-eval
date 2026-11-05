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
- S3: Given the S2 fixture connected as two sources, when the harness runs ontology generation with the default hosted NIM model configuration (chat model nvidia/nemotron-nano-3-30b-a3b, embedding model nvidia/nemotron-3-embed-1b, reranking model nvidia/llama-nemotron-rerank-vl-1b-v2, key supplied only as the NVIDIA_API_KEY repository secret), then the generated catalog is exported to a file and scored against the planted-conflict checklist from the fixture. Every planted conflict is marked exactly one of detected, reconciled or ignored, and each mark carries a verbatim quote from the generated catalog as evidence. A mark without a quote does not count. The harness records time to first ontology: the wall-clock time from both sources being registered with the running stack to the first complete catalog export, measured from run timestamps.

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
