# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import TypedDict

__all__ = ["WandBIntegrationDataParam"]


class WandBIntegrationDataParam(TypedDict, total=False):
    entity: str
    """The username or team name under which the run will be logged."""

    notes: str
    """A description of the run"""

    project: str
    """The name of the project under which this run will be logged."""

    tags: List[str]
    """A list of tags to label this run."""
