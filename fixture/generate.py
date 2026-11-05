"""One-off generator for the S2 fixture. Kept for transparency.

    python fixture/generate.py

Writes the seed CSVs from random.Random(20261105), then computes every
expected answer by running its reference SQL on the seeds, and writes
checklist.json, questions.json and GROUND_TRUTH.md. Running it again
produces byte-identical files. The run itself never calls this script;
it reads the committed files.
"""
from __future__ import annotations

import csv
import json
import random
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from auto_ontology_eval import fixture  # noqa: E402

SEED = 20261105

# Source A product master: brand -> category hierarchy.
PRODUCTS = [
    ("SKU-1001", "Alpine Spring Still 1L", "Alpine Spring", "Water", "1.20"),
    ("SKU-1002", "Alpine Spring Sparkling 1L", "Alpine Spring", "Water", "1.40"),
    ("SKU-1003", "Alpine Spring Lemon Soda 330ml", "Alpine Spring", "Soda", "0.90"),
    ("SKU-1004", "Nordwind Apple Juice 1L", "Nordwind", "Juice", "2.60"),
    ("SKU-1005", "Nordwind Orange Juice 1L", "Nordwind", "Juice", "2.80"),
    ("SKU-1006", "Nordwind Cola 330ml", "Nordwind", "Soda", "0.95"),
    ("SKU-1007", "Sol Mar Mango Juice 1L", "Sol Mar", "Juice", "3.10"),
    ("SKU-1008", "Sol Mar Tonic 330ml", "Sol Mar", "Soda", "1.05"),
]
# Sold SKUs (shared with Source B); SKU-1001 and SKU-1008 are A only.
SHARED = ["SKU-1002", "SKU-1003", "SKU-1004", "SKU-1005", "SKU-1006", "SKU-1007"]
# Source B item master: a different grouping (temperature chain), no brand.
B_ONLY = [
    ("SKU-1009", "ICED TEA PEACH 500ML", "Chilled"),
    ("SKU-1010", "SPORTS DRINK BERRY 500ML", "Ambient"),
    ("SKU-1011", "COLD BREW COFFEE 250ML", "Chilled"),
]
B_GROUP = {
    "SKU-1002": "Ambient", "SKU-1003": "Ambient", "SKU-1004": "Chilled",
    "SKU-1005": "Chilled", "SKU-1006": "Ambient", "SKU-1007": "Chilled",
}

LOCATIONS = [
    # location_id, A name, city, kind, B code
    (1, "Lyon Works", "Lyon", "plant", "PL01"),
    (2, "Porto Works", "Porto", "plant", "PL02"),
    (3, "Rotterdam Hub", "Rotterdam", "dc", "DC-N1"),
    (4, "Milan Depot", "Milan", "dc", "DC-S1"),
]

TABLES = {}


def money(x: Decimal) -> str:
    return f"{x.quantize(Decimal('0.01'))}"


