"""S4: ablation, answers with and without the ontology.

Offline contract with fake arms. An arm exposes:
    model: str
    settings: dict   (must include temperature and max_tokens)
    ask(question: dict) -> {"value": ..., "sql": str | None, "provenance": ... }

ablation.run(questions, ontology_arm, raw_arm, out_dir) writes:
    ground_truth.json        before any arm is asked
    generation_settings.json model + settings shared by both arms
    ablation.json            per-question rows and the summary/delta
"""
import json
import tempfile
import unittest
from pathlib import Path

from auto_ontology_eval import ablation

SETTINGS = {"temperature": 0.0, "max_tokens": 1024, "seed": 7}
MODEL = "nvidia/nemotron-3-nano-30b-a3b"

QUESTIONS = [
    {"id": "Q01", "question": "Total net sales in the sales mart?", "answer_type": "number",
     "expected": 900.0, "reference_sql": "SELECT 900.0", "conflict_ids": ["net_sales_semantics"]},
    {"id": "Q02", "question": "Which SKUs are in both marts?", "answer_type": "set",
     "expected": ["SKU-1", "SKU-2"], "reference_sql": "SELECT 'SKU-1'", "conflict_ids": ["shared_sku_identity"]},
    {"id": "Q03", "question": "Units shipped from plant PL01?", "answer_type": "number",
     "expected": 42, "reference_sql": "SELECT 42", "conflict_ids": ["location_identity"]},
]


class FakeArm:
    def __init__(self, answers, model=MODEL, settings=None, on_ask=None):
        self.answers = answers
        self.model = model
        self.settings = dict(SETTINGS if settings is None else settings)
        self.asked = []
        self.on_ask = on_ask

    def ask(self, question):
        if self.on_ask:
            self.on_ask(question)
        self.asked.append(question["id"])
        answer = self.answers[question["id"]]
        if isinstance(answer, Exception):
            raise answer
        return answer


class ScoreAnswerTests(unittest.TestCase):
    def test_numbers_equal_after_rounding_to_two_decimals(self):
        self.assertTrue(ablation.score_answer(900.004, 900.0, "number"))
        self.assertTrue(ablation.score_answer(42, 42.0, "number"))
        self.assertTrue(ablation.score_answer("900.00", 900, "number"))
        self.assertFalse(ablation.score_answer(900.006, 900.0, "number"))
        self.assertFalse(ablation.score_answer(1000.0, 900.0, "number"))

    def test_sets_equal_regardless_of_order(self):
        self.assertTrue(ablation.score_answer(["SKU-2", "SKU-1"], ["SKU-1", "SKU-2"], "set"))
        self.assertFalse(ablation.score_answer(["SKU-1"], ["SKU-1", "SKU-2"], "set"))
        self.assertFalse(ablation.score_answer(["SKU-1", "SKU-2", "SKU-3"], ["SKU-1", "SKU-2"], "set"))

    def test_no_answer_or_unparseable_is_incorrect(self):
        for value, kind in ((None, "number"), ("", "number"), ("about nine hundred", "number"),
                            (None, "set"), ([], "set")):
            with self.subTest(value=value, kind=kind):
                expected = 900.0 if kind == "number" else ["SKU-1"]
                self.assertFalse(ablation.score_answer(value, expected, kind))


class RunTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.out = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _arms(self):
        onto = FakeArm({
            "Q01": {"value": 900.0, "sql": "SELECT SUM(net_sales) FROM fact_sales",
                    "provenance": ["sales_mart.fact_sales.net_sales"]},
            "Q02": {"value": ["SKU-1", "SKU-2"], "sql": "SELECT sku FROM a INTERSECT SELECT sku FROM b",
                    "provenance": None},
            "Q03": {"value": 40, "sql": "SELECT SUM(units) FROM shipments WHERE plant='Lyon'",
                    "provenance": []},
        })
        raw = FakeArm({
            "Q01": {"value": 1000.0, "sql": "SELECT SUM(net_sales) FROM shipments"},
            "Q02": {"value": ["SKU-1"], "sql": "SELECT DISTINCT sku FROM fact_sales LIMIT 1"},
            "Q03": RuntimeError("HTTP 500"),
        })
        return onto, raw

    def test_scores_both_arms_and_records_delta(self):
        onto, raw = self._arms()
        summary = ablation.run(QUESTIONS, onto, raw, self.out)
        self.assertEqual(onto.asked, ["Q01", "Q02", "Q03"])
        self.assertEqual(raw.asked, ["Q01", "Q02", "Q03"])
        data = json.loads((self.out / "ablation.json").read_text())
        rows = {r["id"]: r for r in data["questions"]}
        self.assertEqual([r["id"] for r in data["questions"]], ["Q01", "Q02", "Q03"])
        self.assertTrue(rows["Q01"]["ontology"]["correct"])
        self.assertTrue(rows["Q02"]["ontology"]["correct"])
        self.assertFalse(rows["Q03"]["ontology"]["correct"])
        self.assertFalse(rows["Q01"]["raw"]["correct"])
        self.assertFalse(rows["Q02"]["raw"]["correct"])
        self.assertFalse(rows["Q03"]["raw"]["correct"])
        expected_summary = {"total": 3, "ontology_correct": 2, "raw_correct": 0, "delta": 2}
        for key, value in expected_summary.items():
            self.assertEqual(data["summary"][key], value)
            self.assertEqual(summary[key], value)

    def test_generated_sql_saved_verbatim(self):
        onto, raw = self._arms()
        ablation.run(QUESTIONS, onto, raw, self.out)
        rows = {r["id"]: r for r in json.loads((self.out / "ablation.json").read_text())["questions"]}
        self.assertEqual(rows["Q03"]["ontology"]["sql"], "SELECT SUM(units) FROM shipments WHERE plant='Lyon'")
        self.assertEqual(rows["Q02"]["raw"]["sql"], "SELECT DISTINCT sku FROM fact_sales LIMIT 1")

    def test_provenance_recorded_for_every_ontology_answer(self):
        onto, raw = self._arms()
        ablation.run(QUESTIONS, onto, raw, self.out)
        rows = {r["id"]: r for r in json.loads((self.out / "ablation.json").read_text())["questions"]}
        self.assertIs(rows["Q01"]["ontology"]["provenance"], True)
        self.assertIs(rows["Q02"]["ontology"]["provenance"], False)
        self.assertIs(rows["Q03"]["ontology"]["provenance"], False)

    def test_arm_error_is_recorded_as_no_answer(self):
        onto, raw = self._arms()
        ablation.run(QUESTIONS, onto, raw, self.out)
        rows = {r["id"]: r for r in json.loads((self.out / "ablation.json").read_text())["questions"]}
        self.assertIsNone(rows["Q03"]["raw"]["value"])
        self.assertFalse(rows["Q03"]["raw"]["correct"])
        self.assertIn("HTTP 500", rows["Q03"]["raw"]["error"])

    def test_ground_truth_written_before_any_model_call(self):
        seen = []

        def check(_question):
            seen.append((self.out / "ground_truth.json").is_file())

        onto, raw = self._arms()
        onto.on_ask = check
        raw.on_ask = check
        ablation.run(QUESTIONS, onto, raw, self.out)
        self.assertTrue(seen and all(seen))
        gt = json.loads((self.out / "ground_truth.json").read_text())
        gt_by_id = {g["id"]: g["expected"] for g in gt}
        self.assertEqual(gt_by_id, {q["id"]: q["expected"] for q in QUESTIONS})

    def test_same_model_and_settings_required_and_recorded(self):
        onto, raw = self._arms()
        ablation.run(QUESTIONS, onto, raw, self.out)
        recorded = json.loads((self.out / "generation_settings.json").read_text())
        self.assertEqual(recorded["model"], MODEL)
        self.assertEqual(recorded["settings"], SETTINGS)

    def test_mismatched_model_or_settings_refused_before_asking(self):
        cases = [
            FakeArm({}, model="some/other-model"),
            FakeArm({}, settings={**SETTINGS, "temperature": 0.7}),
            FakeArm({}, settings={**SETTINGS, "max_tokens": 64}),
        ]
        for raw in cases:
            with self.subTest(model=raw.model, settings=raw.settings):
                onto, _ = self._arms()
                with self.assertRaises(ValueError):
                    ablation.run(QUESTIONS, onto, raw, self.out)
                self.assertEqual(onto.asked, [])
                self.assertEqual(raw.asked, [])

    def test_settings_must_include_temperature_and_max_tokens(self):
        for missing in ("temperature", "max_tokens"):
            with self.subTest(missing=missing):
                settings = {k: v for k, v in SETTINGS.items() if k != missing}
                onto = FakeArm({}, settings=settings)
                raw = FakeArm({}, settings=settings)
                with self.assertRaises(ValueError):
                    ablation.run(QUESTIONS, onto, raw, self.out)


class RawArmPromptTests(unittest.TestCase):
    def test_raw_prompt_holds_question_and_schema_only(self):
        schema = "CREATE TABLE fact_sales (sku TEXT, net_sales NUMERIC);"
        prompt = ablation.raw_schema_prompt("Total net sales?", schema)
        self.assertIn("Total net sales?", prompt)
        self.assertIn(schema, prompt)
        for leak in ("excludes returns", "includes returns", "ground_truth"):
            self.assertNotIn(leak, prompt.lower())


if __name__ == "__main__":
    unittest.main()
