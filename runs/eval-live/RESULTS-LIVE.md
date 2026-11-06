# RESULTS-LIVE: NVIDIA Auto Ontology enterprise evaluation, live-internals configuration

Internal evidence artifact, written by the harness from run artifacts only. Not for publication.

Second configuration under spec Amendment 3: identical to the default configuration except that the stack's internal chat model slots (DEFAULT_MODELS_MODEL, REASONING_MODEL, NON_REASONING_MODEL) are wired to the pinned chat model. The default configuration's results stand in runs/eval/RESULTS.md; this run does not modify them.

## Environment

- Runner: `ubuntu24 20261101.360.1 (GitHub Actions, GitHub Actions 1000013143, Linux)`
- GitHub run id: `42162053401`
- Upstream repository: `https://github.com/NVIDIA/auto-ontology.git`
- Upstream commit: `cdaf61e1bd0cf3820d11d72b43bb460816aebbd3`
- Chat model: `nvidia/nemotron-3.5-lightning-30b-a3b`
- Embedding model: `nvidia/nemotron-3-embed-1b`
- Rerank model: `nvidia/llama-nemotron-rerank-vl-1b-v2`
- Run date: `2026-11-06T04:21:58Z`

### Stack smoke (S1)

- health: pass (evidence `smoke/health.txt`)
- catalog: pass (evidence `smoke/catalog.txt`)
- mcp: pass (evidence `smoke/mcp.txt`)

- Configuration: `live-internals`

### Internal models resolved in the running stack (S1)

- DEFAULT_MODELS_MODEL: `nvidia/nemotron-3.5-lightning-30b-a3b`
- EMBED_MODEL: `nvidia/nemotron-3-embed-1b`
- NON_REASONING_MODEL: `nvidia/nemotron-3.5-lightning-30b-a3b`
- REASONING_MODEL: `nvidia/nemotron-3.5-lightning-30b-a3b`
- RERANK_MODEL: `nvidia/llama-nemotron-rerank-vl-1b-v2`

## Time to first ontology

- 361.07 s from both sources registered to the first complete catalog export.
- start: `2026-11-06T04:25:16.788241Z`
- end: `2026-11-06T04:31:17.858944Z`

- Default configuration: 15.42 s (GitHub Actions run 42127124473, `runs/eval/timing.json`).

## Catalog description coverage

Description fields are the `description:` lines of the exported catalog. A field is authored when it carries a real definition, blank when its value is empty, and template when it is one of the upstream's own templated lines ("Business entity represented by table ..." or a "format: ..." note).

- Live-internals catalog: 88 description fields: 39 authored, 49 blank, 0 template.
- Default configuration catalog (`runs/eval/catalog.yaml`): 88 description fields: 0 authored, 77 blank, 11 template.

## Reconciliation checklist

4 planted conflicts; 4 marks backed by a verbatim catalog quote. A mark without a verbatim quote does not count.

### net_sales_semantics: ignored (counted: yes)

Quote from the exported catalog:

```text
name: shipments
```

### location_identity: ignored (counted: yes)

Quote from the exported catalog:

```text
name: distribution_centers
```

### product_hierarchy: ignored (counted: yes)

Quote from the exported catalog:

```text
name: items
```

### shared_sku_identity: ignored (counted: yes)

Quote from the exported catalog:

```text
name: items
```

- Default configuration (GitHub Actions run 42127124473): net_sales_semantics ignored, location_identity ignored, product_hierarchy ignored, shared_sku_identity ignored.

## Per-question results (Auto Ontology arm)

Auto Ontology arm: model `nvidia/nemotron-3.5-lightning-30b-a3b`, settings `{"max_tokens": 8192, "temperature": 0.0}`. The raw-schema arm was not rerun in this configuration.

