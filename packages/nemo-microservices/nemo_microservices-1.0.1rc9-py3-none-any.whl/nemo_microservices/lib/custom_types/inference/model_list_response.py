# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["ModelListResponse", "Data"]


class Data(BaseModel):
    id: str

    created: int

    object: Optional[Literal["model"]] = None

    owned_by: str


class ModelListResponse(BaseModel):
    objects: Optional[Literal["list"]] = None

    data: List[Data]
