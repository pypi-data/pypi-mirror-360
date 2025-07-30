# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["ExternalEndpointConfig"]


class ExternalEndpointConfig(BaseModel):
    host_url: str
    """The external host URL."""

    api_key: Optional[str] = None
    """The API key that should be used to access the endpoint."""

    enabled_models: Optional[List[str]] = None
