# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TolerationParam"]


class TolerationParam(TypedDict, total=False):
    effect: str
    """Taint effect to match: "NoSchedule", "PreferNoSchedule", or "NoExecute" """

    key: str
    """Taint key that the toleration applies to"""

    operator: str
    """Operator: "Exists" or "Equal" """

    toleration_seconds: Annotated[int, PropertyInfo(alias="tolerationSeconds")]
    """Only for NoExecute; how long the toleration lasts"""

    value: str
    """Value to match"""