def build_rows():
    rng = random.Random(SEED)
    price = {p[0]: Decimal(p[4]) for p in PRODUCTS}
    name = {p[0]: p[1] for p in PRODUCTS}

    TABLES[("A", "dim_product")] = [
        {"sku": s, "product_name": n, "brand": b, "category": c, "list_price": p}
        for s, n, b, c, p in PRODUCTS
    ]
    TABLES[("A", "dim_location")] = [
        {"location_id": str(i), "location_name": n, "city": c, "location_kind": k}
        for i, n, c, k, _ in LOCATIONS
    ]
    sales, returns, shipments = [], [], []
    return_id = 1
    for sale_id in range(1, 25):
        sku = SHARED[(sale_id - 1) % len(SHARED)]
        dc = LOCATIONS[2 + rng.randrange(2)]
        plant = LOCATIONS[rng.randrange(2)]
        units = rng.randint(10, 60)
        day = 1 + rng.randrange(28)
        date = f"2026-03-{day:02d}"
        gross = price[sku] * units
        ret = Decimal("0")
        if sale_id % 4 == 0:
            ret_units = rng.randint(1, 5)
            ret = price[sku] * ret_units
            returns.append({
                "return_id": str(return_id), "sale_id": str(sale_id),
                "return_date": f"2026-04-{day:02d}", "return_amount": money(ret),
            })
            return_id += 1
        sales.append({
            "sale_id": str(sale_id), "sale_date": date, "sku": sku,
            "location_id": str(dc[0]), "units": str(units),
            "gross_sales": money(gross), "net_sales": money(gross - ret),
        })
        # The ops mart records the same physical movement; its net_sales is
        # the gross invoice value and so still includes the later return.
        shipments.append({
            "shipment_id": str(5000 + sale_id), "ship_date": date, "item_sku": sku,
            "plant_code": plant[4], "dc_code": dc[4], "units": str(units),
            "net_sales": money(gross),
        })
    TABLES[("A", "fact_sales")] = sales
    TABLES[("A", "sales_returns")] = returns
    TABLES[("B", "plants")] = [
        {"plant_code": "PL01", "plant_city": "Lyon", "capacity_units": "12000"},
        {"plant_code": "PL02", "plant_city": "Porto", "capacity_units": "8000"},
    ]
    TABLES[("B", "distribution_centers")] = [
        {"dc_code": "DC-N1", "dc_city": "Rotterdam", "region": "North"},
        {"dc_code": "DC-S1", "dc_city": "Milan", "region": "South"},
    ]
    TABLES[("B", "items")] = [
        {"item_sku": s, "item_description": name[s].upper(), "product_group": B_GROUP[s]}
        for s in SHARED
    ] + [{"item_sku": s, "item_description": d, "product_group": g} for s, d, g in B_ONLY]
    TABLES[("B", "shipments")] = shipments


def write_seeds():
    for (source, table), rows in TABLES.items():
        path = fixture.seed_path(source, table)
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)


QUESTIONS = [
    ("Q01", "What is the company's total net sales after returns?", "number",
     ["net_sales_semantics"],
     "SELECT ROUND(SUM(net_sales), 2) FROM a.fact_sales",
     "Sum of fact_sales.net_sales (Source A, already net of returns)."),
    ("Q02", "What is the total gross sales value before any returns?", "number",
     ["net_sales_semantics"],
     "SELECT ROUND(SUM(net_sales), 2) FROM b.shipments",
     "Sum of shipments.net_sales (Source B, gross, returns included); equals SUM(fact_sales.gross_sales)."),
    ("Q03", "What is the total value of returns?", "number",
     ["net_sales_semantics"],
     "SELECT ROUND((SELECT SUM(net_sales) FROM b.shipments) - (SELECT SUM(net_sales) FROM a.fact_sales), 2)",
     "Source B net_sales total minus Source A net_sales total; equals SUM(sales_returns.return_amount)."),
    ("Q04", "What are net sales after returns for the brand Nordwind?", "number",
     ["net_sales_semantics", "product_hierarchy"],
     "SELECT ROUND(SUM(f.net_sales), 2) FROM a.fact_sales f JOIN a.dim_product p ON p.sku = f.sku WHERE p.brand = 'Nordwind'",
     "fact_sales joined to dim_product, brand = Nordwind."),
    ("Q05", "Which categories does the brand Alpine Spring have products in?", "set",
     ["product_hierarchy"],
     "SELECT DISTINCT category FROM a.dim_product WHERE brand = 'Alpine Spring'",
     "dim_product rows with brand = Alpine Spring."),
    ("Q06", "What are net sales after returns for the Juice category?", "number",
     ["net_sales_semantics", "product_hierarchy"],
     "SELECT ROUND(SUM(f.net_sales), 2) FROM a.fact_sales f JOIN a.dim_product p ON p.sku = f.sku WHERE p.category = 'Juice'",
     "fact_sales joined to dim_product, category = Juice."),
    ("Q07", "How many units were shipped from Lyon Works?", "number",
     ["location_identity"],
     "SELECT SUM(s.units) FROM b.shipments s JOIN b.plants pl ON pl.plant_code = s.plant_code JOIN a.dim_location l ON l.city = pl.plant_city WHERE l.location_name = 'Lyon Works'",
     "Lyon Works is plant code PL01 in Source B; sum of shipments.units where plant_code = PL01."),
    ("Q08", "What are net sales after returns for sales through distribution center DC-N1?", "number",
     ["location_identity", "net_sales_semantics"],
     "SELECT ROUND(SUM(f.net_sales), 2) FROM a.fact_sales f JOIN a.dim_location l ON l.location_id = f.location_id JOIN b.distribution_centers d ON d.dc_city = l.city WHERE d.dc_code = 'DC-N1'",
     "DC-N1 is Rotterdam Hub in Source A; sum of fact_sales.net_sales at Rotterdam Hub."),
    ("Q09", "Which plant codes shipped goods to Milan Depot?", "set",
     ["location_identity"],
     "SELECT DISTINCT s.plant_code FROM b.shipments s JOIN b.distribution_centers d ON d.dc_code = s.dc_code JOIN a.dim_location l ON l.city = d.dc_city WHERE l.location_name = 'Milan Depot'",
     "Milan Depot is DC-S1 in Source B; distinct shipments.plant_code where dc_code = DC-S1."),
    ("Q10", "Which SKUs exist in both the sales mart and the ops mart?", "set",
     ["shared_sku_identity"],
     "SELECT sku FROM a.dim_product INTERSECT SELECT item_sku FROM b.items",
     "dim_product.sku intersected with items.item_sku."),
    ("Q11", "How many SKUs exist only in the ops mart?", "number",
     ["shared_sku_identity"],
     "SELECT COUNT(*) FROM (SELECT item_sku FROM b.items EXCEPT SELECT sku FROM a.dim_product)",
     "items.item_sku not present in dim_product.sku."),
    ("Q12", "How many units of the brand Sol Mar were shipped?", "number",
     ["shared_sku_identity", "product_hierarchy"],
     "SELECT SUM(s.units) FROM b.shipments s JOIN a.dim_product p ON p.sku = s.item_sku WHERE p.brand = 'Sol Mar'",
     "shipments joined to dim_product on SKU (item_sku = sku), brand = Sol Mar."),
]


