"""Requirements: Docker-capable GitHub Actions runner, key only via the
repository secret, never echoed, nothing published.

Contract: .github/workflows/auto-ontology-eval.yml runs the harness.
"""
import re
import unittest

from tests._support import WORKFLOW


class WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text()

    def test_runs_on_a_docker_capable_github_hosted_linux_runner(self):
        self.assertRegex(self.text, r"runs-on:\s*\[?\s*ubuntu-")

    def test_key_comes_only_from_the_repository_secret(self):
        self.assertIn("secrets.NVIDIA_API_KEY", self.text)
        for line in self.text.splitlines():
            if "NVIDIA_API_KEY" in line and ":" in line and "secrets." not in line:
                # Any assignment of the variable must source the secret.
                self.assertNotRegex(line, r"NVIDIA_API_KEY:\s*\S")

    def test_key_is_never_echoed_or_traced(self):
        for line in self.text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            self.assertFalse(
                re.search(r"\b(echo|printf|cat)\b", stripped) and "NVIDIA_API_KEY" in stripped,
                stripped,
            )
        self.assertNotRegex(self.text, r"set\s+-[a-wyz]*x")

    def test_nothing_is_published(self):
        lowered = self.text.lower()
        for marker in ("gh release", "softprops/action-gh-release", "gh-pages",
                       "peaceiris/actions-gh-pages", "npm publish", "twine upload"):
            self.assertNotIn(marker, lowered)

    def test_pins_the_upstream_commit_via_the_harness_or_directly(self):
        self.assertTrue(
            "cdaf61e1bd0cf3820d11d72b43bb460816aebbd3" in self.text
            or "auto_ontology_eval" in self.text,
            "workflow neither pins the commit nor invokes the harness that does",
        )

    def test_amendment3_live_configuration_is_dispatchable(self):
        # Spec Amendment 3: the second configuration runs through the same
        # workflow, selected by dispatch inputs whose defaults reproduce
        # the default configuration run.
        self.assertIn("live-internals", self.text)
        self.assertIn("--configuration", self.text)
        self.assertIn("inputs.run_dir", self.text)
        self.assertIn("default: runs/eval", self.text)


if __name__ == "__main__":
    unittest.main()
