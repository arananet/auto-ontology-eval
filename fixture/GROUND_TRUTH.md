# Fixture ground truth

Synthetic data only. Every value below can be recomputed by hand from the seed
CSVs in `source_a/seeds/` and `source_b/seeds/`. The expected answers were
computed by running each question's reference SQL over the seeds (SQLite, Source A
attached as schema `a`, Source B as schema `b`) before any model was called.

## Sources

- Source A, Postgres sales mart: `dim_product`, `dim_location`, `fact_sales`, `sales_returns`.
- Source B, DuckDB ops mart: `plants`, `distribution_centers`, `items`, `shipments`.
- 8 tables in total. Each Source B shipment records the same movement as the Source A sale
  with the same SKU, date and units (`shipment_id` = 5000 + `sale_id`).

## Planted conflicts

1. `net_sales_semantics`: `fact_sales.net_sales` (A) is `gross_sales` minus returns, so it
   excludes returns. `shipments.net_sales` (B) is the gross invoice value, so it includes
   returns. A total 1549.75; B total 1598.25; returns total
   (`SUM(sales_returns.return_amount)`) 48.50 = B total minus A total.
2. `location_identity`: B identifies sites by code, A by name. The only join is the city
   column (`dim_location.city` = `plants.plant_city` / `distribution_centers.dc_city`).

   | B code | kind | A location_name |
   |---|---|---|
   | PL01 | plant | Lyon Works |
   | PL02 | plant | Porto Works |
   | DC-N1 | dc | Rotterdam Hub |
   | DC-S1 | dc | Milan Depot |

3. `product_hierarchy`: A uses brand, then category (`dim_product.brand`,
   `dim_product.category`). B has a single `items.product_group` (Ambient / Chilled)
   and no brand.
4. `shared_sku_identity`: the same SKU is `dim_product.sku` in A and `items.item_sku` in B.
   Shared SKUs: SKU-1002, SKU-1003, SKU-1004, SKU-1005, SKU-1006, SKU-1007. A only: SKU-1001, SKU-1008. B only: SKU-1009,
   SKU-1010, SKU-1011.

## Questions and expected answers

| id | question | expected | conflicts | how to recompute |
|---|---|---|---|---|
| Q01 | What is the company's total net sales after returns? | 1549.75 | net_sales_semantics | Sum of fact_sales.net_sales (Source A, already net of returns). |
| Q02 | What is the total gross sales value before any returns? | 1598.25 | net_sales_semantics | Sum of shipments.net_sales (Source B, gross, returns included); equals SUM(fact_sales.gross_sales). |
| Q03 | What is the total value of returns? | 48.50 | net_sales_semantics | Source B net_sales total minus Source A net_sales total; equals SUM(sales_returns.return_amount). |
| Q04 | What are net sales after returns for the brand Nordwind? | 961.55 | net_sales_semantics, product_hierarchy | fact_sales joined to dim_product, brand = Nordwind. |
| Q05 | Which categories does the brand Alpine Spring have products in? | Soda, Water | product_hierarchy | dim_product rows with brand = Alpine Spring. |
| Q06 | What are net sales after returns for the Juice category? | 1052.80 | net_sales_semantics, product_hierarchy | fact_sales joined to dim_product, category = Juice. |
| Q07 | How many units were shipped from Lyon Works? | 507.00 | location_identity | Lyon Works is plant code PL01 in Source B; sum of shipments.units where plant_code = PL01. |
| Q08 | What are net sales after returns for sales through distribution center DC-N1? | 608.15 | location_identity, net_sales_semantics | DC-N1 is Rotterdam Hub in Source A; sum of fact_sales.net_sales at Rotterdam Hub. |
| Q09 | Which plant codes shipped goods to Milan Depot? | PL01, PL02 | location_identity | Milan Depot is DC-S1 in Source B; distinct shipments.plant_code where dc_code = DC-S1. |
| Q10 | Which SKUs exist in both the sales mart and the ops mart? | SKU-1002, SKU-1003, SKU-1004, SKU-1005, SKU-1006, SKU-1007 | shared_sku_identity | dim_product.sku intersected with items.item_sku. |
| Q11 | How many SKUs exist only in the ops mart? | 3.00 | shared_sku_identity | items.item_sku not present in dim_product.sku. |
| Q12 | How many units of the brand Sol Mar were shipped? | 90.00 | shared_sku_identity, product_hierarchy | shipments joined to dim_product on SKU (item_sku = sku), brand = Sol Mar. |

## Reference SQL

- Q01:

  ```sql
  SELECT ROUND(SUM(net_sales), 2) FROM a.fact_sales
  ```

- Q02:

  ```sql
  SELECT ROUND(SUM(net_sales), 2) FROM b.shipments
  ```

- Q03:

  ```sql
  SELECT ROUND((SELECT SUM(net_sales) FROM b.shipments) - (SELECT SUM(net_sales) FROM a.fact_sales), 2)
  ```

- Q04:

  ```sql
  SELECT ROUND(SUM(f.net_sales), 2) FROM a.fact_sales f JOIN a.dim_product p ON p.sku = f.sku WHERE p.brand = 'Nordwind'
  ```

- Q05:

  ```sql
  SELECT DISTINCT category FROM a.dim_product WHERE brand = 'Alpine Spring'
  ```

- Q06:

  ```sql
  SELECT ROUND(SUM(f.net_sales), 2) FROM a.fact_sales f JOIN a.dim_product p ON p.sku = f.sku WHERE p.category = 'Juice'
  ```

- Q07:

  ```sql
  SELECT SUM(s.units) FROM b.shipments s JOIN b.plants pl ON pl.plant_code = s.plant_code JOIN a.dim_location l ON l.city = pl.plant_city WHERE l.location_name = 'Lyon Works'
  ```

- Q08:

  ```sql
  SELECT ROUND(SUM(f.net_sales), 2) FROM a.fact_sales f JOIN a.dim_location l ON l.location_id = f.location_id JOIN b.distribution_centers d ON d.dc_city = l.city WHERE d.dc_code = 'DC-N1'
  ```

- Q09:

  ```sql
  SELECT DISTINCT s.plant_code FROM b.shipments s JOIN b.distribution_centers d ON d.dc_code = s.dc_code JOIN a.dim_location l ON l.city = d.dc_city WHERE l.location_name = 'Milan Depot'
  ```

- Q10:

  ```sql
  SELECT sku FROM a.dim_product INTERSECT SELECT item_sku FROM b.items
  ```

- Q11:

  ```sql
  SELECT COUNT(*) FROM (SELECT item_sku FROM b.items EXCEPT SELECT sku FROM a.dim_product)
  ```

- Q12:

  ```sql
  SELECT SUM(s.units) FROM b.shipments s JOIN a.dim_product p ON p.sku = s.item_sku WHERE p.brand = 'Sol Mar'
  ```
