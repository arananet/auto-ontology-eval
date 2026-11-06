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
def model_env(configuration: str = config.DEFAULT_CONFIGURATION) -> dict[str, str]:
    env = {
        "REASONING_MODEL": config.CHAT_MODEL,
        "NON_REASONING_MODEL": config.CHAT_MODEL,
        "EMBED_MODEL": config.EMBEDDING_MODEL,
        "RERANK_MODEL": config.RERANK_MODEL,
    }
    if configuration == config.LIVE_CONFIGURATION:
        # Spec Amendment 3: wire every internal chat model slot, including
        # the shared DEFAULT_MODELS fallback triplet the role triplets
        # fall back to when unset, to the pinned chat model.
        env = {slot: config.CHAT_MODEL for slot in config.INTERNAL_CHAT_MODEL_SLOTS} | env
    elif configuration != config.DEFAULT_CONFIGURATION:
        raise errors.StepFailed(f"unknown configuration {configuration!r}")
    return env


def _prefixes(configuration: str) -> tuple[str, ...]:
    roles = ("REASONING", "NON_REASONING", "EMBED", "RERANK")
    if configuration == config.LIVE_CONFIGURATION:
        return ("DEFAULT_MODELS",) + roles
    return roles


def resolve_models_script(configuration: str = config.DEFAULT_CONFIGURATION) -> str:
    """In-container script printing the models the stack actually
    resolves, through the upstream's own resolver, for every wired slot
    of the selected configuration."""
    prefixes = ", ".join(repr(p) for p in _prefixes(configuration))
    return (
        "import json\n"
        "from auto_ontology.utils.model_config import resolve\n"
        f"print(json.dumps({{f'{{p}}_MODEL': resolve(p, 'MODEL') for p in ({prefixes},)}}))\n"
    )


# Run inside the auto-ontology container: print the models the stack
# actually resolves, through the upstream's own resolver.
RESOLVE_MODELS_SCRIPT = resolve_models_script()


def verify_resolved_models(output: str,
                           configuration: str = config.DEFAULT_CONFIGURATION) -> dict[str, str]:
    """Parse the resolver output; fail closed unless every pin matches."""
    try:
        resolved = json.loads(output.strip().splitlines()[-1])
    except (ValueError, IndexError) as exc:
        raise errors.StepFailed(f"could not read the stack's resolved models: {output[-500:]!r}") from exc
    expected = model_env(configuration)
    wrong = {k: (resolved.get(k), v) for k, v in expected.items() if resolved.get(k) != v}
    if wrong:
        raise errors.StepFailed(
            "upstream stack resolves models other than the spec pins (got, expected): " + repr(wrong))
    return resolved
