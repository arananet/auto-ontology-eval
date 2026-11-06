"""S3: generate the ontology and score the reconciliation.

Offline contract: every planted conflict gets exactly one mark among
detected / reconciled / ignored; a mark counts only when its quote appears
verbatim in the exported catalog; time to first ontology runs from both
sources registered to the first complete catalog export.
"""
import unittest

from auto_ontology_eval import errors, reconcile, timing

CHECKLIST = [
    {
        "id": "net_sales_semantics",
        "involves": [
            {"source": "A", "table": "fact_sales", "column": "net_sales"},
            {"source": "B", "table": "shipments", "column": "net_sales"},
        ],
        "ground_truth": {"source_a_total": 900.0, "source_b_total": 1000.0, "returns_total": 100.0},
    },
    {
        "id": "location_identity",
        "involves": [
            {"source": "A", "table": "dim_store", "column": "location_name"},
            {"source": "B", "table": "plants", "column": "plant_code"},
        ],
        "ground_truth": {"mapping": [{"code": "PL01", "kind": "plant", "name": "Lyon Works"}]},
    },
]

CATALOG_WITH_NET_SALES_CONFLICT = (
    "Entity: NetSales\n"
    "The net_sales column in fact_sales excludes returns, while net_sales in "
    "shipments includes returns; the two definitions conflict.\n"
)

CATALOG_SILENT = "Entity: Product\nA product sold by the company.\n"


class MarkVocabularyTests(unittest.TestCase):
    def test_marks(self):
        self.assertEqual(set(reconcile.MARKS), {"detected", "reconciled", "ignored"})


class ScoreTests(unittest.TestCase):
    def test_verbatim_quote_counts(self):
        quote = "net_sales in shipments includes returns"
        marks = [
            {"conflict_id": "net_sales_semantics", "mark": "detected", "quote": quote},
            {"conflict_id": "location_identity", "mark": "ignored", "quote": "Entity: NetSales"},
        ]
        scored = {r["conflict_id"]: r for r in reconcile.score(CHECKLIST, CATALOG_WITH_NET_SALES_CONFLICT, marks)}
        self.assertTrue(scored["net_sales_semantics"]["counted"])
        self.assertEqual(scored["net_sales_semantics"]["quote"], quote)
        self.assertEqual(scored["net_sales_semantics"]["mark"], "detected")

    def test_fabricated_or_paraphrased_quote_does_not_count(self):
        for quote in ("net sales in shipments include returns", "NET_SALES IN SHIPMENTS INCLUDES RETURNS"):
            with self.subTest(quote=quote):
                marks = [
                    {"conflict_id": "net_sales_semantics", "mark": "reconciled", "quote": quote},
                    {"conflict_id": "location_identity", "mark": "ignored", "quote": ""},
                ]
                scored = {r["conflict_id"]: r for r in reconcile.score(CHECKLIST, CATALOG_WITH_NET_SALES_CONFLICT, marks)}
                self.assertFalse(scored["net_sales_semantics"]["counted"])

    def test_mark_without_quote_does_not_count(self):
        for quote in ("", None, "   "):
            with self.subTest(quote=repr(quote)):
                marks = [
                    {"conflict_id": "net_sales_semantics", "mark": "detected", "quote": quote},
                    {"conflict_id": "location_identity", "mark": "ignored", "quote": quote},
                ]
                for r in reconcile.score(CHECKLIST, CATALOG_WITH_NET_SALES_CONFLICT, marks):
                    self.assertFalse(r["counted"])

    def test_every_conflict_needs_exactly_one_mark(self):
        missing = [{"conflict_id": "net_sales_semantics", "mark": "detected", "quote": "x"}]
        with self.assertRaises(ValueError):
            reconcile.score(CHECKLIST, CATALOG_SILENT, missing)
        doubled = missing + [
            {"conflict_id": "net_sales_semantics", "mark": "ignored", "quote": "x"},
            {"conflict_id": "location_identity", "mark": "ignored", "quote": "x"},
        ]
        with self.assertRaises(ValueError):
            reconcile.score(CHECKLIST, CATALOG_SILENT, doubled)

    def test_unknown_mark_rejected(self):
        marks = [
            {"conflict_id": "net_sales_semantics", "mark": "partially", "quote": "Entity"},
            {"conflict_id": "location_identity", "mark": "ignored", "quote": "Entity"},
        ]
        with self.assertRaises(ValueError):
            reconcile.score(CHECKLIST, CATALOG_SILENT, marks)

    def test_unknown_conflict_id_rejected(self):
        marks = [
            {"conflict_id": "net_sales_semantics", "mark": "ignored", "quote": "Entity"},
            {"conflict_id": "location_identity", "mark": "ignored", "quote": "Entity"},
            {"conflict_id": "made_up", "mark": "ignored", "quote": "Entity"},
        ]
        with self.assertRaises(ValueError):
            reconcile.score(CHECKLIST, CATALOG_SILENT, marks)


