# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["VersionTag"]


class VersionTag(TypedDict, total=False):
    name: Required[str]
    """The name of the version.

    Typically should be kept lower case, no space, no '/', no `@`.
    """

    created_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Timestamp for when the version tag was created."""

    created_by: str
    """The ID of the user that created this entity."""
