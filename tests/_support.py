"""Shared helpers for the auto-ontology-enterprise-eval scenario tests.

Spec: .openspec/specs/auto-ontology-enterprise-eval/spec.md

Run from the project root:
    python -m unittest discover -s tests -t .

The tests are offline. They exercise the harness contract with fakes and
the committed fixture; they never call NVIDIA endpoints or Docker.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

FIXTURE_DIR = ROOT / "fixture"
WORKFLOW = ROOT / ".github" / "workflows" / "auto-ontology-eval.yml"

# Values pinned by the spec. If the spec is amended, change them here and
# nowhere else in the tests.
UPSTREAM_COMMIT = "cdaf61e1bd0cf3820d11d72b43bb460816aebbd3"
CHAT_MODEL = "nvidia/nemotron-nano-3-30b-a3b"  # spec Amendment 1, 2026-11-05
EMBEDDING_MODEL = "nvidia/nemotron-3-embed-1b"
RERANK_MODEL = "nvidia/llama-nemotron-rerank-vl-1b-v2"

# Deliberately short so it can never match the real-key scan pattern.
FAKE_KEY = "nvapi-TESTONLY-k3y"

REQUIRED_CONFLICT_IDS = {
    "net_sales_semantics",
    "location_identity",
    "product_hierarchy",
    "shared_sku_identity",
}


def read_all_text(directory: Path) -> str:
    """Concatenate every file under a directory, for secret scans."""
    chunks = []
    for path in sorted(directory.rglob("*")):
        if path.is_file():
            chunks.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(chunks)
