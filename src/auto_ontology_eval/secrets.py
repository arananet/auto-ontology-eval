"""Secret handling: require the key, and redact it from anything written."""
from __future__ import annotations

from typing import Mapping

from . import config, errors

REDACTED = "[REDACTED]"


def require_api_key(env: Mapping[str, str]) -> str:
    value = env.get(config.API_KEY_ENV)
    if value is None or not value.strip():
        raise errors.MissingSecretError(
            f"{config.API_KEY_ENV} is absent or empty; set the repository secret "
            f"{config.API_KEY_ENV}. The run stops here."
        )
    return value.strip()


def redact(text: str, secret: str | None) -> str:
    if not secret:
        return text
    out = text.replace(secret, REDACTED)
    stripped = secret.strip()
    if stripped and stripped != secret:
        out = out.replace(stripped, REDACTED)
    return out
