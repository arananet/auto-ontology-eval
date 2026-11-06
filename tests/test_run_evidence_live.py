"""Committed live-internals run evidence matches spec Amendment 3.

Spec: .openspec/specs/auto-ontology-enterprise-eval/spec.md, Amendment 3.

test_s5_live_results.py and test_s1_model_pins.py check the live-internals
harness offline with fakes. This file checks the evidence the executed
GitHub Actions run of the live-internals configuration commits under
runs/eval-live/, the same way test_run_evidence.py checks runs/eval/. It
also checks that the default configuration evidence in runs/eval/ stayed
frozen.

Written before the live run exists. Until runs/eval-live/ is committed,
every test here fails rather than skips: the spec's Done condition needs
the committed run evidence.

Mapping (Amendment 3 clause -> test class):
- second configuration, one change only: every internal chat model slot
  set to the chat pin, verified in the running stack (S1)
                                -> LiveEnvironmentTests, LiveResolvedModelsTests
- identical stage structure and fail closed rule
                                -> LiveStepsTests, LiveSmokeTests
- same fixture, checklist and scorer (S3)
                                -> LiveReconciliationTests, LiveTimingTests
- S4 runs the Auto Ontology arm only, same model and settings as the
  standing control             -> LiveAblationTests
- RESULTS-LIVE.md from the live artifacts plus cited frozen figures,
  description coverage, control cited with its run id
                                -> LiveResultsMarkdownTests
- runs/eval/ and its RESULTS.md are frozen, never rerun or modified
                                -> FrozenDefaultTests
- the key never appears in committed evidence
                                -> LiveNoKeyTests
"""
from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path

from tests._support import (
    CHAT_MODEL,
    EMBEDDING_MODEL,
    RERANK_MODEL,
    REQUIRED_CONFLICT_IDS,
    ROOT,
    UPSTREAM_COMMIT,
    read_all_text,
)

from auto_ontology_eval import ablation, fixture, reconcile, results, timing, upstream

RUN_DIR = ROOT / "runs" / "eval-live"
RESULTS_LIVE = RUN_DIR / "RESULTS-LIVE.md"
FROZEN_DIR = ROOT / "runs" / "eval"
# The default configuration run named in spec Amendment 3.
FROZEN_RUN_ID = "42127124473"
FROZEN_SUMMARY = {"total": 12, "ontology_correct": 0, "raw_correct": 8, "delta": -8}
CONFIGURATION = "live-internals"
# Amendment 3: the complete internal chat model slot list of the pinned upstream.
INTERNAL_CHAT_SLOTS = ("DEFAULT_MODELS_MODEL", "REASONING_MODEL", "NON_REASONING_MODEL")
PIPELINE_STEPS = ("preflight", "s2_fixture", "s1_smoke", "s3_generate", "s4_ablation")
LIVE_SECTIONS = [
    "Environment",
    "Time to first ontology",
    "Catalog description coverage",
    "Reconciliation checklist",
    "Per-question results (Auto Ontology arm)",
    "Comparison with the default configuration and the standing control",
    "Failure gallery",
    "Limits",
]


