# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["ActionRails"]


class ActionRails(BaseModel):
    instant_actions: Optional[List[str]] = None
    """The names of all actions which should finish instantly."""
