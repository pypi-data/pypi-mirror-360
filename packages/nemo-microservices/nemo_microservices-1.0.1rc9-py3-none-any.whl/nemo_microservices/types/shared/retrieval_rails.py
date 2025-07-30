# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["RetrievalRails"]


class RetrievalRails(BaseModel):
    flows: Optional[List[str]] = None
    """The names of all the flows that implement retrieval rails."""
