# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .validation_error import ValidationError

__all__ = ["HTTPValidationError"]


class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]] = None
