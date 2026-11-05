"""S1: clone the official repository at the pinned commit; compose argv."""
from __future__ import annotations

import json
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


# Model triplets of the pinned upstream (auto_ontology/utils/model_config.py).
# Any triplet left unset falls back to a built-in default chosen by key
# prefix; for nvapi- keys that default is the end-of-life chat model
# nvidia/nemotron-3-nano-30b-a3b (HTTP 410 Gone on the hosted endpoint).
# The stack must therefore receive every model pin explicitly, so that the
# Auto Ontology arm uses the same chat model as the raw-schema arm (S4).
def model_env() -> dict[str, str]:
    return {
        "REASONING_MODEL": config.CHAT_MODEL,
        "NON_REASONING_MODEL": config.CHAT_MODEL,
        "EMBED_MODEL": config.EMBEDDING_MODEL,
        "RERANK_MODEL": config.RERANK_MODEL,
    }


# Run inside the auto-ontology container: print the models the stack
# actually resolves, through the upstream's own resolver.
RESOLVE_MODELS_SCRIPT = (
    "import json\n"
    "from auto_ontology.utils.model_config import resolve\n"
    "print(json.dumps({f'{p}_MODEL': resolve(p, 'MODEL') for p in "
    "('REASONING', 'NON_REASONING', 'EMBED', 'RERANK')}))\n"
)


def verify_resolved_models(output: str) -> dict[str, str]:
    """Parse the resolver output; fail closed unless every pin matches."""
    try:
        resolved = json.loads(output.strip().splitlines()[-1])
    except (ValueError, IndexError) as exc:
        raise errors.StepFailed(f"could not read the stack's resolved models: {output[-500:]!r}") from exc
    wrong = {k: (resolved.get(k), v) for k, v in model_env().items() if resolved.get(k) != v}
    if wrong:
        raise errors.StepFailed(
            "upstream stack resolves models other than the spec pins (got, expected): " + repr(wrong))
    return resolved