def checklist(returns_total, a_total, b_total, shared):
    return {"conflicts": [
        {
            "id": "net_sales_semantics",
            "description": "Both marts have a column named net_sales with different meanings.",
            "involves": [
                {"source": "A", "table": "fact_sales", "column": "net_sales"},
                {"source": "B", "table": "shipments", "column": "net_sales"},
            ],
            "ground_truth": {
                "source_a_meaning": "gross_sales minus returns (excludes returns)",
                "source_b_meaning": "gross invoice value (includes returns)",
                "source_a_total": float(a_total),
                "source_b_total": float(b_total),
                "returns_total": float(returns_total),
            },
        },
        {
            "id": "location_identity",
            "description": "Source B identifies plants and DCs by codes; Source A uses names for the same sites.",
            "involves": [
                {"source": "A", "table": "dim_location", "column": "location_name"},
                {"source": "B", "table": "plants", "column": "plant_code"},
                {"source": "B", "table": "distribution_centers", "column": "dc_code"},
            ],
            "ground_truth": {
                "join_path": "dim_location.city = plants.plant_city / distribution_centers.dc_city",
                "mapping": [
                    {"code": code, "kind": kind, "name": name}
                    for _, name, _, kind, code in LOCATIONS
                ],
            },
        },
        {
            "id": "product_hierarchy",
            "description": "Source A groups products brand then category; Source B uses product_group with no brand.",
            "involves": [
                {"source": "A", "table": "dim_product", "column": "brand"},
                {"source": "A", "table": "dim_product", "column": "category"},
                {"source": "B", "table": "items", "column": "product_group"},
            ],
            "ground_truth": {
                "source_a_levels": ["brand", "category"],
                "source_b_levels": ["product_group"],
            },
        },
        {
            "id": "shared_sku_identity",
            "description": "The same SKU is dim_product.sku in A and items.item_sku in B.",
            "involves": [
                {"source": "A", "table": "dim_product", "column": "sku"},
                {"source": "B", "table": "items", "column": "item_sku"},
            ],
            "ground_truth": {"shared_skus": shared},
        },
    ]}


def fmt(v):
    return f"{float(v):.2f}" if not isinstance(v, list) else ", ".join(v)