def load(rel: str, base: Path | None = None):
    path = (RUN_DIR if base is None else base) / rel
    if not path.is_file():
        raise AssertionError(f"run artifact missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def results_text() -> str:
    if not RESULTS_LIVE.is_file():
        raise AssertionError("runs/eval-live/RESULTS-LIVE.md missing")
    return RESULTS_LIVE.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        raise AssertionError(f"RESULTS-LIVE.md has no '## {heading}' section")
    return m.group(1)


def live_catalog() -> str:
    path = RUN_DIR / "catalog.yaml"
    if not path.is_file():
        raise AssertionError("runs/eval-live/catalog.yaml missing")
    return path.read_text(encoding="utf-8")


class LiveEvidenceDirectoryTests(unittest.TestCase):
    def test_live_run_directory_and_results_are_committed(self):
        self.assertTrue(RUN_DIR.is_dir(), "runs/eval-live/ is missing: no live-internals run is committed")
        self.assertTrue(RESULTS_LIVE.is_file(), "runs/eval-live/RESULTS-LIVE.md is missing")

    def test_live_run_writes_results_live_not_results(self):
        # Amendment 3: the live configuration's document is RESULTS-LIVE.md.
        self.assertFalse((RUN_DIR / "RESULTS.md").exists())


class LiveEnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.env = load("environment.json")

    def test_environment_records_the_pins_and_the_configuration(self):
        self.assertEqual(self.env["configuration"], CONFIGURATION)
        self.assertEqual(self.env["upstream_commit"], UPSTREAM_COMMIT)
        self.assertEqual(self.env["upstream_repo"], "https://github.com/NVIDIA/auto-ontology.git")
        self.assertEqual(self.env["chat_model"], CHAT_MODEL)
        self.assertEqual(self.env["embedding_model"], EMBEDDING_MODEL)
        self.assertEqual(self.env["rerank_model"], RERANK_MODEL)

    def test_environment_proves_its_own_github_actions_run(self):
        run_id = str(self.env.get("github_run_id", ""))
        self.assertRegex(run_id, r"^\d+$")
        self.assertNotEqual(run_id, FROZEN_RUN_ID, "live evidence reuses the default run id")
        self.assertIn("GitHub Actions", self.env.get("runner", ""))
        self.assertTrue(self.env.get("run_date"))


class LiveResolvedModelsTests(unittest.TestCase):
    """Amendment 3, S1: the running stack resolved every wired slot to the pin."""

    def setUp(self):
        self.models = load("smoke/models.json")

    def test_every_internal_chat_slot_resolved_to_the_chat_pin(self):
        for slot in INTERNAL_CHAT_SLOTS:
            with self.subTest(slot=slot):
                self.assertEqual(self.models.get(slot), CHAT_MODEL)

    def test_embedding_and_rerank_pins_unchanged(self):
        self.assertEqual(self.models.get("EMBED_MODEL"), EMBEDDING_MODEL)
        self.assertEqual(self.models.get("RERANK_MODEL"), RERANK_MODEL)

    def test_recorded_models_pass_the_harness_verification(self):
        expected = upstream.model_env(CONFIGURATION)
        self.assertEqual({k: self.models.get(k) for k in expected}, expected)
        upstream.verify_resolved_models(json.dumps(self.models), CONFIGURATION)


class LiveStepsTests(unittest.TestCase):
    """Same stage structure and fail closed rule as the default configuration."""

    def test_every_pipeline_step_ran_and_passed_in_order(self):
        steps = load("steps.json")
        self.assertEqual([s["step"] for s in steps], list(PIPELINE_STEPS))
        for s in steps:
            with self.subTest(step=s["step"]):
                self.assertIs(s["ok"], True)

    def test_every_step_evidence_file_exists(self):
        for s in load("steps.json"):
            with self.subTest(step=s["step"]):
                self.assertTrue(list(RUN_DIR.rglob(s["evidence"])),
                                f"evidence {s['evidence']} for {s['step']} not in runs/eval-live")

    def test_completed_run_has_no_failure_record(self):
        self.assertFalse((RUN_DIR / "failure.json").exists())


class LiveSmokeTests(unittest.TestCase):
    def test_three_smoke_checks_passed_with_evidence(self):
        smoke = load("smoke/smoke.json")
        self.assertEqual(set(smoke), {"health", "catalog", "mcp"})
        for name, check in smoke.items():
            with self.subTest(check=name):
                self.assertIs(check["ok"], True)
                path = RUN_DIR / "smoke" / check["evidence"]
                self.assertTrue(path.is_file(), f"missing smoke/{check['evidence']}")
                self.assertTrue(path.read_text(encoding="utf-8").strip())


class LiveReconciliationTests(unittest.TestCase):
    """Same checklist and scorer as the default configuration (S3)."""

    def setUp(self):
        self.catalog = live_catalog()
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

    def test_rescoring_and_reclassifying_reproduce_the_file(self):
        raw = [{k: m[k] for k in ("conflict_id", "mark", "quote")} for m in self.marks]
        self.assertEqual(reconcile.score(self.checklist, self.catalog, raw), self.marks)
        self.assertEqual(reconcile.classify(self.checklist, self.catalog), raw)


class LiveTimingTests(unittest.TestCase):
    def test_recorded_seconds_recompute_from_events(self):
        events = load("events.json")
        recorded = load("timing.json")
        self.assertAlmostEqual(timing.time_to_first_ontology(events), recorded["seconds"], places=2)
        stamps = {e["at"] for e in events}
        self.assertIn(recorded["start"], stamps)
        self.assertIn(recorded["end"], stamps)
        self.assertGreater(recorded["seconds"], 0)


class LiveAblationTests(unittest.TestCase):
    """Amendment 3, S4: the Auto Ontology arm only, scored exactly as before."""

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

    def test_committed_ground_truth_recomputes_from_reference_sql(self):
        conn = fixture.reference_connection()
        for gt in load("ground_truth.json"):
            with self.subTest(q=gt["id"]):
                rows = conn.execute(gt["reference_sql"]).fetchall()
                got = rows[0][0] if gt["answer_type"] == "number" else [r[0] for r in rows]
                self.assertTrue(ablation.score_answer(got, gt["expected"], gt["answer_type"]))
                self.assertEqual(gt["expected"], self.fixture_qs[gt["id"]]["expected"])

    def test_raw_arm_was_not_rerun(self):
        for r in self.rows:
            with self.subTest(q=r["id"]):
                self.assertIsNone(r["raw"])
                self.assertFalse((RUN_DIR / "s4" / f"{r['id']}.raw.response.json").exists())

    def test_correct_flags_rescore_from_recorded_values(self):
        for r in self.rows:
            with self.subTest(q=r["id"]):
                o = r["ontology"]
                self.assertEqual(o["correct"],
                                 ablation.score_answer(o["value"], r["expected"], r["answer_type"]))

    def test_summary_recomputes_with_null_raw_and_delta(self):
        onto = sum(r["ontology"]["correct"] for r in self.rows)
        s = self.data["summary"]
        self.assertEqual(s["total"], 12)
        self.assertEqual(s["ontology_correct"], onto)
        self.assertIsNone(s["raw_correct"])
        self.assertIsNone(s["delta"])

    def test_same_model_and_settings_as_the_standing_control(self):
        live = load("generation_settings.json")
        frozen = load("generation_settings.json", FROZEN_DIR)
        self.assertEqual(live["model"], CHAT_MODEL)
        self.assertEqual(live, frozen)
        for key in ablation.REQUIRED_SETTINGS:
            self.assertIn(key, live["settings"])

    def test_every_ontology_answer_records_a_provenance_flag(self):
        for r in self.rows:
            with self.subTest(q=r["id"]):
                self.assertIsInstance(r["ontology"]["provenance"], bool)
                self.assertEqual(r["ontology"]["provenance"],
                                 ablation.has_provenance(r["ontology"].get("provenance_detail")))

    def test_ontology_events_saved_and_sql_verbatim_in_them(self):
        for r in self.rows:
            with self.subTest(q=r["id"]):
                path = RUN_DIR / "s4" / f"{r['id']}.ontology.events.json"
                self.assertTrue(path.is_file())
                sql = r["ontology"]["sql"]
                if sql:
                    self.assertIn(json.dumps(sql)[1:-1], path.read_text(encoding="utf-8"))

    def test_ontology_no_answer_keeps_the_upstream_reason(self):
        for r in self.rows:
            o = r["ontology"]
            if o["value"] is None:
                with self.subTest(q=r["id"]):
                    self.assertTrue(o.get("error") or o.get("response"))


class LiveResultsMarkdownTests(unittest.TestCase):
    """RESULTS-LIVE.md says only what the live artifacts and the cited
    frozen artifacts say."""

    def setUp(self):
        self.text = results_text()

    def test_document_regenerates_from_the_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            regenerated = results.write_live_results(RUN_DIR, Path(d) / "RESULTS-LIVE.md")
        self.assertEqual(regenerated, self.text)

    def test_sections_present_in_order(self):
        headings = re.findall(r"^## (.+)$", self.text, re.M)
        self.assertEqual([h for h in headings if h in LIVE_SECTIONS], LIVE_SECTIONS)

    def test_no_run_stopped_banner(self):
        self.assertNotIn("**Run stopped**", self.text)

    def test_environment_names_configuration_and_resolved_slots(self):
        body = section(self.text, "Environment")
        for key, value in load("environment.json").items():
            with self.subTest(field=key):
                self.assertIn(str(value), body)
        self.assertIn(f"Configuration: `{CONFIGURATION}`", body)
        for slot in INTERNAL_CHAT_SLOTS:
            with self.subTest(slot=slot):
                self.assertIn(f"- {slot}: `{CHAT_MODEL}`", body)

    def test_timing_reports_live_and_cites_default(self):
        body = section(self.text, "Time to first ontology")
        t = load("timing.json")
        self.assertIn(f"{t['seconds']} s", body)
        d = load("timing.json", FROZEN_DIR)
        self.assertIn(f"Default configuration: {d['seconds']} s (GitHub Actions run {FROZEN_RUN_ID}", body)

    def test_description_coverage_recomputes_for_both_catalogs(self):
        body = section(self.text, "Catalog description coverage")
        live = results.description_coverage(live_catalog())
        self.assertIn(f"Live-internals catalog: {live['total']} description fields: "
                      f"{live['authored']} authored, {live['blank']} blank, "
                      f"{live['template']} template.", body)
        self.assertIn("88 description fields: 0 authored, 77 blank, 11 template.", body)

    def test_every_live_mark_and_quote_is_reported(self):
        body = section(self.text, "Reconciliation checklist")
        for m in load("reconciliation.json"):
            with self.subTest(conflict=m["conflict_id"]):
                self.assertIn(f"### {m['conflict_id']}: {m['mark']}", body)
                if m["quote"]:
                    self.assertIn(m["quote"], body)

    def test_comparison_cites_control_and_default_with_their_run_id(self):
        body = section(self.text, "Comparison with the default configuration and the standing control")
        s = load("ablation.json")["summary"]
        env = load("environment.json")
        self.assertIn(f"Live-internals Auto Ontology arm: {s['ontology_correct']} / 12 correct "
                      f"(this run, GitHub Actions run {env['github_run_id']})", body)
        self.assertIn(f"Default configuration Auto Ontology arm: 0 / 12 correct "
                      f"(GitHub Actions run {FROZEN_RUN_ID}", body)
        self.assertIn(f"Raw-schema control arm, not rerun (spec Amendment 3): 8 / 12 correct "
                      f"(GitHub Actions run {FROZEN_RUN_ID}", body)
        self.assertIn("Delta (live-internals Auto Ontology minus standing raw-schema control): "
                      f"{s['ontology_correct'] - 8:+d}", body)
        self.assertIn("Delta (live-internals minus default configuration, Auto Ontology arm): "
                      f"{s['ontology_correct'] - 0:+d}", body)
        self.assertIn("the standing control is comparable on model and settings", body)

    def test_failure_gallery_has_every_wrong_answer_and_its_sql_verbatim(self):
        body = section(self.text, "Failure gallery")
        for r in load("ablation.json")["questions"]:
            o = r["ontology"]
            with self.subTest(q=r["id"]):
                if o["correct"]:
                    self.assertNotIn(f"### {r['id']}, Auto Ontology arm\n", body)
                    continue
                self.assertIn(f"### {r['id']}, Auto Ontology arm", body)
                if o["sql"]:
                    self.assertIn(o["sql"], body)

    def test_limits_name_each_recorded_equivalent_with_its_reason(self):
        limits = section(self.text, "Limits")
        entries = load("equivalents.json")
        by_scenario = {e["scenario"]: e for e in entries}
        # Same S1 stage as the default configuration: the MCP probe is in process.
        self.assertIn("S1", by_scenario)
        self.assertIn("in process", by_scenario["S1"]["equivalent"])
        for e in entries:
            with self.subTest(scenario=e["scenario"]):
                for key in ("literal", "equivalent", "reason"):
                    self.assertTrue(str(e.get(key, "")).strip(), f"empty {key}")
                    self.assertIn(e[key], limits)


class FrozenDefaultTests(unittest.TestCase):
    """Amendment 3: runs/eval/ is frozen; the live run never modifies or
    reruns the default configuration."""

    def test_default_evidence_is_still_run_42127124473(self):
        env = load("environment.json", FROZEN_DIR)
        self.assertEqual(str(env["github_run_id"]), FROZEN_RUN_ID)
        self.assertNotEqual(env.get("configuration"), CONFIGURATION)
        self.assertEqual(load("ablation.json", FROZEN_DIR)["summary"], FROZEN_SUMMARY)

    def test_default_results_still_regenerate_from_frozen_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            regenerated = results.write_results(FROZEN_DIR, Path(d) / "RESULTS.md")
        self.assertEqual(regenerated, (FROZEN_DIR / "RESULTS.md").read_text(encoding="utf-8"))

    def test_no_live_artifacts_written_into_the_frozen_directory(self):
        self.assertFalse((FROZEN_DIR / "RESULTS-LIVE.md").exists())
        self.assertFalse((FROZEN_DIR / "smoke" / "models.json").exists())


class LiveNoKeyTests(unittest.TestCase):
    REAL_KEY_PATTERN = re.compile(r"nvapi-[A-Za-z0-9_\-]{20,}")

    def test_no_key_literal_or_bearer_token_in_live_evidence(self):
        self.assertTrue(RUN_DIR.is_dir(), "runs/eval-live/ is missing")
        text = read_all_text(RUN_DIR)
        self.assertIsNone(self.REAL_KEY_PATTERN.search(text))
        self.assertIsNone(re.search(r"Bearer\s+nvapi-", text))


if __name__ == "__main__":
    unittest.main()
