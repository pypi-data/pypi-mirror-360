# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["WandBIntegrationData"]


class WandBIntegrationData(BaseModel):
    entity: Optional[str] = None
    """The username or team name under which the run will be logged."""

    notes: Optional[str] = None
    """A description of the run"""

    project: Optional[str] = None
    """The name of the project under which this run will be logged."""

    tags: Optional[List[str]] = None
    """A list of tags to label this run."""
