# RESULTS: NVIDIA Auto Ontology enterprise evaluation

Internal evidence artifact, written by the harness from run artifacts only. Not for publication.

**Run stopped** at step `preflight`: StepFailed: hosted model preflight failed: nvidia/nemotron-3-nano-30b-a3b HTTP 410: {"type":"about:blank","title":"Gone","status":410,"detail":"The model 'nvidia/nemotron-3-nano-30b-a3b' has reached its end of life on 2026-09-01T09:00:00Z and is no longer available."}


Sections after the failed step have no run evidence; nothing below is estimated.

## Environment

- Runner: `ubuntu24 20261026.354.1 (GitHub Actions, GitHub Actions 1000013115, Linux)`
- GitHub run id: `41971180197`
- Upstream repository: `https://github.com/NVIDIA/auto-ontology.git`
- Upstream commit: `cdaf61e1bd0cf3820d11d72b43bb460816aebbd3`
- Chat model: `nvidia/nemotron-3-nano-30b-a3b`
- Embedding model: `nvidia/nemotron-3-embed-1b`
- Rerank model: `nvidia/llama-nemotron-rerank-vl-1b-v2`
- Run date: `2026-11-05T05:13:39Z`

### Stack smoke (S1)

No run evidence: the run did not produce `smoke/smoke.json`.

## Time to first ontology

No run evidence: the run did not produce `timing.json`.

## Reconciliation checklist

No run evidence: the run did not produce `reconciliation.json`.

## Per-question results

No run evidence: the run did not produce `ablation.json`.

## Failure gallery

No run evidence: the run did not produce `ablation.json`.

## Limits

This is what the fixture did not exercise. No claim here goes beyond it.

- All data is synthetic: 8 small tables (dozens of rows) across one Postgres and one DuckDB source, built from fixed seed files. Results say nothing about scale, data volume or real enterprise schemas.
- The fixture plants four conflicts only (net_sales semantics, location identity, product hierarchy, shared SKU identity). Other conflict kinds (units of measure, currencies, time zones, slowly changing dimensions, fiscal calendars) were not exercised.
- 12 questions, each answered once per arm with one fixed chat model and fixed generation settings. Run-to-run variance, other models and prompt variants were not tested.
- Only the default hosted NIM configuration was used; self-hosted NIMs, other connectors and the web UI workflows were not exercised.
- The MCP surface was probed (tools listing) but agents using the MCP tools end to end were not tested.
- Security, access control, multi-user behaviour, cost and latency beyond the measured time to first ontology were not covered.
