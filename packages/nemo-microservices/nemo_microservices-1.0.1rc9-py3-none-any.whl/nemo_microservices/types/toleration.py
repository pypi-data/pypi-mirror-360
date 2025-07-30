# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Toleration"]


class Toleration(BaseModel):
    effect: Optional[str] = None
    """Taint effect to match: "NoSchedule", "PreferNoSchedule", or "NoExecute" """

    key: Optional[str] = None
    """Taint key that the toleration applies to"""

    operator: Optional[str] = None
    """Operator: "Exists" or "Equal" """

    toleration_seconds: Optional[int] = FieldInfo(alias="tolerationSeconds", default=None)
    """Only for NoExecute; how long the toleration lasts"""

    value: Optional[str] = None
    """Value to match"""
