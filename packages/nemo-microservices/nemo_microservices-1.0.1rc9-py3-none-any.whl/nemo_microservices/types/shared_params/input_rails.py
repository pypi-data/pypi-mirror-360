# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import TypedDict

__all__ = ["InputRails"]


class InputRails(TypedDict, total=False):
    flows: List[str]
    """The names of all the flows that implement input rails."""
