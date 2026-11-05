"""Record each place the run used an equivalent instead of the literal spec step.

S5 (amended): the RESULTS.md limits section names every such place and says
why. Steps call ``record`` at the moment they substitute an equivalent, so
the limits section is built from what the run did, not from hard-coded text.

The artifact is ``equivalents.json`` in the run directory: a JSON list of
``{"scenario", "literal", "equivalent", "reason"}`` objects.
"""
from __future__ import annotations

import json
from pathlib import Path

FILENAME = "equivalents.json"
FIELDS = ("scenario", "literal", "equivalent", "reason")


def start(run_dir) -> Path:
    """Create an empty record. Called once per run before the first step that may use an equivalent."""
    path = Path(run_dir) / FILENAME
    path.write_text("[]\n", encoding="utf-8")
    return path


def record(run_dir, scenario: str, literal: str, equivalent: str, reason: str) -> Path:
    """Append one entry. Recording the same entry twice keeps it once."""
    path = Path(run_dir) / FILENAME
    entries = load(run_dir) or []
    entry = {"scenario": scenario, "literal": literal, "equivalent": equivalent, "reason": reason}
    if entry not in entries:
        entries.append(entry)
    path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    return path


def load(run_dir) -> list | None:
    """The recorded entries, or None when the run produced no readable record."""
    path = Path(run_dir) / FILENAME
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return None
    return data if isinstance(data, list) else None