| id | expected | Auto Ontology answer | correct | provenance | SQL produced |
|---|---|---|---|---|---|
| Q01 | 1549.75 | [{"sum":1549.75}] | no | no | yes |
| Q02 | 1598.25 | [{"total_gross_sales_before_returns":1598.25}] | no | no | yes |
| Q03 | 48.5 | [{"total_value_of_returns":48.5}] | no | no | yes |
| Q04 | 961.55 | [{"net_sales_after_returns":950.35}] | no | no | yes |
| Q05 | Soda, Water | [{"category":"Soda"},{"category":"Water"}] | no | no | yes |
| Q06 | 1052.8 | (no answer) | no | no | no |
| Q07 | 507.0 | [{"sum(s.units)":507.0}] | no | no | yes |
| Q08 | 608.15 | [{"net_sales_after_returns":625.45}] | no | no | yes |
| Q09 | PL01, PL02 | [{"plant_code":"PL01"},{"plant_code":"PL01"},{"plant_code":"PL02"},{"plant_code":"PL02"},{"plant_code":"PL01"},{"plant_code":"PL01"},{"plant_code":"PL01"},{"plant_code":"PL02"},{"plant_code":"PL02"},{"plant_code":"PL02"},{"plant_code":"PL02"},{"plant_code":"PL01"},{"plant_code":"PL02"},{"plant_code":"PL02"}] | no | no | yes |
| Q10 | SKU-1002, SKU-1003, SKU-1004, SKU-1005, SKU-1006, SKU-1007 | [{"sku":"SKU-1007"},{"sku":"SKU-1006"},{"sku":"SKU-1003"},{"sku":"SKU-1004"},{"sku":"SKU-1005"},{"sku":"SKU-1002"}] | no | no | yes |
| Q11 | 3.0 | [{"sku_count":2}] | no | no | yes |
| Q12 | 90.0 | [{"total_units":90}] | no | no | yes |

- Auto Ontology arm: 0 / 12 correct
- Questions where the arm produced SQL: 11 / 12
- Answers carrying provenance: 0 / 12

## Comparison with the default configuration and the standing control

- Live-internals Auto Ontology arm: 0 / 12 correct (this run, GitHub Actions run 42162053401).
- Default configuration Auto Ontology arm: 0 / 12 correct (GitHub Actions run 42127124473, `runs/eval/ablation.json`).
- Raw-schema control arm, not rerun (spec Amendment 3): 8 / 12 correct (GitHub Actions run 42127124473, `runs/eval/ablation.json`).
- Both ablation records used model `nvidia/nemotron-3.5-lightning-30b-a3b` with settings `{"max_tokens": 8192, "temperature": 0.0}`; the standing control is comparable on model and settings.
- Delta (live-internals Auto Ontology minus standing raw-schema control): -8
- Delta (live-internals minus default configuration, Auto Ontology arm): +0

## Failure gallery

### Q01, Auto Ontology arm

- expected: 1549.75
- got: [{"sum":1549.75}]
- response: This calculates the company's total net sales after returns by summing the net_sales column from the fact_sales table, which records revenue after adjustments (including returns). The result is a single total value representing all net sales across the company.

Generated SQL, verbatim:

```sql
SELECT SUM(net_sales) FROM sales_mart.public.fact_sales
```

### Q02, Auto Ontology arm

- expected: 1598.25
- got: [{"total_gross_sales_before_returns":1598.25}]
- response: This calculates the total gross sales revenue from the fact_sales table, which by definition represents total revenue before any deductions including returns. The SUM of the gross_sales column aggregates all sales records to produce the total gross sales value before returns, using the sales_mart.public.fact_sales table.

Generated SQL, verbatim:

```sql
SELECT SUM(gross_sales) AS total_gross_sales_before_returns FROM sales_mart.public.fact_sales;
```

### Q03, Auto Ontology arm

- expected: 48.5
- got: [{"total_value_of_returns":48.5}]
- response: This query calculates the total monetary value of all return transactions by summing the return amount column from the sales returns table. It includes every return record since no time window or filtering conditions are applied, and the non-nullable return amount ensures all values contribute to the total.

