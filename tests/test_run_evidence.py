"""Committed run evidence matches the spec contract.

Spec: .openspec/specs/auto-ontology-enterprise-eval/spec.md

The other test files check the harness offline with fakes. This file checks
the artifacts the executed GitHub Actions run committed under runs/eval/.
Every number in RESULTS.md has to trace back to one of those files, so these
tests recompute what can be recomputed (scores, totals, delta, timing,
checklist marks, ground truths) from the raw artifacts and the fixture, and
compare.

Mapping:
- Requirements (pins, same model and settings in both arms, key never
  committed, fail closed)    -> EnvironmentAndPinsTests, StepsTests, NoKeyInRunEvidenceTests
- S1 smoke evidence          -> SmokeEvidenceTests
- S3 reconciliation, timing  -> ReconciliationEvidenceTests, TimingEvidenceTests
- S4 ablation                -> AblationEvidenceTests
- S5 RESULTS.md, limits      -> ResultsMarkdownEvidenceTests, EquivalentsEvidenceTests

If runs/eval/ is absent, every test here fails rather than skips. The
spec's Done condition requires committed run evidence.
"""
from __future__ import annotations

import json
import re
import unittest

from tests._support import (
    CHAT_MODEL,
    EMBEDDING_MODEL,
    RERANK_MODEL,
    REQUIRED_CONFLICT_IDS,
    ROOT,
    UPSTREAM_COMMIT,
    read_all_text,
)

from auto_ontology_eval import ablation, fixture, reconcile, timing

RUN_DIR = ROOT / "runs" / "eval"
RESULTS = RUN_DIR / "RESULTS.md"
PIPELINE_STEPS = ("preflight", "s2_fixture", "s1_smoke", "s3_generate", "s4_ablation")


def load(rel: str):
    path = RUN_DIR / rel
    if not path.is_file():
        raise AssertionError(f"run artifact missing: runs/eval/{rel}")
    return json.loads(path.read_text(encoding="utf-8"))


def results_text() -> str:
    if not RESULTS.is_file():
        raise AssertionError("runs/eval/RESULTS.md missing")
    return RESULTS.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    """Body of a level-2 section, up to the next level-2 heading."""
    m = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        raise AssertionError(f"RESULTS.md has no '## {heading}' section")
    return m.group(1)


class EvidenceDirectoryTests(unittest.TestCase):
    def test_run_directory_and_results_are_committed(self):
        self.assertTrue(RUN_DIR.is_dir(), "runs/eval/ is missing: no executed run is committed")
        self.assertTrue(RESULTS.is_file(), "runs/eval/RESULTS.md is missing")


class EnvironmentAndPinsTests(unittest.TestCase):
    """Requirements: pinned commit and models; S5 environment."""

    def test_environment_records_the_spec_pins(self):
        env = load("environment.json")
        self.assertEqual(env["upstream_commit"], UPSTREAM_COMMIT)
        self.assertEqual(env["upstream_repo"], "https://github.com/NVIDIA/auto-ontology.git")
        self.assertEqual(env["chat_model"], CHAT_MODEL)
        self.assertEqual(env["embedding_model"], EMBEDDING_MODEL)
        self.assertEqual(env["rerank_model"], RERANK_MODEL)

    def test_environment_proves_a_github_actions_run(self):
        env = load("environment.json")
        self.assertRegex(str(env.get("github_run_id", "")), r"^\d+$")
        self.assertIn("GitHub Actions", env.get("runner", ""))
        self.assertTrue(env.get("run_date"))

    def test_both_arms_used_the_pinned_model_and_recorded_settings(self):
        gen = load("generation_settings.json")
        self.assertEqual(gen["model"], CHAT_MODEL)
        for key in ablation.REQUIRED_SETTINGS:
            self.assertIn(key, gen["settings"])


class StepsTests(unittest.TestCase):
    """Fail closed: a committed run either completed every step with its
    evidence file, or records the failed step. This run claims completion."""

    def test_every_pipeline_step_ran_and_passed_in_order(self):
        steps = load("steps.json")
        self.assertEqual([s["step"] for s in steps], list(PIPELINE_STEPS))
        for s in steps:
            with self.subTest(step=s["step"]):
                self.assertIs(s["ok"], True)

    def test_every_step_evidence_file_exists(self):
        for s in load("steps.json"):
            with self.subTest(step=s["step"]):
                hits = list(RUN_DIR.rglob(s["evidence"]))
                self.assertTrue(hits, f"evidence {s['evidence']} for {s['step']} not in runs/eval")

    def test_completed_run_has_no_failure_record(self):
        self.assertFalse((RUN_DIR / "failure.json").exists())