def main():
    build_rows()
    write_seeds()
    conn = fixture.reference_connection()
    a_total = Decimal(conn.execute("SELECT printf('%.2f', SUM(net_sales)) FROM a.fact_sales").fetchone()[0])
    b_total = Decimal(conn.execute("SELECT printf('%.2f', SUM(net_sales)) FROM b.shipments").fetchone()[0])
    returns_total = Decimal(conn.execute("SELECT printf('%.2f', SUM(return_amount)) FROM a.sales_returns").fetchone()[0])
    assert b_total - a_total == returns_total, (a_total, b_total, returns_total)
    shared = sorted(r[0] for r in conn.execute(
        "SELECT sku FROM a.dim_product INTERSECT SELECT item_sku FROM b.items"))
    (HERE / "checklist.json").write_text(
        json.dumps(checklist(returns_total, a_total, b_total, shared), indent=2) + "\n")

    questions = []
    for qid, text, kind, cids, sql, how in QUESTIONS:
        rows = conn.execute(sql).fetchall()
        if kind == "number":
            assert len(rows) == 1 and len(rows[0]) == 1, (qid, rows)
            expected = round(float(rows[0][0]), 2)
        else:
            expected = sorted(str(r[0]) for r in rows)
        questions.append({
            "id": qid, "question": text, "answer_type": kind, "expected": expected,
            "reference_sql": sql, "conflict_ids": cids, "derivation": how,
        })
    (HERE / "questions.json").write_text(json.dumps({"questions": questions}, indent=2) + "\n")
    write_ground_truth(questions, a_total, b_total, returns_total, shared)


def write_ground_truth(questions, a_total, b_total, returns_total, shared):
    L = [
        "# Fixture ground truth",
        "",
        "Synthetic data only. Every value below can be recomputed by hand from the seed",
        "CSVs in `source_a/seeds/` and `source_b/seeds/`. The expected answers were",
        "computed by running each question's reference SQL over the seeds (SQLite, Source A",
        "attached as schema `a`, Source B as schema `b`) before any model was called.",
        "",
        "## Sources",
        "",
        "- Source A, Postgres sales mart: `dim_product`, `dim_location`, `fact_sales`, `sales_returns`.",
        "- Source B, DuckDB ops mart: `plants`, `distribution_centers`, `items`, `shipments`.",
        "- 8 tables in total. Each Source B shipment records the same movement as the Source A sale",
        "  with the same SKU, date and units (`shipment_id` = 5000 + `sale_id`).",
        "",
        "## Planted conflicts",
        "",
        "1. `net_sales_semantics`: `fact_sales.net_sales` (A) is `gross_sales` minus returns, so it",
        "   excludes returns. `shipments.net_sales` (B) is the gross invoice value, so it includes",
        f"   returns. A total {a_total:.2f}; B total {b_total:.2f}; returns total",
        f"   (`SUM(sales_returns.return_amount)`) {returns_total:.2f} = B total minus A total.",
        "2. `location_identity`: B identifies sites by code, A by name. The only join is the city",
        "   column (`dim_location.city` = `plants.plant_city` / `distribution_centers.dc_city`).",
        "",
        "   | B code | kind | A location_name |",
        "   |---|---|---|",
    ]
    for _, name, _, kind, code in LOCATIONS:
        L.append(f"   | {code} | {kind} | {name} |")
    L += [
        "",
        "3. `product_hierarchy`: A uses brand, then category (`dim_product.brand`,",
        "   `dim_product.category`). B has a single `items.product_group` (Ambient / Chilled)",
        "   and no brand.",
        "4. `shared_sku_identity`: the same SKU is `dim_product.sku` in A and `items.item_sku` in B.",
        f"   Shared SKUs: {', '.join(shared)}. A only: SKU-1001, SKU-1008. B only: SKU-1009,",
        "   SKU-1010, SKU-1011.",
        "",
        "## Questions and expected answers",
        "",
        "| id | question | expected | conflicts | how to recompute |",
        "|---|---|---|---|---|",
    ]
    for q in questions:
        L.append(f"| {q['id']} | {q['question']} | {fmt(q['expected'])} | "
                 f"{', '.join(q['conflict_ids'])} | {q['derivation']} |")
    L += ["", "## Reference SQL", ""]
    for q in questions:
        L += [f"- {q['id']}:", "", "  ```sql", f"  {q['reference_sql']}", "  ```", ""]
    (HERE / "GROUND_TRUTH.md").write_text("\n".join(L))


if __name__ == "__main__":
    main()