class ClassifyTests(unittest.TestCase):
    def test_one_mark_per_conflict_and_quotes_are_verbatim(self):
        for catalog in (CATALOG_WITH_NET_SALES_CONFLICT, CATALOG_SILENT):
            with self.subTest(catalog=catalog[:20]):
                marks = reconcile.classify(CHECKLIST, catalog)
                self.assertEqual(
                    sorted(m["conflict_id"] for m in marks),
                    sorted(c["id"] for c in CHECKLIST),
                )
                for m in marks:
                    self.assertIn(m["mark"], reconcile.MARKS)
                    if m.get("quote"):
                        self.assertIn(m["quote"], catalog)
                # Output must be accepted by score() unchanged.
                reconcile.score(CHECKLIST, catalog, marks)

    def test_silent_catalog_marks_everything_ignored(self):
        for m in reconcile.classify(CHECKLIST, CATALOG_SILENT):
            self.assertEqual(m["mark"], "ignored", m)

    def test_explicit_conflict_statement_is_not_ignored(self):
        marks = {m["conflict_id"]: m for m in reconcile.classify(CHECKLIST, CATALOG_WITH_NET_SALES_CONFLICT)}
        self.assertIn(marks["net_sales_semantics"]["mark"], ("detected", "reconciled"))
        self.assertTrue(marks["net_sales_semantics"]["quote"])

    def test_classify_is_deterministic(self):
        a = reconcile.classify(CHECKLIST, CATALOG_WITH_NET_SALES_CONFLICT)
        b = reconcile.classify(CHECKLIST, CATALOG_WITH_NET_SALES_CONFLICT)
        self.assertEqual(a, b)


class TimeToFirstOntologyTests(unittest.TestCase):
    def test_measured_from_second_registration_to_first_complete_export(self):
        events = [
            {"event": "source_registered", "source": "A", "at": "2026-11-05T10:00:00Z"},
            {"event": "catalog_exported", "complete": False, "at": "2026-11-05T10:00:30Z"},
            {"event": "source_registered", "source": "B", "at": "2026-11-05T10:00:05Z"},
            {"event": "catalog_exported", "complete": True, "at": "2026-11-05T10:01:05Z"},
            {"event": "catalog_exported", "complete": True, "at": "2026-11-05T10:05:00Z"},
        ]
        self.assertEqual(timing.time_to_first_ontology(events), 60.0)

    def test_export_before_both_registered_is_ignored(self):
        events = [
            {"event": "source_registered", "source": "A", "at": "2026-11-05T10:00:00Z"},
            {"event": "catalog_exported", "complete": True, "at": "2026-11-05T10:00:10Z"},
            {"event": "source_registered", "source": "B", "at": "2026-11-05T10:00:20Z"},
            {"event": "catalog_exported", "complete": True, "at": "2026-11-05T10:02:20Z"},
        ]
        self.assertEqual(timing.time_to_first_ontology(events), 120.0)

    def test_missing_evidence_fails_closed(self):
        only_one = [
            {"event": "source_registered", "source": "A", "at": "2026-11-05T10:00:00Z"},
            {"event": "catalog_exported", "complete": True, "at": "2026-11-05T10:01:00Z"},
        ]
        no_export = [
            {"event": "source_registered", "source": "A", "at": "2026-11-05T10:00:00Z"},
            {"event": "source_registered", "source": "B", "at": "2026-11-05T10:00:01Z"},
        ]
        for events in (only_one, no_export, []):
            with self.assertRaises(errors.StepFailed):
                timing.time_to_first_ontology(events)


if __name__ == "__main__":
    unittest.main()
