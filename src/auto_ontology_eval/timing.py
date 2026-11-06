"""S3 time to first ontology, from run event timestamps."""
from __future__ import annotations

import datetime as _dt

from . import errors


def _parse(ts: str) -> _dt.datetime:
    return _dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))


def time_to_first_ontology(events: list[dict], sources=("A", "B")) -> float:
    """Seconds from the moment both sources are registered (the later of the
    two registrations) to the first complete catalog export after it."""
    registered = {}
    for e in events:
        if e.get("event") == "source_registered" and e.get("source") in sources:
            at = _parse(e["at"])
            registered[e["source"]] = min(at, registered.get(e["source"], at))
    if set(registered) != set(sources):
        raise errors.StepFailed(f"not every source was registered: {sorted(registered)}")
    start = max(registered.values())
    exports = sorted(
        _parse(e["at"]) for e in events
        if e.get("event") == "catalog_exported" and e.get("complete") and _parse(e["at"]) >= start
    )
    if not exports:
        raise errors.StepFailed("no complete catalog export after both sources were registered")
    return (exports[0] - start).total_seconds()
