# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["JobLogError"]


class JobLogError(BaseModel):
    exception_type: Optional[str] = None
    """The exception type for the error"""

    explanation: Optional[str] = None
    """Explanation of the error"""

    file: Optional[str] = None
    """File in which the exception occurred"""

    line: Optional[int] = None
    """Line in which the exception occurred"""

    message: Optional[str] = None
    """Message from the exception"""

    stack_trace: Optional[str] = None
    """Stack trace from the exception"""

    timestamp: Optional[str] = None
    """Timestamp of job error"""