class SmokeEvidenceTests(unittest.TestCase):
    """S1: health, catalog and MCP probe each passed and left a non-empty file."""

    def test_three_smoke_checks_passed_with_evidence(self):
        smoke = load("smoke/smoke.json")
        self.assertEqual(set(smoke), {"health", "catalog", "mcp"})
        for name, check in smoke.items():
            with self.subTest(check=name):
                self.assertIs(check["ok"], True)
                path = RUN_DIR / "smoke" / check["evidence"]
                self.assertTrue(path.is_file(), f"missing smoke/{check['evidence']}")
                self.assertTrue(path.read_text(encoding="utf-8").strip())


class ReconciliationEvidenceTests(unittest.TestCase):
    """S3: one mark per planted conflict, quotes verbatim from the export."""

    def setUp(self):
        self.catalog_path = RUN_DIR / "catalog.yaml"
        self.assertTrue(self.catalog_path.is_file(), "runs/eval/catalog.yaml missing")
        self.catalog = self.catalog_path.read_text(encoding="utf-8")
        self.marks = load("reconciliation.json")
        self.checklist = fixture.load_checklist()

    def test_catalog_export_is_not_empty(self):
        self.assertTrue(self.catalog.strip())

    def test_exactly_one_valid_mark_per_checklist_conflict(self):
        ids = [m["conflict_id"] for m in self.marks]
        self.assertEqual(sorted(ids), sorted(c["id"] for c in self.checklist))
        self.assertTrue(REQUIRED_CONFLICT_IDS <= set(ids))
        for m in self.marks:
            with self.subTest(conflict=m["conflict_id"]):
                self.assertIn(m["mark"], reconcile.MARKS)

    def test_counted_flag_is_true_only_for_verbatim_quotes(self):
        for m in self.marks:
            with self.subTest(conflict=m["conflict_id"]):
                verbatim = bool(m["quote"].strip()) and m["quote"] in self.catalog
                self.assertEqual(m["counted"], verbatim)

    def test_rescoring_the_committed_marks_reproduces_the_file(self):
        raw_marks = [{k: m[k] for k in ("conflict_id", "mark", "quote")} for m in self.marks]
        self.assertEqual(reconcile.score(self.checklist, self.catalog, raw_marks), self.marks)

    def test_classifier_is_reproducible_on_the_committed_catalog(self):
        expected = [{k: m[k] for k in ("conflict_id", "mark", "quote")} for m in self.marks]
        self.assertEqual(reconcile.classify(self.checklist, self.catalog), expected)


class TimingEvidenceTests(unittest.TestCase):
    """S3: time to first ontology comes from run timestamps."""

    def test_recorded_seconds_recompute_from_events(self):
        events = load("events.json")
        recorded = load("timing.json")
        self.assertAlmostEqual(
            timing.time_to_first_ontology(events), recorded["seconds"], places=2
        )

    def test_start_and_end_are_event_timestamps(self):
        events = load("events.json")
        recorded = load("timing.json")
        stamps = {e["at"] for e in events}
        self.assertIn(recorded["start"], stamps)
        self.assertIn(recorded["end"], stamps)
        self.assertGreater(recorded["seconds"], 0)


