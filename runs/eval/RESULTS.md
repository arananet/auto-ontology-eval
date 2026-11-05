# RESULTS: NVIDIA Auto Ontology enterprise evaluation

Internal evidence artifact, written by the harness from run artifacts only. Not for publication.

**Run stopped** at step `preflight`: StepFailed: hosted model preflight failed: nvidia/nemotron-nano-3-30b-a3b HTTP 404: {"status":404,"title":"Not Found","detail":"Function '2b2dcd47-c858-425a-9c04-4cacf2eac993': Not found for account 'Nyo8YJeegLDUWvrHQKwJHRnKZkN5K-7P-1Hhs1RiROs'"}

Sections after the failed step have no run evidence; nothing below is estimated.

## Environment

- Runner: `ubuntu24 20261101.360.1 (GitHub Actions, GitHub Actions 1000013128, Linux)`
- GitHub run id: `42090168798`
- Upstream repository: `https://github.com/NVIDIA/auto-ontology.git`
- Upstream commit: `cdaf61e1bd0cf3820d11d72b43bb460816aebbd3`
- Chat model: `nvidia/nemotron-nano-3-30b-a3b`
- Embedding model: `nvidia/nemotron-3-embed-1b`
- Rerank model: `nvidia/llama-nemotron-rerank-vl-1b-v2`
- Run date: `2026-11-05T19:03:27Z`

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
