# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypeAlias

__all__ = ["JobStatus"]

JobStatus: TypeAlias = Literal[
    "created", "pending", "running", "cancelled", "cancelling", "failed", "completed", "ready", "unknown"
]
