"""S1 smoke evidence: API health, one catalog/API response, MCP probe."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Mapping

from . import errors
from .secrets import redact

REQUIRED_CHECKS = ("health", "catalog", "mcp")

Check = Callable[[], "tuple[bool, str]"]


def run_smoke(checks: Mapping[str, Check], out_dir: Path, secret: str | None = None) -> dict:
    """Run every required check, record each response to a file, then fail
    closed if any check failed, raised or is missing."""
    smoke_dir = Path(out_dir) / "smoke"
    smoke_dir.mkdir(parents=True, exist_ok=True)
    summary = {}
    for name in REQUIRED_CHECKS:
        fn = checks.get(name)
        if fn is None:
            ok, body = False, f"check {name!r} was not provided"
        else:
            try:
                ok, body = fn()
                ok = bool(ok)
            except Exception as exc:  # a crashing check is a failed check
                ok, body = False, f"{type(exc).__name__}: {exc}"
        body = redact(str(body), secret)
        path = smoke_dir / f"{name}.txt"
        path.write_text(body, encoding="utf-8")
        summary[name] = {"ok": ok, "evidence": path.name}
    (smoke_dir / "smoke.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    failed = [n for n in REQUIRED_CHECKS if not summary[n]["ok"]]
    if failed:
        raise errors.StepFailed(f"smoke checks failed: {', '.join(failed)}")
    return summary
