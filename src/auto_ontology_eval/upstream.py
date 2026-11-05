"""S1: clone the official repository at the pinned commit; compose argv."""
from __future__ import annotations

from pathlib import Path

from . import config, errors

UPSTREAM_COMPOSE_FILE = "docker-compose.yml"


def clone_commands(dest: str | Path) -> list[list[str]]:
    dest = str(dest)
    return [
        ["git", "clone", "--no-checkout", config.UPSTREAM_REPO_URL, dest],
        ["git", "-C", dest, "checkout", "--detach", config.UPSTREAM_COMMIT],
        ["git", "-C", dest, "rev-parse", "HEAD"],
    ]


def verify_checkout(head_output: str) -> None:
    head = head_output.strip()
    if head != config.UPSTREAM_COMMIT:
        raise errors.StepFailed(
            f"checked out HEAD {head!r} is not the pinned commit {config.UPSTREAM_COMMIT}"
        )


def compose_command(repo: str | Path, *args: str, overrides: list[Path] | None = None) -> list[str]:
    """docker compose with the upstream file first; overrides only after it."""
    repo = Path(repo)
    cmd = ["docker", "compose", "-f", str(repo / UPSTREAM_COMPOSE_FILE)]
    for extra in overrides or []:
        cmd += ["-f", str(extra)]
    return cmd + list(args)
