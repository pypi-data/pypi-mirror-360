# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["ClavataRailOptions"]


class ClavataRailOptions(BaseModel):
    policy: str
    """The policy alias to use when evaluating inputs or outputs."""

    labels: Optional[List[str]] = None
    """
    A list of labels to match against the policy. If no labels are provided, the
    overall policy result will be returned. If labels are provided, only hits on the
    provided labels will be considered a hit.
    """
