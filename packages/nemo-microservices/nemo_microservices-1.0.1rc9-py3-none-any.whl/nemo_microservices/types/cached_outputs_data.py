# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["CachedOutputsData"]


class CachedOutputsData(BaseModel):
    files_url: str
    """The files URL of the cached outputs."""
