"""Requirement (amended for wo-gh-1): the NVIDIA_API_KEY never reaches run
artifacts, committed or uploaded, and any file that has to carry the key
for the upstream stack (the Compose env file) is written outside the run
evidence directory and is never committed or uploaded.

Spec: .openspec/specs/auto-ontology-enterprise-eval/spec.md, Requirements,
fourth bullet; applies to S1 (stack start) and S3 (generation on the
hosted NIM key). Offline: no Docker, no network. Subprocess and HTTP calls
of the S1 stage are faked.
"""
import os
import re
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests._support import FAKE_KEY, ROOT, UPSTREAM_COMMIT, WORKFLOW

from auto_ontology_eval import errors, live


class _StopAtCompose(Exception):
    """Raised by the fake runner at the first docker compose call."""


class S1EnvFileLocationTests(unittest.TestCase):
    """stage_s1 writes the key-carrying .env into the upstream checkout,
    never into the run evidence directory."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.run_dir = base / "runs" / "eval"
        self.run_dir.mkdir(parents=True)
        (self.run_dir / "fixture-data").mkdir()
        (self.run_dir / "fixture-data" / "source_a.sql").write_text("SELECT 1;\n")
        self._saved = (live.CTX.upstream_dir, live.CTX.configuration, live.CTX.pg_password)

    def tearDown(self):
        live.CTX.upstream_dir, live.CTX.configuration, live.CTX.pg_password = self._saved
        self._tmp.cleanup()

    def _upstream(self, path: Path) -> Path:
        (path / ".git").mkdir(parents=True)
        (path / ".env.example").write_text(
            "NVIDIA_API_KEY=nvapi-placeholder\nAPP_URL=http://localhost:3000\n")
        live.CTX.upstream_dir = path
        live.CTX.configuration = "default"
        return path

    @staticmethod
    def _fake_run(cmd, key, cwd=None, timeout=1800, check=True, input_text=None):
        if "rev-parse" in cmd:
            return UPSTREAM_COMMIT + "\n"
        if cmd[:2] == ["docker", "compose"]:
            raise _StopAtCompose()
        return ""

    def _run_s1_until_compose(self):
        with mock.patch.object(live, "_run", side_effect=self._fake_run):
            with self.assertRaises((_StopAtCompose, errors.StepFailed)) as ctx:
                live.stage_s1(self.run_dir, FAKE_KEY)
        return ctx.exception

    def _files_under(self, directory: Path):
        return [p for p in directory.rglob("*") if p.is_file()]

    def test_env_file_with_key_lands_in_upstream_checkout_outside_run_dir(self):
        upstream = self._upstream(Path(self._tmp.name) / "runner-temp" / "auto-ontology")
        self.assertIsInstance(self._run_s1_until_compose(), _StopAtCompose)
        env_file = upstream / ".env"
        self.assertTrue(env_file.is_file(), "S1 did not write the upstream .env")
        self.assertIn(f"NVIDIA_API_KEY={FAKE_KEY}", env_file.read_text())
        self.assertFalse(env_file.resolve().is_relative_to(self.run_dir.resolve()))

    def test_env_file_is_owner_only(self):
        upstream = self._upstream(Path(self._tmp.name) / "runner-temp" / "auto-ontology")
        self._run_s1_until_compose()
        mode = stat.S_IMODE((upstream / ".env").stat().st_mode)
        self.assertEqual(mode & 0o077, 0, oct(mode))

    def test_run_dir_holds_no_key_and_no_env_file_after_stack_start(self):
        self._upstream(Path(self._tmp.name) / "runner-temp" / "auto-ontology")
        self._run_s1_until_compose()
        for path in self._files_under(self.run_dir):
            with self.subTest(path=str(path.relative_to(self.run_dir))):
                self.assertNotEqual(path.name, ".env")
                self.assertNotIn(FAKE_KEY, path.read_text(errors="replace"))

    def test_upstream_dir_inside_run_dir_fails_closed_before_writing_the_key(self):
        # If the operator points --upstream-dir into the evidence directory,
        # the key file would be uploaded with the evidence. S1 must refuse
        # before it writes the .env, not after.
        self._upstream(self.run_dir / "upstream")
        exc = self._run_s1_until_compose()
        self.assertIsInstance(exc, errors.StepFailed)
        self.assertNotIn(FAKE_KEY, str(exc))
        for path in self._files_under(self.run_dir):
            with self.subTest(path=str(path.relative_to(self.run_dir))):
                self.assertNotEqual(path.name, ".env")
                self.assertNotIn(FAKE_KEY, path.read_text(errors="replace"))


class SubprocessOutputRedactionTests(unittest.TestCase):
    """Logs the live stages capture (compose-up.log, compose-logs.txt,
    ingestion-service.log) go through live._run, which must redact."""

    def test_run_redacts_the_key_from_stdout_and_stderr(self):
        script = ("import sys; k = sys.argv[1]; print('out', k); "
                  "print('err', k, file=sys.stderr)")
        out = live._run([sys.executable, "-I", "-c", script, FAKE_KEY], FAKE_KEY)
        self.assertNotIn(FAKE_KEY, out)
        self.assertIn("out", out)
        self.assertIn("err", out)

    def test_failure_message_from_run_is_redacted(self):
        script = "import sys; print(sys.argv[1]); sys.exit(3)"
        with self.assertRaises(errors.StepFailed) as ctx:
            live._run([sys.executable, "-I", "-c", script, FAKE_KEY], FAKE_KEY)
        self.assertNotIn(FAKE_KEY, str(ctx.exception))


class WorkflowUploadScopeTests(unittest.TestCase):
    """The uploaded artifact is the run evidence directory only; the
    upstream checkout that holds the .env lives outside it."""

    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text()

    def _upload_paths(self):
        paths = []
        lines = self.text.splitlines()
        for i, line in enumerate(lines):
            if "actions/upload-artifact" not in line:
                continue
            for follow in lines[i + 1:]:
                if re.match(r"\s*-\s", follow):
                    break
                m = re.match(r"\s*path:\s*(.*)$", follow)
                if m:
                    paths.append(m.group(1).strip())
        return paths

    def test_upload_path_is_the_run_dir_and_nothing_else(self):
        paths = self._upload_paths()
        self.assertTrue(paths, "no upload-artifact path found")
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(path, "${{ inputs.run_dir }}")

    def test_upload_never_names_the_upstream_checkout_or_an_env_file(self):
        for path in self._upload_paths():
            with self.subTest(path=path):
                self.assertNotIn("RUNNER_TEMP", path)
                self.assertNotIn("auto-ontology", path.replace("auto-ontology-eval", ""))
                self.assertNotIn(".env", path)

    def test_harness_upstream_dir_is_outside_the_run_dir(self):
        m = re.search(r'--upstream-dir\s+"?([^"\s]+)"?', self.text)
        self.assertIsNotNone(m, "workflow does not pass --upstream-dir")
        upstream = m.group(1)
        self.assertTrue(upstream.startswith("${RUNNER_TEMP}"), upstream)
        self.assertNotIn("inputs.run_dir", upstream)
        self.assertNotIn("GITHUB_WORKSPACE", upstream)


class CommittedEvidenceTests(unittest.TestCase):
    """No committed run artifact is, or carries, a key file."""

    ASSIGNMENT = re.compile(r"NVIDIA_API_KEY\s*=\s*(?!\s|$|\*+|\[REDACTED\]|<redacted>)\S+",
                            re.IGNORECASE)

    def test_env_files_are_git_ignored(self):
        patterns = (ROOT / ".gitignore").read_text().splitlines()
        self.assertIn(".env", [p.strip() for p in patterns])

    def test_no_env_file_under_runs(self):
        runs = ROOT / "runs"
        if not runs.is_dir():
            self.skipTest("no runs/ directory committed")
        found = [str(p.relative_to(ROOT)) for p in runs.rglob(".env*") if p.is_file()]
        self.assertEqual(found, [])

    def test_no_key_assignment_in_any_committed_run_artifact(self):
        runs = ROOT / "runs"
        if not runs.is_dir():
            self.skipTest("no runs/ directory committed")
        for path in sorted(runs.rglob("*")):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            with self.subTest(path=str(path.relative_to(ROOT))):
                self.assertIsNone(self.ASSIGNMENT.search(text))


if __name__ == "__main__":
    unittest.main()
