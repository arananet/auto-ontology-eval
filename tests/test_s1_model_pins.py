"""S1/S3/S4: the upstream stack must run on the spec's model pins.

Regression for run 42127124473: the harness dropped every *_MODEL line from
the upstream .env, so the pinned upstream fell back to its built-in nvapi-
default chat model (end of life, HTTP 410) while the raw-schema arm used the
Amendment 2 pin. Offline: no Docker, no network.
"""
import json
import tempfile
import unittest
from pathlib import Path

from tests._support import CHAT_MODEL, EMBEDDING_MODEL, FAKE_KEY, RERANK_MODEL  # noqa: F401

from auto_ontology_eval import errors, live, upstream

EOL_CHAT = "nvidia/nemotron-3-nano-30b-a3b"
EXPECTED = {
    "REASONING_MODEL": CHAT_MODEL,
    "NON_REASONING_MODEL": CHAT_MODEL,
    "EMBED_MODEL": EMBEDDING_MODEL,
    "RERANK_MODEL": RERANK_MODEL,
}


class ModelEnv(unittest.TestCase):
    def test_every_triplet_carries_the_spec_pin(self):
        self.assertEqual(upstream.model_env(), EXPECTED)

    def test_env_file_writes_the_pins_and_never_the_eol_model(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / ".env.example").write_text(
                f"DEFAULT_MODELS_MODEL={EOL_CHAT}\nREASONING_MODEL={EOL_CHAT}\n"
                f"NON_REASONING_MODEL={EOL_CHAT}\nAPP_URL=http://localhost:3000\n")
            text = live._env_file(repo, FAKE_KEY)
        env = dict(l.split("=", 1) for l in text.splitlines() if "=" in l)
        for name, value in EXPECTED.items():
            self.assertEqual(env.get(name), value, name)
        self.assertNotIn(EOL_CHAT, text)
        self.assertNotIn("DEFAULT_MODELS_MODEL", env)


class ResolvedModels(unittest.TestCase):
    def test_matching_resolution_passes(self):
        self.assertEqual(upstream.verify_resolved_models("log line\n" + json.dumps(EXPECTED)), EXPECTED)

    def test_fallback_to_eol_default_fails_closed(self):
        bad = dict(EXPECTED, REASONING_MODEL=EOL_CHAT)
        with self.assertRaises(errors.StepFailed):
            upstream.verify_resolved_models(json.dumps(bad))

    def test_unreadable_output_fails_closed(self):
        for out in ("", "Traceback: ModuleNotFoundError"):
            with self.assertRaises(errors.StepFailed):
                upstream.verify_resolved_models(out)


if __name__ == "__main__":
    unittest.main()
