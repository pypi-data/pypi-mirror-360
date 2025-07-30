# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, TypedDict

__all__ = ["ClavataRailOptions"]


class ClavataRailOptions(TypedDict, total=False):
    policy: Required[str]
    """The policy alias to use when evaluating inputs or outputs."""

    labels: List[str]
    """
    A list of labels to match against the policy. If no labels are provided, the
    overall policy result will be returned. If labels are provided, only hits on the
    provided labels will be considered a hit.
    """