class AblationEvidenceTests(unittest.TestCase):
    """S4: 12 questions, ground truth from reference SQL, exact scoring,
    per-arm totals and delta, provenance per ontology answer, verbatim SQL."""

    def setUp(self):
        self.data = load("ablation.json")
        self.rows = self.data["questions"]
        self.fixture_qs = {q["id"]: q for q in fixture.load_questions()}

    def test_twelve_questions_matching_the_fixture(self):
        self.assertEqual(len(self.rows), 12)
        self.assertEqual({r["id"] for r in self.rows}, set(self.fixture_qs))
        for r in self.rows:
            with self.subTest(q=r["id"]):
                self.assertEqual(r["expected"], self.fixture_qs[r["id"]]["expected"])
                self.assertEqual(r["answer_type"], self.fixture_qs[r["id"]]["answer_type"])

    def test_every_planted_conflict_is_touched_by_a_question(self):
        touched = {c for r in self.rows for c in r["conflict_ids"]}
        self.assertTrue(REQUIRED_CONFLICT_IDS <= touched)

    def test_committed_ground_truth_recomputes_from_reference_sql(self):
        conn = fixture.reference_connection()
        for gt in load("ground_truth.json"):
            with self.subTest(q=gt["id"]):
                rows = conn.execute(gt["reference_sql"]).fetchall()
                if gt["answer_type"] == "number":
                    got = rows[0][0]
                else:
                    got = [r[0] for r in rows]
                self.assertTrue(ablation.score_answer(got, gt["expected"], gt["answer_type"]))
                self.assertEqual(gt["expected"], self.fixture_qs[gt["id"]]["expected"])

    def test_correct_flags_rescore_from_recorded_values(self):
        for r in self.rows:
            for arm in ("ontology", "raw"):
                with self.subTest(q=r["id"], arm=arm):
                    self.assertEqual(
                        r[arm]["correct"],
                        ablation.score_answer(r[arm]["value"], r["expected"], r["answer_type"]),
                    )

    def test_summary_totals_and_delta_recompute(self):
        onto = sum(r["ontology"]["correct"] for r in self.rows)
        raw = sum(r["raw"]["correct"] for r in self.rows)
        self.assertEqual(
            self.data["summary"],
            {"total": 12, "ontology_correct": onto, "raw_correct": raw, "delta": onto - raw},
        )

    def test_every_ontology_answer_records_a_provenance_flag(self):
        for r in self.rows:
            with self.subTest(q=r["id"]):
                self.assertIsInstance(r["ontology"]["provenance"], bool)
                self.assertEqual(
                    r["ontology"]["provenance"],
                    ablation.has_provenance(r["ontology"].get("provenance_detail")),
                )

    def test_raw_responses_and_ontology_events_are_saved_per_question(self):
        for r in self.rows:
            with self.subTest(q=r["id"]):
                self.assertTrue((RUN_DIR / "s4" / f"{r['id']}.raw.response.json").is_file())
                self.assertTrue((RUN_DIR / "s4" / f"{r['id']}.ontology.events.json").is_file())

    def test_raw_arm_sql_is_verbatim_from_the_model_response(self):
        for r in self.rows:
            with self.subTest(q=r["id"]):
                body = json.loads(
                    (RUN_DIR / "s4" / f"{r['id']}.raw.response.json").read_text(encoding="utf-8")
                )
                content = body["choices"][0]["message"].get("content")
                if r["raw"]["sql"] is None:
                    continue
                self.assertIsNotNone(content)
                self.assertEqual(r["raw"]["sql"], json.loads(content)["sql"])

    def test_ontology_sql_when_present_appears_in_the_event_stream(self):
        for r in self.rows:
            sql = r["ontology"]["sql"]
            if not sql:
                continue
            with self.subTest(q=r["id"]):
                events = (RUN_DIR / "s4" / f"{r['id']}.ontology.events.json").read_text(
                    encoding="utf-8"
                )
                self.assertIn(json.dumps(sql)[1:-1], events)

    def test_ontology_no_answer_keeps_the_upstream_reason(self):
        # A missing answer is scored incorrect, but the evidence must show
        # why: an error or the upstream response text, never a silent blank.
        for r in self.rows:
            o = r["ontology"]
            if o["value"] is not None:
                continue
            with self.subTest(q=r["id"]):
                self.assertTrue(o.get("error") or o.get("response"))


