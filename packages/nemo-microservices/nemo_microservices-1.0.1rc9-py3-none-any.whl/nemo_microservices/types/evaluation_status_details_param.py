# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import TypedDict

from .task_status import TaskStatus

__all__ = ["EvaluationStatusDetailsParam"]


class EvaluationStatusDetailsParam(TypedDict, total=False):
    message: str
    """A message about the status of the evaluation."""

    progress: float
    """The progress of the evaluation, between 0.0 and 100.0."""

    task_status: Dict[str, TaskStatus]
    """Information about the status of every task."""
