# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .function_parameters import FunctionParameters

__all__ = ["FunctionSchemaOutput"]


class FunctionSchemaOutput(BaseModel):
    description: str
    """Description of what the function does."""

    name: str
    """Name of the function."""

    parameters: FunctionParameters
    """Parameters schema for the function."""

    strict: Optional[bool] = None
    """Whether the verification is in strict mode."""
