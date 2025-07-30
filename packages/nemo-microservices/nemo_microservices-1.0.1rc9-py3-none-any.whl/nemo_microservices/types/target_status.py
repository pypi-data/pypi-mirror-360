# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["TargetStatus"]

TargetStatus: TypeAlias = Literal[
    "created",
    "pending",
    "downloading",
    "failed",
    "ready",
    "cancelled",
    "unknown",
    "deleted",
    "deleting",
    "delete_failed",
]
