"""S1: stand up the upstream stack at the pinned commit and prove it answers.

Offline contract tests: the clone/checkout and compose commands target the
official repo, the exact commit and the upstream project's own compose
file; smoke evidence for health, catalog and MCP is captured to files; the
step fails closed when any of the three checks fails.
"""
import json
import tempfile
import unittest
from pathlib import Path

from tests._support import FAKE_KEY, UPSTREAM_COMMIT

from auto_ontology_eval import errors, smoke, upstream


class CloneAndCheckoutTests(unittest.TestCase):
    def test_clones_official_repo_and_checks_out_exact_commit(self):
        cmds = upstream.clone_commands("/tmp/ao")
        flat = [" ".join(c) for c in cmds]
        self.assertTrue(
            any(c[:2] == ["git", "clone"] and any("github.com/NVIDIA/auto-ontology" in a for a in c) for c in cmds),
            flat,
        )
        self.assertTrue(
            any("checkout" in c and UPSTREAM_COMMIT in c for c in cmds),
            f"no checkout of {UPSTREAM_COMMIT} in {flat}",
        )

    def test_commands_are_argv_lists_not_shell_strings(self):
        for cmd in upstream.clone_commands("/tmp/ao"):
            self.assertIsInstance(cmd, list)
            for arg in cmd:
                self.assertIsInstance(arg, str)

    def test_verify_checkout_accepts_pinned_head(self):
        upstream.verify_checkout(UPSTREAM_COMMIT + "\n")  # no raise

    def test_verify_checkout_rejects_any_other_head(self):
        with self.assertRaises(errors.StepFailed):
            upstream.verify_checkout("0" * 40)
        with self.assertRaises(errors.StepFailed):
            upstream.verify_checkout(UPSTREAM_COMMIT[:12])


class ComposeCommandTests(unittest.TestCase):
    def test_uses_upstream_compose_file_first(self):
        repo = Path("/tmp/ao")
        cmd = upstream.compose_command(repo, "up", "-d")
        self.assertEqual(cmd[:2], ["docker", "compose"])
        self.assertIn("-f", cmd)
        first_file = Path(cmd[cmd.index("-f") + 1])
        # The first compose file is the upstream project's own, inside the
        # pinned checkout; overrides (if any) may only follow it.
        self.assertEqual(first_file.parent, repo)
        self.assertRegex(first_file.name, r"^(docker-)?compose(\.[\w-]+)?\.ya?ml$")
        self.assertEqual(cmd[-2:], ["up", "-d"])


def _ok(body):
    return lambda: (True, body)


def _fail(body):
    return lambda: (False, body)


class SmokeTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.out = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_required_checks_are_health_catalog_mcp(self):
        self.assertEqual(set(smoke.REQUIRED_CHECKS), {"health", "catalog", "mcp"})

    def test_all_pass_writes_three_evidence_files_and_summary(self):
        checks = {
            "health": _ok('{"status":"ok"}'),
            "catalog": _ok('{"items":[{"name":"sales"}]}'),
            "mcp": _ok('{"jsonrpc":"2.0","result":{"tools":[]}}'),
        }
        result = smoke.run_smoke(checks, self.out)
        for name in ("health", "catalog", "mcp"):
            path = self.out / "smoke" / f"{name}.txt"
            self.assertTrue(path.is_file(), path)
            self.assertIn(checks[name]()[1], path.read_text())
        summary = json.loads((self.out / "smoke" / "smoke.json").read_text())
        self.assertTrue(all(summary[n]["ok"] for n in ("health", "catalog", "mcp")))
        self.assertTrue(all(result[n]["ok"] for n in ("health", "catalog", "mcp")))

    def test_any_failing_check_fails_closed_after_recording_evidence(self):
        for failing in ("health", "catalog", "mcp"):
            with self.subTest(failing=failing):
                out = self.out / failing
                checks = {n: _ok("fine") for n in ("health", "catalog", "mcp")}
                checks[failing] = _fail("HTTP 503")
                with self.assertRaises(errors.StepFailed):
                    smoke.run_smoke(checks, out)
                summary = json.loads((out / "smoke" / "smoke.json").read_text())
                self.assertFalse(summary[failing]["ok"])
                self.assertIn("HTTP 503", (out / "smoke" / f"{failing}.txt").read_text())

    def test_missing_check_fails_closed(self):
        checks = {"health": _ok("ok"), "catalog": _ok("ok")}
        with self.assertRaises(errors.StepFailed):
            smoke.run_smoke(checks, self.out)

    def test_check_that_raises_counts_as_failure(self):
        def boom():
            raise ConnectionError("refused")

        checks = {"health": boom, "catalog": _ok("ok"), "mcp": _ok("ok")}
        with self.assertRaises(errors.StepFailed):
            smoke.run_smoke(checks, self.out)

    def test_evidence_is_redacted(self):
        checks = {
            "health": _ok("ok"),
            "catalog": _ok(f"echo header Bearer {FAKE_KEY}"),
            "mcp": _ok("ok"),
        }
        smoke.run_smoke(checks, self.out, secret=FAKE_KEY)
        for path in (self.out / "smoke").iterdir():
            self.assertNotIn(FAKE_KEY, path.read_text())


if __name__ == "__main__":
    unittest.main()
