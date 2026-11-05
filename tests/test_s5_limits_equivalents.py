"""S5 (amended): the limits section names every equivalent the run used.

Spec text: "The limits section also names every place where the run used an
equivalent instead of the literal step in S1 to S4, and says why. Two known
cases: the MCP probe in S1 listing tools in process rather than over the
network (the pinned MCP server requires an OAuth token), and SQL from the
raw-schema arm in S4 running on a copy of the fixture rather than on the live
Postgres and DuckDB sources."

Contract: any step that substitutes an equivalent for the literal spec step
records it in the run artifact equivalents.json, a JSON list of objects:

    {"scenario": "S1" | "S2" | "S3" | "S4",
     "literal": what the spec step says,
     "equivalent": what the run did instead,
     "reason": why}

results.write_results renders every entry inside "## Limits". Because
RESULTS.md holds only what the run produced, it names only recorded entries
and never invents one. If equivalents.json is missing, the limits section
says there is no run evidence about equivalents instead of claiming there
were none.
"""
import json
import tempfile
import unittest
from pathlib import Path

from tests._support import FAKE_KEY
from tests.test_s5_results_and_fail_closed import section, write_full_run

from auto_ontology_eval import results

MCP_EQUIVALENT = {
    "scenario": "S1",
    "literal": "MCP tools/list probe over the network",
    "equivalent": "MCP tools listed in process against the pinned server module",
    "reason": "the pinned MCP server requires a frontend OAuth token on HTTP",
}
RAW_ARM_EQUIVALENT = {
    "scenario": "S4",
    "literal": "raw-schema arm SQL executed on the live Postgres and DuckDB sources",
    "equivalent": "raw-schema arm SQL executed on a copy of the fixture",
    "reason": "the live sources are only reachable inside the upstream compose network",
}


class LimitsEquivalentsTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.run_dir = Path(self._tmp.name)
        self.out = self.run_dir / "RESULTS.md"
        write_full_run(self.run_dir)

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, entries):
        (self.run_dir / "equivalents.json").write_text(json.dumps(entries))

    def _limits(self, **kwargs):
        return section(results.write_results(self.run_dir, self.out, **kwargs), "## Limits")

    def test_both_known_equivalents_are_named_with_their_reasons(self):
        self._write([MCP_EQUIVALENT, RAW_ARM_EQUIVALENT])
        limits = self._limits()
        for entry in (MCP_EQUIVALENT, RAW_ARM_EQUIVALENT):
            with self.subTest(scenario=entry["scenario"]):
                self.assertIn(entry["scenario"], limits)
                self.assertIn(entry["equivalent"], limits)
                self.assertIn(entry["reason"], limits)

    def test_equivalents_stay_inside_the_limits_section(self):
        self._write([MCP_EQUIVALENT, RAW_ARM_EQUIVALENT])
        text = results.write_results(self.run_dir, self.out)
        limits_start = text.index("## Limits")
        for entry in (MCP_EQUIVALENT, RAW_ARM_EQUIVALENT):
            with self.subTest(scenario=entry["scenario"]):
                self.assertIn(entry["equivalent"], text)
                self.assertGreater(text.index(entry["equivalent"]), limits_start)

    def test_every_recorded_equivalent_is_named_not_just_the_known_two(self):
        extra = {
            "scenario": "S3",
            "literal": "catalog page fetched from the web UI",
            "equivalent": "catalog exported through the REST API",
            "reason": "the web UI needs an interactive login",
        }
        self._write([MCP_EQUIVALENT, RAW_ARM_EQUIVALENT, extra])
        limits = self._limits()
        self.assertIn(extra["equivalent"], limits)
        self.assertIn(extra["reason"], limits)

    def test_only_recorded_equivalents_are_named(self):
        self._write([MCP_EQUIVALENT])
        limits = self._limits()
        self.assertIn(MCP_EQUIVALENT["equivalent"], limits)
        self.assertNotIn(RAW_ARM_EQUIVALENT["equivalent"], limits)
        self.assertNotIn(RAW_ARM_EQUIVALENT["reason"], limits)

    def test_entry_without_a_reason_is_flagged_not_silently_rendered(self):
        self._write([dict(MCP_EQUIVALENT, reason="")])
        limits = self._limits()
        self.assertIn(MCP_EQUIVALENT["equivalent"], limits)
        self.assertRegex(limits, r"(?i)reason not recorded")

    def test_missing_equivalents_artifact_says_no_run_evidence(self):
        limits = self._limits()
        self.assertRegex(limits, r"(?i)no run evidence")
        self.assertIn("equivalents.json", limits)
        # The standing what-was-not-exercised limits still appear.
        self.assertRegex(limits, r"(?i)synthetic")

    def test_empty_list_means_the_run_recorded_no_equivalents(self):
        self._write([])
        limits = self._limits()
        self.assertRegex(limits, r"(?i)no equivalents")
        self.assertNotRegex(limits, r"(?i)no run evidence[^\n]*equivalents\.json")

    def test_key_in_an_equivalent_entry_is_redacted(self):
        self._write([dict(MCP_EQUIVALENT, reason=f"token rejected for {FAKE_KEY}")])
        text = results.write_results(self.run_dir, self.out, secret=FAKE_KEY)
        self.assertNotIn(FAKE_KEY, text)


if __name__ == "__main__":
    unittest.main()
