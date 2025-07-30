# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import builtins
from typing import List, Optional

from ..._models import BaseModel
from .job_event import JobEvent

__all__ = ["JobEntry"]


class JobEntry(BaseModel):
    events: Optional[List[JobEvent]] = None
    """The events that occurred"""

    logs: Optional[object] = None
    """The logs from any pods that existed"""

    object: Optional[str] = None
    """The object where the informaiton is being pulled"""

    status: Optional[builtins.object] = None
    """The status of the pod"""
