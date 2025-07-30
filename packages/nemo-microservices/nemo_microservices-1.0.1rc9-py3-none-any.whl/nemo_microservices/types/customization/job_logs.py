# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from ..._models import BaseModel
from .job_entry import JobEntry
from .job_log_error import JobLogError

__all__ = ["JobLogs"]


class JobLogs(BaseModel):
    entries: Optional[Dict[str, JobEntry]] = None
    """The output from all of the containers"""

    error: Optional[JobLogError] = None
    """Error information from job execution.

    Contains detailed error information including stack traces and context for
    debugging failed jobs.
    """
