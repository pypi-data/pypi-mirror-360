"""Utility guards for SupervisorAgent."""

from __future__ import annotations

import os
import time
from typing import Iterable

from diagram_to_iac.core.errors import MissingSecretError


def check_required_secrets(required: Iterable[str] | None = None) -> None:
    """Ensure required secrets exist and are not empty."""
    start = time.perf_counter()
    secrets = list(required) if required is not None else ["GITHUB_TOKEN"]
    missing = [s for s in secrets if not os.environ.get(s, "").strip()]
    if missing:
        raise MissingSecretError(
            "Missing required secret(s): " + ", ".join(missing)
        )
    # Function should be extremely fast; return quickly
    _ = time.perf_counter() - start

