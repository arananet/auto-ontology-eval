"""Spec Amendment 3: the live-internals configuration.

Offline checks: the ontology only S4 run, the catalog description
coverage counter (including its counts on the committed frozen default
catalog), and RESULTS-LIVE.md citing the standing control and the
default configuration figures from the frozen runs/eval artifacts.
"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tests._support import CHAT_MODEL, ROOT

from auto_ontology_eval import ablation, results

FROZEN = ROOT / "runs" / "eval"


class FakeArm:
    model = CHAT_MODEL
    settings = {"temperature": 0.0, "max_tokens": 8192}

    def __init__(self, answers):
        self.answers = answers

    def ask(self, question):
        return self.answers[question["id"]]


QUESTIONS = [
    {"id": "Q01", "question": "q1", "answer_type": "number", "expected": 2.0,
     "reference_sql": "select 2", "conflict_ids": []},
    {"id": "Q02", "question": "q2", "answer_type": "number", "expected": 3.0,
     "reference_sql": "select 3", "conflict_ids": []},
]


class OntologyOnlyAblation(unittest.TestCase):
    def test_writes_raw_rows_null_and_records_the_arm_note(self):
        arm = FakeArm({
            "Q01": {"value": 2.0, "sql": "select 2", "provenance": {"sources": ["catalog"]}},
            "Q02": {"value": None, "sql": None, "provenance": None},
        })
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            summary = ablation.run_ontology_only(QUESTIONS, arm, out)
            data = json.loads((out / "ablation.json").read_text())
            gen = json.loads((out / "generation_settings.json").read_text())
            truth = json.loads((out / "ground_truth.json").read_text())
        self.assertEqual(summary["ontology_correct"], 1)
        self.assertIsNone(summary["raw_correct"])
        self.assertIsNone(summary["delta"])
        self.assertIn("not rerun", summary["arms"])
        self.assertTrue(all(q["raw"] is None for q in data["questions"]))
        self.assertTrue(data["questions"][0]["ontology"]["provenance"])
        self.assertEqual(gen, {"model": CHAT_MODEL,
                               "settings": {"temperature": 0.0, "max_tokens": 8192}})
        self.assertEqual([t["id"] for t in truth], ["Q01", "Q02"])


class DescriptionCoverage(unittest.TestCase):
    def test_counts_authored_blank_and_template(self):
        catalog = "\n".join([
            "data_layer:",
            "  tables:",
            "    - name: t1",
            "      description: ''",
            "    - name: t2",
            "      description: Business entity represented by table t2",
            "    - name: t3",
            "      description: 'format: YYYY-MM-DD'",
            "    - name: t4",
            "      description: Sales orders as booked in the sales mart.",
            "other: description: not a field line start",
        ])
        self.assertEqual(results.description_coverage(catalog),
                         {"total": 4, "authored": 1, "blank": 1, "template": 2})

    def test_frozen_default_catalog_counts_match_the_diagnosis(self):
        text = (FROZEN / "catalog.yaml").read_text()
        self.assertEqual(results.description_coverage(text),
                         {"total": 88, "authored": 0, "blank": 77, "template": 11})


def _write(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2))
    return path


class LiveResults(unittest.TestCase):
    def test_cites_the_standing_control_and_default_figures(self):
        with tempfile.TemporaryDirectory() as d:
            runs = Path(d) / "runs"
            frozen = runs / "eval"
            live_dir = runs / "eval-live"
            for name in ("ablation.json", "environment.json", "timing.json",
                         "reconciliation.json", "generation_settings.json", "catalog.yaml"):
                frozen.mkdir(parents=True, exist_ok=True)
                shutil.copy(FROZEN / name, frozen / name)
            _write(live_dir / "environment.json",
                   {"runner": "test", "github_run_id": "999", "upstream_commit": "cdaf",
                    "chat_model": CHAT_MODEL, "configuration": "live-internals",
                    "run_date": "2026-11-05T00:00:00Z"})
            _write(live_dir / "timing.json", {"seconds": 42.5, "start": "a", "end": "b"})
            _write(live_dir / "generation_settings.json",
                   {"model": CHAT_MODEL, "settings": {"temperature": 0.0, "max_tokens": 8192}})
            _write(live_dir / "reconciliation.json",
                   [{"conflict_id": "net_sales_semantics", "mark": "reconciled",
                     "quote": "net_sales maps to gross sales", "counted": True}])
            questions = [
                {"id": f"Q{i:02d}", "expected": 1.0, "answer_type": "number",
                 "ontology": {"value": 1.0 if i <= 5 else None,
                              "sql": "select 1" if i <= 9 else None,
                              "correct": i <= 5, "provenance": i <= 4},
                 "raw": None}
                for i in range(1, 13)
            ]
            _write(live_dir / "ablation.json",
                   {"questions": questions,
                    "summary": {"total": 12, "ontology_correct": 5,
                                "raw_correct": None, "delta": None}})
            (live_dir / "catalog.yaml").write_text(
                "data_layer:\n  tables:\n    - name: t\n"
                "      description: A real authored definition.\n")
            out = live_dir / "RESULTS-LIVE.md"
            text = results.write_live_results(live_dir, out)
            written = out.read_text()
        self.assertEqual(text, written)
        self.assertIn("live-internals configuration", text)
        self.assertIn("Configuration: `live-internals`", text)
        self.assertIn("42.5 s from both sources registered", text)
        self.assertIn("Default configuration: 15.42 s (GitHub Actions run 42127124473", text)
        self.assertIn("1 authored, 0 blank, 0 template", text)
        self.assertIn("88 description fields: 0 authored, 77 blank, 11 template", text)
        self.assertIn("Auto Ontology arm: 5 / 12 correct", text)
        self.assertIn("Questions where the arm produced SQL: 9 / 12", text)
        self.assertIn("Default configuration Auto Ontology arm: 0 / 12 correct "
                      "(GitHub Actions run 42127124473", text)
        self.assertIn("Raw-schema control arm, not rerun (spec Amendment 3): 8 / 12 correct "
                      "(GitHub Actions run 42127124473", text)
        self.assertIn("Delta (live-internals Auto Ontology minus standing raw-schema control): -3", text)
        self.assertIn("Delta (live-internals minus default configuration, Auto Ontology arm): +5", text)


if __name__ == "__main__":
    unittest.main()
