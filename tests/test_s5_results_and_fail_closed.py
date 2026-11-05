"""S5: RESULTS.md from the executed run only, plus the fail-closed requirement.

results.write_results(run_dir, out_path) reads only these run artifacts:
    environment.json, smoke/smoke.json, timing.json, reconciliation.json,
    ablation.json, and failure.json when a step stopped the run.

pipeline.run_all(env, steps, run_dir) -> exit code. steps is an ordered list
of (name, fn) where fn(run_dir, api_key) returns the Path of the evidence
file it produced.
"""
import json
import re
import tempfile
import unittest
from pathlib import Path

from tests._support import CHAT_MODEL, EMBEDDING_MODEL, FAKE_KEY, RERANK_MODEL, UPSTREAM_COMMIT

from auto_ontology_eval import pipeline, results

SECTIONS = [
    "## Environment",
    "## Time to first ontology",
    "## Reconciliation checklist",
    "## Per-question results",
    "## Failure gallery",
    "## Limits",
]

WRONG_SQL = "SELECT SUM(net_sales)\n  FROM shipments -- gross, includes returns"


def write_full_run(run_dir: Path):
    (run_dir / "smoke").mkdir(parents=True, exist_ok=True)
    (run_dir / "environment.json").write_text(json.dumps({
        "runner": "ubuntu-24.04 (GitHub Actions)",
        "upstream_commit": UPSTREAM_COMMIT,
        "chat_model": CHAT_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "rerank_model": RERANK_MODEL,
        "run_date": "2026-11-05",
    }))
    (run_dir / "smoke" / "smoke.json").write_text(json.dumps({
        "health": {"ok": True}, "catalog": {"ok": True}, "mcp": {"ok": True},
    }))
    (run_dir / "timing.json").write_text(json.dumps({"seconds": 417.25}))
    (run_dir / "reconciliation.json").write_text(json.dumps([
        {"conflict_id": "net_sales_semantics", "mark": "detected",
         "quote": "net_sales in shipments includes returns", "counted": True},
        {"conflict_id": "location_identity", "mark": "ignored", "quote": "", "counted": False},
    ]))
    (run_dir / "ablation.json").write_text(json.dumps({
        "questions": [
            {"id": "Q01", "expected": 900.0,
             "ontology": {"value": 900.0, "sql": "SELECT SUM(net_sales) FROM fact_sales",
                          "correct": True, "provenance": True},
             "raw": {"value": 1000.0, "sql": WRONG_SQL, "correct": False}},
            {"id": "Q02", "expected": ["SKU-1"],
             "ontology": {"value": None, "sql": None, "correct": False, "provenance": False},
             "raw": {"value": ["SKU-1"], "sql": "SELECT sku FROM x", "correct": True}},
        ],
        "summary": {"total": 2, "ontology_correct": 1, "raw_correct": 1, "delta": 0},
    }))


def section(text, heading):
    start = text.index(heading)
    nxt = text.find("\n## ", start + len(heading))
    return text[start: nxt if nxt != -1 else len(text)]


class WriteResultsTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.run_dir = Path(self._tmp.name)
        self.out = self.run_dir / "RESULTS.md"

    def tearDown(self):
        self._tmp.cleanup()

    def test_full_run_has_all_sections_in_order(self):
        write_full_run(self.run_dir)
        text = results.write_results(self.run_dir, self.out)
        self.assertEqual(text, self.out.read_text())
        positions = [text.index(h) for h in SECTIONS]
        self.assertEqual(positions, sorted(positions))

    def test_environment_section_comes_from_artifact(self):
        write_full_run(self.run_dir)
        env = section(results.write_results(self.run_dir, self.out), "## Environment")
        for value in (UPSTREAM_COMMIT, CHAT_MODEL, EMBEDDING_MODEL, RERANK_MODEL,
                      "2026-11-05", "ubuntu-24.04 (GitHub Actions)"):
            self.assertIn(value, env)

    def test_time_and_checklist_come_from_artifacts(self):
        write_full_run(self.run_dir)
        text = results.write_results(self.run_dir, self.out)
        self.assertIn("417.25", section(text, "## Time to first ontology"))
        checklist = section(text, "## Reconciliation checklist")
        self.assertIn("net_sales_semantics", checklist)
        self.assertIn("detected", checklist)
        self.assertIn("net_sales in shipments includes returns", checklist)
        self.assertIn("location_identity", checklist)

    def test_per_question_table_covers_both_arms_and_delta(self):
        write_full_run(self.run_dir)
        table = section(results.write_results(self.run_dir, self.out), "## Per-question results")
        self.assertIn("Q01", table)
        self.assertIn("Q02", table)
        self.assertIn("|", table)
        self.assertRegex(table, r"(?i)delta")
        self.assertRegex(table, r"1\s*/\s*2")  # each arm 1 of 2

    def test_failure_gallery_quotes_wrong_sql_verbatim(self):
        write_full_run(self.run_dir)
        gallery = section(results.write_results(self.run_dir, self.out), "## Failure gallery")
        self.assertIn(WRONG_SQL, gallery)
        self.assertNotIn("SELECT SUM(net_sales) FROM fact_sales", gallery)  # correct SQL is not a failure
        self.assertIn("Q02", gallery)  # ontology arm gave no answer

    def test_limits_section_states_what_the_fixture_did_not_exercise(self):
        write_full_run(self.run_dir)
        limits = section(results.write_results(self.run_dir, self.out), "## Limits")
        self.assertRegex(limits, r"(?i)synthetic")
        self.assertRegex(limits, r"(?i)not (exercise|test|cover)")
        self.assertGreater(len(limits.strip().splitlines()), 2)

    def test_missing_artifacts_say_no_run_evidence_instead_of_estimating(self):
        (self.run_dir / "environment.json").write_text(json.dumps({
            "runner": "r", "upstream_commit": UPSTREAM_COMMIT, "chat_model": CHAT_MODEL,
            "embedding_model": EMBEDDING_MODEL, "rerank_model": RERANK_MODEL, "run_date": "2026-11-05",
        }))
        text = results.write_results(self.run_dir, self.out)
        for heading in SECTIONS[1:5]:
            with self.subTest(heading=heading):
                body = section(text, heading)
                self.assertRegex(body, r"(?i)no run evidence")
                self.assertIsNone(re.search(r"\d+\.\d+\s*s\b", body))

    def test_failed_run_records_failed_step(self):
        write_full_run(self.run_dir)
        (self.run_dir / "failure.json").write_text(json.dumps(
            {"step": "s3_generate", "reason": "HTTP 410 Gone"}))
        text = results.write_results(self.run_dir, self.out)
        self.assertRegex(text, r"(?i)run stopped")
        self.assertIn("s3_generate", text)
        self.assertIn("HTTP 410 Gone", text)

    def test_never_includes_the_key(self):
        write_full_run(self.run_dir)
        (self.run_dir / "failure.json").write_text(json.dumps(
            {"step": "s1_smoke", "reason": f"auth header Bearer {FAKE_KEY}"}))
        text = results.write_results(self.run_dir, self.out, secret=FAKE_KEY)
        self.assertNotIn(FAKE_KEY, text)


class PipelineFailClosedTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.run_dir = Path(self._tmp.name)
        self.calls = []

    def tearDown(self):
        self._tmp.cleanup()

    def _step(self, name, behaviour="ok"):
        def fn(run_dir, api_key):
            self.calls.append(name)
            self.assertEqual(api_key, FAKE_KEY)
            if behaviour == "raise":
                raise RuntimeError(f"step blew up with key {api_key}")
            path = Path(run_dir) / f"{name}.json"
            if behaviour != "no_file":
                path.write_text("{}")
            return path
        return (name, fn)

    def _failure(self):
        return json.loads((self.run_dir / "failure.json").read_text())

    def test_missing_secret_stops_before_any_step(self):
        for env in ({}, {"NVIDIA_API_KEY": ""}):
            with self.subTest(env=env):
                self.calls.clear()
                code = pipeline.run_all(env, [self._step("s1_smoke")], self.run_dir)
                self.assertNotEqual(code, 0)
                self.assertEqual(self.calls, [])
                self.assertEqual(self._failure()["step"], "secrets")
                self.assertIn("secrets", (self.run_dir / "RESULTS.md").read_text())

    def test_raising_step_stops_the_run_and_is_recorded(self):
        steps = [self._step("s1_smoke"), self._step("s3_generate", "raise"), self._step("s4_ablation")]
        code = pipeline.run_all({"NVIDIA_API_KEY": FAKE_KEY}, steps, self.run_dir)
        self.assertNotEqual(code, 0)
        self.assertEqual(self.calls, ["s1_smoke", "s3_generate"])
        self.assertEqual(self._failure()["step"], "s3_generate")
        self.assertIn("s3_generate", (self.run_dir / "RESULTS.md").read_text())

    def test_step_without_evidence_file_stops_the_run(self):
        steps = [self._step("s1_smoke", "no_file"), self._step("s3_generate")]
        code = pipeline.run_all({"NVIDIA_API_KEY": FAKE_KEY}, steps, self.run_dir)
        self.assertNotEqual(code, 0)
        self.assertEqual(self.calls, ["s1_smoke"])
        self.assertEqual(self._failure()["step"], "s1_smoke")

    def test_successful_run_exits_zero_and_writes_results(self):
        steps = [self._step("s1_smoke"), self._step("s3_generate")]
        code = pipeline.run_all({"NVIDIA_API_KEY": FAKE_KEY}, steps, self.run_dir)
        self.assertEqual(code, 0)
        self.assertEqual(self.calls, ["s1_smoke", "s3_generate"])
        self.assertFalse((self.run_dir / "failure.json").exists())
        self.assertTrue((self.run_dir / "RESULTS.md").is_file())

    def test_key_never_lands_in_run_artifacts(self):
        steps = [self._step("s1_smoke"), self._step("s3_generate", "raise")]
        pipeline.run_all({"NVIDIA_API_KEY": FAKE_KEY}, steps, self.run_dir)
        for path in self.run_dir.rglob("*"):
            if path.is_file():
                with self.subTest(path=path.name):
                    self.assertNotIn(FAKE_KEY, path.read_text(errors="replace"))


if __name__ == "__main__":
    unittest.main()
