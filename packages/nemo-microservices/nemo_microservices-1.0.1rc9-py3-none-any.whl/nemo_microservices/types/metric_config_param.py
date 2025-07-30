# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["MetricConfigParam"]


class MetricConfigParam(TypedDict, total=False):
    type: Required[str]
    """The type of the metric."""

    params: object
    """Specific parameters for the metric."""
