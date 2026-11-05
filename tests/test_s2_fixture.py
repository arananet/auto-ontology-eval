"""S2: a deterministic two-source fixture with planted conflicts.

Layout contract (relative to the project root):
    fixture/source_a/schema.sql           Postgres DDL, sales mart
    fixture/source_a/seeds/<table>.csv    fixed seed rows, one file per table
    fixture/source_b/schema.sql           DuckDB DDL, ops mart
    fixture/source_b/seeds/<table>.csv
    fixture/checklist.json                machine-readable planted conflicts
    fixture/questions.json                the 12 S4 questions + reference SQL
    fixture/GROUND_TRUTH.md               human-readable ground truths

The ground-truth checks below recompute values straight from the seed CSVs
with the csv module, independently of the harness code.
"""
import csv
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

from tests._support import FIXTURE_DIR, REQUIRED_CONFLICT_IDS

from auto_ontology_eval import fixture

SOURCE_DIRS = {"A": FIXTURE_DIR / "source_a", "B": FIXTURE_DIR / "source_b"}


def csv_rows(source, table):
    path = SOURCE_DIRS[source] / "seeds" / f"{table}.csv"
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def column_values(source, table, column):
    return [row[column] for row in csv_rows(source, table)]


def involves(conflict, source):
    return [i for i in conflict["involves"] if i["source"] == source]


class LayoutTests(unittest.TestCase):
    def test_fixture_files_exist(self):
        for rel in (
            "source_a/schema.sql",
            "source_b/schema.sql",
            "checklist.json",
            "questions.json",
            "GROUND_TRUTH.md",
        ):
            with self.subTest(rel=rel):
                self.assertTrue((FIXTURE_DIR / rel).is_file())

    def test_eight_to_ten_tables_across_both_sources(self):
        tables = fixture.table_names()
        self.assertEqual(set(tables), {"A", "B"})
        self.assertTrue(tables["A"] and tables["B"])
        self.assertGreaterEqual(len(tables["A"]) + len(tables["B"]), 8)
        self.assertLessEqual(len(tables["A"]) + len(tables["B"]), 10)

    def test_every_table_has_seed_file_and_ddl(self):
        for source, names in fixture.table_names().items():
            ddl = (SOURCE_DIRS[source] / "schema.sql").read_text().lower()
            for table in names:
                with self.subTest(source=source, table=table):
                    self.assertTrue(
                        (SOURCE_DIRS[source] / "seeds" / f"{table}.csv").is_file()
                    )
                    self.assertRegex(
                        ddl, rf"create table\s+(if not exists\s+)?([\w\"]+\.)?\"?{re.escape(table.lower())}\"?\b"
                    )
                    self.assertTrue(csv_rows(source, table), "seed file is empty")

    def test_seed_rows_api_matches_seed_files(self):
        for source, names in fixture.table_names().items():
            for table in names:
                with self.subTest(source=source, table=table):
                    api = [{k: str(v) for k, v in r.items()} for r in fixture.seed_rows(source, table)]
                    self.assertEqual(api, csv_rows(source, table))


class ChecklistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checklist = fixture.load_checklist()
        cls.by_id = {c["id"]: c for c in cls.checklist}
        cls.tables = fixture.table_names()

    def test_checklist_file_matches_loader(self):
        raw = json.loads((FIXTURE_DIR / "checklist.json").read_text())
        raw_list = raw["conflicts"] if isinstance(raw, dict) else raw
        self.assertEqual([c["id"] for c in raw_list], [c["id"] for c in self.checklist])

    def test_has_the_four_required_conflicts_with_unique_ids(self):
        ids = [c["id"] for c in self.checklist]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(REQUIRED_CONFLICT_IDS <= set(ids), ids)

    def test_every_conflict_has_involves_and_ground_truth(self):
        for c in self.checklist:
            with self.subTest(conflict=c["id"]):
                self.assertTrue(c["involves"])
                self.assertIn("ground_truth", c)
                for inv in c["involves"]:
                    self.assertIn(inv["source"], ("A", "B"))
                    self.assertIn(inv["table"], self.tables[inv["source"]])
                    header = csv_rows(inv["source"], inv["table"])[0].keys()
                    self.assertIn(inv["column"], header)

    def test_conflicts_span_both_sources(self):
        for cid in ("net_sales_semantics", "location_identity", "shared_sku_identity"):
            with self.subTest(conflict=cid):
                self.assertTrue(involves(self.by_id[cid], "A"))
                self.assertTrue(involves(self.by_id[cid], "B"))

    def test_net_sales_a_excludes_returns_b_includes_them(self):
        c = self.by_id["net_sales_semantics"]
        gt = c["ground_truth"]
        (a,), (b,) = involves(c, "A"), involves(c, "B")
        self.assertEqual(a["column"], "net_sales")
        self.assertEqual(b["column"], "net_sales")
        a_total = round(sum(float(v) for v in column_values("A", a["table"], a["column"])), 2)
        b_total = round(sum(float(v) for v in column_values("B", b["table"], b["column"])), 2)
        self.assertEqual(a_total, round(float(gt["source_a_total"]), 2))
        self.assertEqual(b_total, round(float(gt["source_b_total"]), 2))
        self.assertGreater(float(gt["returns_total"]), 0)
        self.assertEqual(round(b_total - a_total, 2), round(float(gt["returns_total"]), 2))

    def test_location_codes_map_to_names_and_differ_from_them(self):
        c = self.by_id["location_identity"]
        mapping = c["ground_truth"]["mapping"]
        self.assertTrue(mapping)
        a_names = {v for i in involves(c, "A") for v in column_values("A", i["table"], i["column"])}
        b_codes = {v for i in involves(c, "B") for v in column_values("B", i["table"], i["column"])}
        kinds = set()
        for entry in mapping:
            with self.subTest(code=entry["code"]):
                self.assertIn(entry["kind"], ("plant", "dc"))
                kinds.add(entry["kind"])
                self.assertIn(entry["code"], b_codes)
                self.assertIn(entry["name"], a_names)
                self.assertNotEqual(entry["code"].strip().lower(), entry["name"].strip().lower())
        self.assertEqual(kinds, {"plant", "dc"})
        # No B code may already equal an A name: the identity must need the map.
        self.assertFalse({x.lower() for x in a_names} & {x.lower() for x in b_codes})
        codes = [e["code"] for e in mapping]
        self.assertEqual(len(codes), len(set(codes)))

    def test_product_hierarchy_a_is_brand_then_category_b_differs(self):
        c = self.by_id["product_hierarchy"]
        gt = c["ground_truth"]
        self.assertEqual([lvl.lower() for lvl in gt["source_a_levels"]], ["brand", "category"])
        self.assertNotEqual(
            [lvl.lower() for lvl in gt.get("source_b_levels", [])], ["brand", "category"]
        )
        a_cols = {i["column"].lower() for i in involves(c, "A")}
        self.assertTrue({"brand", "category"} <= a_cols)

    def test_shared_skus_appear_in_both_sources(self):
        c = self.by_id["shared_sku_identity"]
        shared = c["ground_truth"]["shared_skus"]
        self.assertTrue(shared)
        a_skus = {v for i in involves(c, "A") for v in column_values("A", i["table"], i["column"])}
        b_skus = {v for i in involves(c, "B") for v in column_values("B", i["table"], i["column"])}
        self.assertEqual(set(shared), a_skus & b_skus)


