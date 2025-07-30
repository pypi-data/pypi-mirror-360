# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["ChoiceDeltaFunctionCall"]


class ChoiceDeltaFunctionCall(BaseModel):
    arguments: Optional[str] = None

    name: Optional[str] = None
