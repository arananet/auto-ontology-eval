"""Spec requirements: upstream pin, default models, secret handling.

Covers the Requirements section (pin, NVIDIA_API_KEY only as a secret,
never in code/logs/RESULTS.md) and the model ids named in S3.
"""
import json
import re
import unittest

from tests._support import (
    CHAT_MODEL,
    EMBEDDING_MODEL,
    FAKE_KEY,
    RERANK_MODEL,
    ROOT,
    UPSTREAM_COMMIT,
    read_all_text,
)

from auto_ontology_eval import config, environment, errors, secrets


class PinnedConfigTests(unittest.TestCase):
    def test_upstream_is_the_official_repo_at_the_pinned_commit(self):
        self.assertRegex(
            config.UPSTREAM_REPO_URL,
            r"^https://github\.com/NVIDIA/auto-ontology(\.git)?$",
        )
        self.assertEqual(config.UPSTREAM_COMMIT, UPSTREAM_COMMIT)

    def test_default_hosted_nim_models_match_spec(self):
        self.assertEqual(config.CHAT_MODEL, CHAT_MODEL)
        self.assertEqual(config.EMBEDDING_MODEL, EMBEDDING_MODEL)
        self.assertEqual(config.RERANK_MODEL, RERANK_MODEL)

    def test_api_key_env_name_is_the_repository_secret_name(self):
        self.assertEqual(config.API_KEY_ENV, "NVIDIA_API_KEY")


class RequireApiKeyTests(unittest.TestCase):
    def test_returns_key_when_present(self):
        self.assertEqual(
            secrets.require_api_key({"NVIDIA_API_KEY": FAKE_KEY}), FAKE_KEY
        )

    def test_absent_key_fails_closed(self):
        with self.assertRaises(errors.MissingSecretError):
            secrets.require_api_key({})

    def test_empty_or_blank_key_fails_closed(self):
        for value in ("", "   ", "\n"):
            with self.subTest(value=repr(value)):
                with self.assertRaises(errors.MissingSecretError):
                    secrets.require_api_key({"NVIDIA_API_KEY": value})

    def test_missing_secret_is_a_step_failure(self):
        self.assertTrue(issubclass(errors.MissingSecretError, errors.StepFailed))

    def test_error_message_never_contains_key(self):
        # Even a malformed (whitespace-padded) key must not be echoed.
        try:
            secrets.require_api_key({"OTHER": FAKE_KEY})
        except errors.MissingSecretError as exc:
            self.assertNotIn(FAKE_KEY, str(exc))


class RedactTests(unittest.TestCase):
    def test_redacts_every_occurrence(self):
        text = f"Authorization: Bearer {FAKE_KEY}\nretry {FAKE_KEY}"
        out = secrets.redact(text, FAKE_KEY)
        self.assertNotIn(FAKE_KEY, out)
        self.assertIn("Authorization: Bearer", out)

    def test_empty_secret_leaves_text_unchanged(self):
        self.assertEqual(secrets.redact("hello", ""), "hello")


class EnvironmentRecordTests(unittest.TestCase):
    """S5 environment section: runner, commit, model ids, run date."""

    def test_collects_required_fields_without_the_key(self):
        env = {
            "NVIDIA_API_KEY": FAKE_KEY,
            "RUNNER_OS": "Linux",
            "RUNNER_NAME": "GitHub Actions 7",
            "ImageOS": "ubuntu24",
        }
        record = environment.collect(env)
        for field in (
            "runner",
            "upstream_commit",
            "chat_model",
            "embedding_model",
            "rerank_model",
            "run_date",
        ):
            self.assertIn(field, record)
        self.assertEqual(record["upstream_commit"], UPSTREAM_COMMIT)
        self.assertEqual(record["chat_model"], CHAT_MODEL)
        self.assertEqual(record["embedding_model"], EMBEDDING_MODEL)
        self.assertEqual(record["rerank_model"], RERANK_MODEL)
        self.assertRegex(record["run_date"], r"^\d{4}-\d{2}-\d{2}")
        self.assertNotIn(FAKE_KEY, json.dumps(record))


class NoKeyInCommittedFilesTests(unittest.TestCase):
    """The key never appears in code or committed files."""

    REAL_KEY_PATTERN = re.compile(r"nvapi-[A-Za-z0-9_\-]{20,}")

    def test_no_nvidia_key_literal_in_repo_sources(self):
        for sub in ("src", "fixture", "tests", ".github"):
            directory = ROOT / sub
            if not directory.exists():
                continue
            with self.subTest(directory=sub):
                self.assertIsNone(
                    self.REAL_KEY_PATTERN.search(read_all_text(directory))
                )


if __name__ == "__main__":
    unittest.main()
