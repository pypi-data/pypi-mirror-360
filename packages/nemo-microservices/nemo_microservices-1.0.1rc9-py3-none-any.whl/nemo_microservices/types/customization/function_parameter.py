# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Optional

from ..._models import BaseModel

__all__ = ["FunctionParameter"]


class FunctionParameter(BaseModel):
    type: str
    """The type of the parameter provided."""

    description: Optional[str] = None
    """The description of this parameter."""

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...
