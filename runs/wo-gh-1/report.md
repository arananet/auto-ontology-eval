# Run Report

Work Order: wo-gh-1
Title: Evaluate NVIDIA Auto Ontology as an enterprise semantic layer (executed ablation test)
Kind: feature
Status: new

## Intake Outcome

Outcome: rescoped

This work order was rescoped at intake.

### Rescoped Description

```
Implement spec auto-ontology-enterprise-eval (S1–S3 only) in the factory: (S1) stand up NVIDIA/auto-ontology at pinned commit cdaf61e1bd0cf3820d11d72b43bb460816aebbd3 via its own Docker Compose on a Docker-capable GitHub Actions runner and record smoke evidence (API health check, one catalog page or API response, an MCP tools/list or equivalent probe); (S2) build the deterministic two-source fixture with planted conflicts (Source A Postgres sales mart where net_sales excludes returns and hierarchy is brand then category; Source B DuckDB ops mart where net_sales is gross including returns and locations use plant/DC codes differing from Source A names; shared SKUs; 8 to 10 tables total; fixed seeds; ground truths documented inside the fixture); (S3) run ontology generation against both sources with the default hosted NIM configuration (chat nvidia/nemotron-3-nano-30b-a3b, embeddings nvidia/nemotron-3-embed-1b, rerank nvidia/llama-nemotron-rerank-vl-1b-v2), with the API key supplied only as the NVIDIA_API_KEY repository secret (never written to logs, artifacts, or the repo), and score the generated ontology against the planted-conflict checklist, marking each conflict detected, reconciled, or ignored, each mark backed by a verbatim quote from the generated catalog. No real company data is used and nothing is published.
```

### Rescope Reasons

- Cut S4 \(12\-question ablation of Auto Ontology chat API vs raw\-schema LLM with reference\-SQL ground truths\): it depends on S3's generated ontology and is a separate buildable change with its own scoring harness\.
- Cut S5 \(RESULTS\.md\): it must be produced solely from the executed run of S1–S4, so it cannot be built until S4 has executed; it should follow as its own work order\.
- The original bundles five scenarios \(deploy, fixture, generation and scoring, ablation, report\) into one work order; S1–S3 are cut down to one coherent buildable scope: stand up, fixture, and scored generation\.

Risk: high

Surfaces: deploy, security, data, api

## Routing

**Decision**: High risk: full panel at policy models, no reduction applied; Security surface: reviewer-security at strong model

**Selected reviewers** (5):
- reviewer-spec (model: review-balanced)
- reviewer-security (model: review-strong)
- reviewer-tests (model: review-balanced)
- reviewer-architecture (model: review-balanced)
- reviewer-design (model: review-balanced)

**Routed out** (1):
- reviewer-ux: Routed out: no UI surface

## Verdict

Verdict: changes_requested

Reviewers reviewer-spec, reviewer-design requested changes. (Counted 3 reviews, expected 5.)

## Steps

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
- observer: executed

