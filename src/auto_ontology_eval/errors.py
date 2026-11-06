"""Failure types. Any StepFailed stops the run (fail closed)."""


class StepFailed(RuntimeError):
    """A scenario step could not produce its evidence."""


class MissingSecretError(StepFailed):
    """NVIDIA_API_KEY is absent or blank."""
