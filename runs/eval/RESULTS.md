# RESULTS: NVIDIA Auto Ontology enterprise evaluation

Internal evidence artifact, written by the harness from run artifacts only. Not for publication.

## Environment

- Runner: `ubuntu24 20261101.360.1 (GitHub Actions, GitHub Actions 1000013134, Linux)`
- GitHub run id: `42127124473`
- Upstream repository: `https://github.com/NVIDIA/auto-ontology.git`
- Upstream commit: `cdaf61e1bd0cf3820d11d72b43bb460816aebbd3`
- Chat model: `nvidia/nemotron-3.5-lightning-30b-a3b`
- Embedding model: `nvidia/nemotron-3-embed-1b`
- Rerank model: `nvidia/llama-nemotron-rerank-vl-1b-v2`
- Run date: `2026-11-05T23:07:28Z`

### Stack smoke (S1)

- health: pass (evidence `smoke/health.txt`)
- catalog: pass (evidence `smoke/catalog.txt`)
- mcp: pass (evidence `smoke/mcp.txt`)

## Time to first ontology

- 15.42 s from both sources registered to the first complete catalog export.
- start: `2026-11-05T23:12:22.548955Z`
- end: `2026-11-05T23:12:37.967486Z`

## Reconciliation checklist

4 planted conflicts; 4 marks backed by a verbatim catalog quote. A mark without a verbatim quote does not count.

### net_sales_semantics: ignored (counted: yes)

Quote from the exported catalog:

```text
name: fact_sales
```

### location_identity: ignored (counted: yes)

Quote from the exported catalog:

```text
name: dim_location
```

### product_hierarchy: ignored (counted: yes)

Quote from the exported catalog:

```text
name: dim_product
```

### shared_sku_identity: ignored (counted: yes)

Quote from the exported catalog:

```text
name: dim_product
```

## Per-question results

Both arms: model `nvidia/nemotron-3.5-lightning-30b-a3b`, settings `{"max_tokens": 8192, "temperature": 0.0}`.

| id | expected | Auto Ontology answer | correct | provenance | raw-schema answer | correct |
|---|---|---|---|---|---|---|
| Q01 | 1549.75 | (no answer) | no | no | 1549.75 | yes |
| Q02 | 1598.25 | (no answer) | no | no | (no answer) | no |
| Q03 | 48.5 | (no answer) | no | no | 48.5 | yes |
| Q04 | 961.55 | (no answer) | no | no | 961.55 | yes |
| Q05 | Soda, Water | (no answer) | no | no | Water, Soda | yes |
| Q06 | 1052.8 | (no answer) | no | no | 1052.8 | yes |
| Q07 | 507.0 | (no answer) | no | no | (no answer) | no |
| Q08 | 608.15 | (no answer) | no | no | 608.1500000000001 | yes |
| Q09 | PL01, PL02 | (no answer) | no | no | (no answer) | no |
| Q10 | SKU-1002, SKU-1003, SKU-1004, SKU-1005, SKU-1006, SKU-1007 | (no answer) | no | no | SKU-1002, SKU-1003, SKU-1004, SKU-1005, SKU-1006, SKU-1007 | yes |
| Q11 | 3.0 | (no answer) | no | no | (no answer) | no |
| Q12 | 90.0 | (no answer) | no | no | 90 | yes |

- Auto Ontology arm: 0 / 12 correct
- Raw-schema arm: 8 / 12 correct
- Delta (Auto Ontology minus raw schema): -8

## Failure gallery

### Q01, Auto Ontology arm

- expected: 1549.75
- got: (no answer)

No SQL was produced.

### Q02, Auto Ontology arm

- expected: 1598.25
- got: (no answer)

No SQL was produced.

### Q02, raw-schema arm

- expected: 1598.25
- got: (no answer)
- error: no such column: a.gross_sales

Generated SQL, verbatim:

```sql
SELECT SUM(a.gross_sales) FROM a.fact_sales;
```

### Q03, Auto Ontology arm

- expected: 48.5
- got: (no answer)

No SQL was produced.

### Q04, Auto Ontology arm

- expected: 961.55
- got: (no answer)

No SQL was produced.

### Q05, Auto Ontology arm

- expected: Soda, Water
- got: (no answer)

No SQL was produced.

### Q06, Auto Ontology arm

- expected: 1052.8
- got: (no answer)

No SQL was produced.

### Q07, Auto Ontology arm

- expected: 507.0
- got: (no answer)

No SQL was produced.

### Q07, raw-schema arm

- expected: 507.0
- got: (no answer)

Generated SQL, verbatim:

```sql
SELECT SUM(units) FROM b.shipments WHERE plant_code = 'Lyon Works';
```

### Q08, Auto Ontology arm

- expected: 608.15
- got: (no answer)

No SQL was produced.

### Q09, Auto Ontology arm

- expected: PL01, PL02
- got: (no answer)

No SQL was produced.

### Q09, raw-schema arm

- expected: PL01, PL02
- got: (no answer)
- error: no such column: b.plant_code

Generated SQL, verbatim:

```sql
SELECT DISTINCT b.plant_code FROM b.shipments JOIN b.distribution_centers ON b.shipments.dc_code = b.distribution_centers.dc_code WHERE b.distribution_centers.dc_city = 'Milan';
```

### Q10, Auto Ontology arm

- expected: SKU-1002, SKU-1003, SKU-1004, SKU-1005, SKU-1006, SKU-1007
- got: (no answer)

No SQL was produced.

### Q11, Auto Ontology arm

- expected: 3.0
- got: (no answer)

No SQL was produced.

### Q11, raw-schema arm

- expected: 3.0
- got: (no answer)

No SQL was produced.

### Q12, Auto Ontology arm

- expected: 90.0
- got: (no answer)

No SQL was produced.

## Limits

This is what the fixture did not exercise. No claim here goes beyond it.

- All data is synthetic: 8 small tables (dozens of rows) across one Postgres and one DuckDB source, built from fixed seed files. Results say nothing about scale, data volume or real enterprise schemas.
- The fixture plants four conflicts only (net_sales semantics, location identity, product hierarchy, shared SKU identity). Other conflict kinds (units of measure, currencies, time zones, slowly changing dimensions, fiscal calendars) were not exercised.
- 12 questions, each answered once per arm with one fixed chat model and fixed generation settings. Run-to-run variance, other models and prompt variants were not tested.
- Only the default hosted NIM configuration was used; self-hosted NIMs, other connectors and the web UI workflows were not exercised.
- The MCP surface was probed (tools listing) but agents using the MCP tools end to end were not tested.
- Security, access control, multi-user behaviour, cost and latency beyond the measured time to first ontology were not covered.

### Equivalents used instead of the literal spec step

Each entry is a place where the run did something other than the literal step in S1 to S4.

- S1: MCP tools listed in process against the pinned MCP server module (fastmcp in-memory client), instead of MCP tools/list request sent over the network to the running MCP server. Why: the pinned MCP server is not part of the upstream compose stack and its HTTP endpoint requires a frontend OAuth token, which the harness has no way to obtain without the interactive web login.
- S4: raw-schema arm SQL executed on an in-memory SQLite copy of the fixture, loaded from the same seed files, with Source A as schema a and Source B as schema b, instead of raw-schema arm SQL executed on the live Postgres (Source A) and DuckDB (Source B) sources. Why: the two live sources are separate engines, so one model-written query cannot join across them; a single SQLite copy holding both sources lets the raw-schema arm answer every question, including cross-source ones, with one query, and is the same engine the reference SQL ground truths were computed on.
