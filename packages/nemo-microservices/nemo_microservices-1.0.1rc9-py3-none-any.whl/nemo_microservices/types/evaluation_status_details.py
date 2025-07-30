# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from .._models import BaseModel
from .task_status import TaskStatus

__all__ = ["EvaluationStatusDetails"]


class EvaluationStatusDetails(BaseModel):
    message: Optional[str] = None
    """A message about the status of the evaluation."""

    progress: Optional[float] = None
    """The progress of the evaluation, between 0.0 and 100.0."""

    task_status: Optional[Dict[str, TaskStatus]] = None
    """Information about the status of every task."""