class QuestionsTests(unittest.TestCase):
    """S4 questions live in the fixture; ground truth is fixed before any model run."""

    @classmethod
    def setUpClass(cls):
        cls.questions = fixture.load_questions()
        cls.conflict_ids = {c["id"] for c in fixture.load_checklist()}

    def test_exactly_twelve_questions_with_unique_ids(self):
        self.assertEqual(len(self.questions), 12)
        ids = [q["id"] for q in self.questions]
        self.assertEqual(len(ids), len(set(ids)))

    def test_question_shape(self):
        for q in self.questions:
            with self.subTest(q=q["id"]):
                self.assertTrue(q["question"].strip())
                self.assertTrue(q["reference_sql"].strip())
                self.assertIn(q["answer_type"], ("number", "set"))
                self.assertIn("expected", q)
                if q["answer_type"] == "set":
                    self.assertIsInstance(q["expected"], list)
                else:
                    self.assertIsInstance(q["expected"], (int, float))
                self.assertTrue(set(q["conflict_ids"]) <= self.conflict_ids)

    def test_at_least_one_question_per_planted_conflict(self):
        covered = {cid for q in self.questions for cid in q["conflict_ids"]}
        self.assertEqual(covered, self.conflict_ids)

    def test_expected_answers_match_reference_sql(self):
        conn = fixture.reference_connection()
        for q in self.questions:
            with self.subTest(q=q["id"]):
                rows = conn.execute(q["reference_sql"]).fetchall()
                if q["answer_type"] == "number":
                    self.assertEqual(len(rows), 1)
                    self.assertEqual(len(rows[0]), 1)
                    self.assertEqual(round(float(rows[0][0]), 2), round(float(q["expected"]), 2))
                else:
                    self.assertEqual(
                        {str(r[0]) for r in rows}, {str(v) for v in q["expected"]}
                    )

    def test_ground_truth_doc_lists_every_question_and_number(self):
        doc = (FIXTURE_DIR / "GROUND_TRUTH.md").read_text()
        for q in self.questions:
            with self.subTest(q=q["id"]):
                self.assertIn(q["id"], doc)
                if q["answer_type"] == "number":
                    self.assertIn(f"{float(q['expected']):.2f}", doc)


class DeterminismTests(unittest.TestCase):
    def test_reference_connection_is_reproducible(self):
        q = fixture.load_questions()
        first = [fixture.reference_connection().execute(x["reference_sql"]).fetchall() for x in q]
        second = [fixture.reference_connection().execute(x["reference_sql"]).fetchall() for x in q]
        self.assertEqual(
            [sorted(map(repr, r)) for r in first], [sorted(map(repr, r)) for r in second]
        )

    @unittest.skipUnless(importlib.util.find_spec("duckdb"), "duckdb not installed")
    def test_build_duckdb_is_deterministic_and_holds_source_b(self):
        import duckdb

        with tempfile.TemporaryDirectory() as tmp:
            dumps = []
            for name in ("one.duckdb", "two.duckdb"):
                path = fixture.build_duckdb(Path(tmp) / name)
                con = duckdb.connect(str(path), read_only=True)
                dump = {}
                for table in fixture.table_names()["B"]:
                    rows = con.execute(f'SELECT * FROM "{table}"').fetchall()
                    self.assertEqual(len(rows), len(csv_rows("B", table)))
                    dump[table] = sorted(map(repr, rows))
                con.close()
                dumps.append(dump)
            self.assertEqual(dumps[0], dumps[1])


class RawSchemaTests(unittest.TestCase):
    """S4 raw arm gets the raw schema only: tables and columns, no semantics."""

    def test_raw_schema_names_every_table_and_carries_no_comments(self):
        text = fixture.raw_schema_text()
        for names in fixture.table_names().values():
            for table in names:
                self.assertIn(table, text)
        self.assertNotIn("--", text)
        self.assertNotIn("/*", text)

    def test_raw_schema_leaks_no_ground_truth(self):
        text = fixture.raw_schema_text().lower()
        for c in fixture.load_checklist():
            if c["id"] == "location_identity":
                for entry in c["ground_truth"]["mapping"]:
                    # Location names/codes are data, not schema.
                    self.assertNotIn(entry["name"].lower(), text)
        for phrase in ("excludes returns", "includes returns", "ground truth", "maps to"):
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
