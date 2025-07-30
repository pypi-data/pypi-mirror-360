# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["CachedOutputsDataParam"]


class CachedOutputsDataParam(TypedDict, total=False):
    files_url: Required[str]
    """The files URL of the cached outputs."""
