# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["LabelSelectorRequirement"]


class LabelSelectorRequirement(BaseModel):
    key: str

    operator: Literal["In", "NotIn", "Exists", "DoesNotExist", "Gt", "Lt"]

    values: Optional[List[str]] = None
