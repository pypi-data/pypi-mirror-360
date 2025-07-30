# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union

from ..._models import BaseModel

__all__ = ["ValidationError"]


class ValidationError(BaseModel):
    loc: List[Union[str, int]]

    msg: str

    type: str