Generated SQL, verbatim:

```sql
SELECT SUM(return_amount) AS total_value_of_returns FROM sales_mart.public.sales_returns;
```

### Q04, Auto Ontology arm

- expected: 961.55
- got: [{"net_sales_after_returns":950.35}]
- response: This query calculates total net sales after returns for the Nordwind brand. It starts with dim_product filtered to brand 'Nordwind', joins to fact_sales on sku to access each sale's net_sales, then left-joins a subquery that aggregates total return_amount per sale_id from sales_returns. COALESCE handles sales with no returns (treating them as 0). The final SUM subtracts total returns from net_sales across all Nordwind sales, yielding the brand's net sales after returns.

Generated SQL, verbatim:

```sql
SELECT SUM(s.net_sales - COALESCE(tr.total_return, 0)) AS net_sales_after_returns FROM sales_mart.public.dim_product AS p JOIN sales_mart.public.fact_sales AS s ON p.sku = s.sku LEFT JOIN (SELECT sale_id, SUM(return_amount) AS total_return FROM sales_mart.public.sales_returns GROUP BY sale_id) AS tr ON s.sale_id = tr.sale_id WHERE p.brand = 'Nordwind'
```

### Q05, Auto Ontology arm

- expected: Soda, Water
- got: [{"category":"Soda"},{"category":"Water"}]
- response: This query returns the unique product categories for all products branded by Alpine Spring. It filters the dim_product table to rows where the brand column equals 'Alpine Spring' and then projects the distinct values from the category column, giving the complete set of product categories associated with that brand.

Generated SQL, verbatim:

```sql
SELECT DISTINCT category FROM sales_mart.public.dim_product WHERE brand = 'Alpine Spring';
```

### Q06, Auto Ontology arm

- expected: 1052.8
- got: (no answer)
- response: LLM failed to produce a response.

No SQL was produced.

### Q07, Auto Ontology arm

- expected: 507.0
- got: [{"sum(s.units)":507.0}]
- response: This query calculates the total number of units shipped from the Lyon plant by joining the shipments table with the plants table on plant_code and filtering for the plant located in Lyon. The SUM of the units column from matching shipment records gives the total units dispatched from that location.

Generated SQL, verbatim:

```sql
SELECT SUM(s.units) FROM ops_mart.main.shipments AS s JOIN ops_mart.main.plants AS p ON s.plant_code = p.plant_code WHERE p.plant_city = 'Lyon';
```

### Q08, Auto Ontology arm

- expected: 608.15
- got: [{"net_sales_after_returns":625.45}]
- response: This query calculates the total net sales after returns for all shipments processed through distribution center DC-N1. It sums the net_sales column from the shipments table, which already represents net revenue after returns, and filters to only include shipments where dc_code is 'DC-N1'.

Generated SQL, verbatim:

```sql
SELECT SUM(net_sales) AS net_sales_after_returns FROM ops_mart.main.shipments WHERE dc_code = 'DC-N1';
```

### Q09, Auto Ontology arm

- expected: PL01, PL02
- got: [{"plant_code":"PL01"},{"plant_code":"PL01"},{"plant_code":"PL02"},{"plant_code":"PL02"},{"plant_code":"PL01"},{"plant_code":"PL01"},{"plant_code":"PL01"},{"plant_code":"PL02"},{"plant_code":"PL02"},{"plant_code":"PL02"},{"plant_code":"PL02"},{"plant_code":"PL01"},{"plant_code":"PL02"},{"plant_code":"PL02"}]
- response: This query retrieves plant codes from the shipments table for all shipments that were sent to distribution centers located in Milan. It joins shipments with distribution_centers on the dc_code column and filters for dc_city = 'Milan', returning the plant_code for each qualifying shipment record.

Generated SQL, verbatim:

```sql
SELECT s.plant_code FROM ops_mart.main.shipments AS s INNER JOIN ops_mart.main.distribution_centers AS d ON s.dc_code = d.dc_code WHERE d.dc_city = 'Milan'
```

### Q10, Auto Ontology arm

- expected: SKU-1002, SKU-1003, SKU-1004, SKU-1005, SKU-1006, SKU-1007
- got: [{"sku":"SKU-1007"},{"sku":"SKU-1006"},{"sku":"SKU-1003"},{"sku":"SKU-1004"},{"sku":"SKU-1005"},{"sku":"SKU-1002"}]
- response: This query finds SKUs that appear in both the product catalog (dim_product) and the sales records (fact_sales) within the sales mart. It joins the two tables on the sku column and returns distinct SKUs that have matching entries in both, which are SKU-1002, SKU-1003, SKU-1004, and SKU-1005 based on the sample data.

Generated SQL, verbatim:

```sql
SELECT DISTINCT d.sku FROM sales_mart.public.dim_product d INNER JOIN sales_mart.public.fact_sales f ON d.sku = f.sku
```

### Q11, Auto Ontology arm

- expected: 3.0
- got: [{"sku_count":2}]
- response: This counts the number of product SKUs defined in the product catalog (dim_product) that have no corresponding sales records in the fact_sales table, representing SKUs that exist only in the ops mart and have never been sold.

Generated SQL, verbatim:

```sql
SELECT COUNT(*) AS sku_count FROM sales_mart.public.dim_product WHERE sku NOT IN (SELECT sku FROM sales_mart.public.fact_sales)
```

### Q12, Auto Ontology arm

- expected: 90.0
- got: [{"total_units":90}]
- response: This query sums the units column from fact_sales for all sales transactions where the associated product in dim_product has brand 'Sol Mar'. The join between fact_sales and dim_product is on the sku column, which is the common key between sales transactions and product catalog information. Filtering by brand isolates only Sol Mar products, and aggregating the units gives the total shipped quantity.

Generated SQL, verbatim:

```sql
SELECT SUM(f.units) AS total_units FROM sales_mart.public.fact_sales AS f JOIN sales_mart.public.dim_product AS p ON f.sku = p.sku WHERE p.brand = 'Sol Mar'
```

## Limits

This is what the fixture did not exercise. No claim here goes beyond it.

- All data is synthetic: 8 small tables (dozens of rows) across one Postgres and one DuckDB source, built from fixed seed files. Results say nothing about scale, data volume or real enterprise schemas.
- The fixture plants four conflicts only (net_sales semantics, location identity, product hierarchy, shared SKU identity). Other conflict kinds (units of measure, currencies, time zones, slowly changing dimensions, fiscal calendars) were not exercised.
- 12 questions, each answered once by the Auto Ontology arm with one fixed chat model and fixed generation settings. Run-to-run variance, other models and prompt variants were not tested.
- The raw-schema control arm was not rerun in this configuration (spec Amendment 3). The standing control result from the default configuration run is cited in the comparison section, and the comparison inherits that run's single-sample limits.
- This configuration wires the stack's internal chat model slots to the evaluation's pinned chat model. It measures a configured stack, not the out-of-the-box default; the default configuration's measurement stands separately in runs/eval/RESULTS.md.
- Only the hosted NIM configuration was used; self-hosted NIMs, other connectors and the web UI workflows were not exercised.
- The MCP surface was probed (tools listing) but agents using the MCP tools end to end were not tested.
- Security, access control, multi-user behaviour, cost and latency beyond the measured time to first ontology were not covered.

### Equivalents used instead of the literal spec step

Each entry is a place where the run did something other than the literal step in S1 to S4.

- S1: MCP tools listed in process against the pinned MCP server module (fastmcp in-memory client), instead of MCP tools/list request sent over the network to the running MCP server. Why: the pinned MCP server is not part of the upstream compose stack and its HTTP endpoint requires a frontend OAuth token, which the harness has no way to obtain without the interactive web login.