class ResultsMarkdownEvidenceTests(unittest.TestCase):
    """S5: RESULTS.md says only what the artifacts say."""

    def setUp(self):
        self.text = results_text()

    def test_sections_present_in_order(self):
        headings = re.findall(r"^## (.+)$", self.text, re.M)
        wanted = [
            "Environment",
            "Time to first ontology",
            "Reconciliation checklist",
            "Per-question results",
            "Failure gallery",
            "Limits",
        ]
        self.assertEqual([h for h in headings if h in wanted], wanted)

    def test_environment_values_come_from_environment_json(self):
        body = section(self.text, "Environment")
        for key, value in load("environment.json").items():
            with self.subTest(field=key):
                self.assertIn(str(value), body)

    def test_time_to_first_ontology_matches_timing_json(self):
        body = section(self.text, "Time to first ontology")
        t = load("timing.json")
        self.assertIn(f"{t['seconds']} s", body)
        self.assertIn(t["start"], body)
        self.assertIn(t["end"], body)

    def test_every_mark_and_quote_is_reported(self):
        body = section(self.text, "Reconciliation checklist")
        for m in load("reconciliation.json"):
            with self.subTest(conflict=m["conflict_id"]):
                self.assertIn(f"### {m['conflict_id']}: {m['mark']}", body)
                if m["quote"]:
                    self.assertIn(m["quote"], body)

    def test_per_question_table_matches_ablation_json(self):
        body = section(self.text, "Per-question results")
        rows = {}
        for line in body.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and re.fullmatch(r"Q\d\d", cells[0]):
                rows[cells[0]] = cells
        data = load("ablation.json")
        self.assertEqual(set(rows), {r["id"] for r in data["questions"]})
        yes = {True: "yes", False: "no"}
        for r in data["questions"]:
            cells = rows[r["id"]]
            with self.subTest(q=r["id"]):
                self.assertEqual(cells[3], yes[r["ontology"]["correct"]])
                self.assertEqual(cells[4], yes[r["ontology"]["provenance"]])
                self.assertEqual(cells[6], yes[r["raw"]["correct"]])
        s = data["summary"]
        self.assertIn(f"Auto Ontology arm: {s['ontology_correct']} / {s['total']} correct", body)
        self.assertIn(f"Raw-schema arm: {s['raw_correct']} / {s['total']} correct", body)
        self.assertIn(f"Delta (Auto Ontology minus raw schema): {s['delta']}", body)

    def test_failure_gallery_has_every_wrong_answer_and_its_sql_verbatim(self):
        body = section(self.text, "Failure gallery")
        labels = {"ontology": "Auto Ontology arm", "raw": "raw-schema arm"}
        for r in load("ablation.json")["questions"]:
            for arm, label in labels.items():
                if r[arm]["correct"]:
                    continue
                with self.subTest(q=r["id"], arm=arm):
                    self.assertIn(f"### {r['id']}, {label}", body)
                    if r[arm]["sql"]:
                        self.assertIn(r[arm]["sql"], body)

    def test_failure_gallery_has_no_correct_answers(self):
        body = section(self.text, "Failure gallery")
        labels = {"ontology": "Auto Ontology arm", "raw": "raw-schema arm"}
        for r in load("ablation.json")["questions"]:
            for arm, label in labels.items():
                if r[arm]["correct"]:
                    with self.subTest(q=r["id"], arm=arm):
                        self.assertNotIn(f"### {r['id']}, {label}\n", body)


class EquivalentsEvidenceTests(unittest.TestCase):
    """S5 limits: the two known equivalents were recorded by the live run
    itself and each is named in the limits section with its reason."""

    def setUp(self):
        self.entries = load("equivalents.json")

    def test_entries_have_all_fields(self):
        for e in self.entries:
            with self.subTest(scenario=e.get("scenario")):
                for key in ("scenario", "literal", "equivalent", "reason"):
                    self.assertTrue(str(e.get(key, "")).strip(), f"empty {key}")

    def test_both_known_equivalents_were_recorded_by_the_run(self):
        by_scenario = {e["scenario"]: e for e in self.entries}
        self.assertIn("S1", by_scenario)
        self.assertIn("in process", by_scenario["S1"]["equivalent"])
        self.assertIn("OAuth", by_scenario["S1"]["reason"])
        self.assertIn("S4", by_scenario)
        self.assertIn("copy of the fixture", by_scenario["S4"]["equivalent"])

    def test_limits_section_names_each_entry_with_its_reason(self):
        limits = section(results_text(), "Limits")
        for e in self.entries:
            with self.subTest(scenario=e["scenario"]):
                self.assertIn(e["equivalent"], limits)
                self.assertIn(e["literal"], limits)
                self.assertIn(e["reason"], limits)


class NoKeyInRunEvidenceTests(unittest.TestCase):
    """Requirements: the key never appears in committed run evidence."""

    REAL_KEY_PATTERN = re.compile(r"nvapi-[A-Za-z0-9_\-]{20,}")

    def test_no_key_literal_anywhere_under_runs(self):
        self.assertIsNone(self.REAL_KEY_PATTERN.search(read_all_text(ROOT / "runs")))

    def test_no_bearer_token_in_run_evidence(self):
        self.assertIsNone(
            re.search(r"Bearer\s+nvapi-", read_all_text(RUN_DIR)),
        )


if __name__ == "__main__":
    unittest.main()
