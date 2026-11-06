# Task packet: observer

## Station prompt

# Observer

## Role
Watch the released change and report what actually happened.

## Inputs
- release record

## Outputs
- observation report

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.


## Work order

- id: wo-gh-1
- kind: feature
- title: Evaluate NVIDIA Auto Ontology as an enterprise semantic layer (executed ablation test)
- source: github-issue
- description: Implement spec auto-ontology-enterprise-eval (S1–S3 only) in the factory: (S1) stand up NVIDIA/auto-ontology at pinned commit cdaf61e1bd0cf3820d11d72b43bb460816aebbd3 via its own Docker Compose on a Docker-capable GitHub Actions runner and record smoke evidence (API health check, one catalog page or API response, an MCP tools/list or equivalent probe); (S2) build the deterministic two-source fixture with planted conflicts (Source A Postgres sales mart where net_sales excludes returns and hierarchy is brand then category; Source B DuckDB ops mart where net_sales is gross including returns and locations use plant/DC codes differing from Source A names; shared SKUs; 8 to 10 tables total; fixed seeds; ground truths documented inside the fixture); (S3) run ontology generation against both sources with the default hosted NIM configuration (chat nvidia/nemotron-3-nano-30b-a3b, embeddings nvidia/nemotron-3-embed-1b, rerank nvidia/llama-nemotron-rerank-vl-1b-v2), with the API key supplied only as the NVIDIA_API_KEY repository secret (never written to logs, artifacts, or the repo), and score the generated ontology against the planted-conflict checklist, marking each conflict detected, reconciled, or ignored, each mark backed by a verbatim quote from the generated catalog. No real company data is used and nothing is published.
- risk_hints: secrets
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: not_configured
- reviewer-spec: executed
- reviewer-security: executed
- reviewer-tests: executed
- reviewer-architecture: executed
- reviewer-design: executed
- reviewer-ux: routed_out
- approver: completed
- approver: loopback
- triage-human: completed
- deployer: packet_ready
