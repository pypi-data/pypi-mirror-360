# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, TypedDict

__all__ = ["ExternalEndpointConfigParam"]


class ExternalEndpointConfigParam(TypedDict, total=False):
    host_url: Required[str]
    """The external host URL."""

    api_key: str
    """The API key that should be used to access the endpoint."""

    enabled_models: List[str]
