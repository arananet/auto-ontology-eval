"""Fail-closed runner. Steps run in order; the first step that raises or
does not produce its evidence file stops the run. RESULTS.md is always
written, and records the failed step when there is one."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Mapping, Sequence

from . import config, environment, equivalents, errors, results, secrets

Step = "tuple[str, Callable[[Path, str], Path]]"


def _fail(run_dir: Path, step: str, reason: str, key: str | None) -> None:
    (run_dir / "failure.json").write_text(json.dumps(
        {"step": step, "reason": secrets.redact(reason, key)}, indent=2))


def run_all(env: Mapping[str, str], steps: Sequence, run_dir,
            configuration: str = config.DEFAULT_CONFIGURATION) -> int:
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    for stale in (run_dir / "failure.json", run_dir / equivalents.FILENAME):
        if stale.exists():
            stale.unlink()
    (run_dir / "environment.json").write_text(
        json.dumps(environment.collect(env, configuration=configuration), indent=2))
    key = None
    code = 0
    log = []
    try:
        key = secrets.require_api_key(env)
    except errors.MissingSecretError as exc:
        _fail(run_dir, "secrets", str(exc), None)
        code = 1
    if code == 0:
        equivalents.start(run_dir)
        for name, fn in steps:
            try:
                evidence = fn(run_dir, key)
            except Exception as exc:
                _fail(run_dir, name, f"{type(exc).__name__}: {exc}", key)
                log.append({"step": name, "ok": False})
                code = 1
                break
            if not evidence or not Path(evidence).is_file():
                _fail(run_dir, name, f"step produced no evidence file ({evidence})", key)
                log.append({"step": name, "ok": False})
                code = 1
                break
            log.append({"step": name, "ok": True, "evidence": str(Path(evidence).name)})
    (run_dir / "steps.json").write_text(json.dumps(log, indent=2))
    if configuration == config.LIVE_CONFIGURATION:
        # Spec Amendment 3: the live-internals configuration writes its
        # own results document, RESULTS-LIVE.md, in its own run directory.
        results.write_live_results(run_dir, run_dir / "RESULTS-LIVE.md", secret=key)
    else:
        results.write_results(run_dir, run_dir / "RESULTS.md", secret=key)
    return code
