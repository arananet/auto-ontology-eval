"""S5 environment record: runner, upstream commit, model ids, run date."""
from __future__ import annotations

import datetime as _dt
import platform
from typing import Mapping

from . import config


def collect(env: Mapping[str, str], now: _dt.datetime | None = None) -> dict:
    now = now or _dt.datetime.now(_dt.timezone.utc)
    image = env.get("ImageOS", "")
    image_version = env.get("ImageVersion", "")
    runner_bits = [b for b in (image, image_version) if b]
    runner = " ".join(runner_bits) or platform.platform()
    if env.get("GITHUB_ACTIONS") == "true" or env.get("RUNNER_NAME"):
        runner += f" (GitHub Actions, {env.get('RUNNER_NAME', 'runner')}, {env.get('RUNNER_OS', '')})"
    return {
        "runner": runner,
        "github_run_id": env.get("GITHUB_RUN_ID", ""),
        "upstream_repo": config.UPSTREAM_REPO_URL,
        "upstream_commit": config.UPSTREAM_COMMIT,
        "chat_model": config.CHAT_MODEL,
        "embedding_model": config.EMBEDDING_MODEL,
        "rerank_model": config.RERANK_MODEL,
        "run_date": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
