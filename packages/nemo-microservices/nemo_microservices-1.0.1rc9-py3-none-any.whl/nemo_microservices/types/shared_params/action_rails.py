# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import TypedDict

__all__ = ["ActionRails"]


class ActionRails(TypedDict, total=False):
    instant_actions: List[str]
    """The names of all actions which should finish instantly."""
