# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ..shared.api_endpoint_format import APIEndpointFormat

__all__ = ["APIEndpointData"]


class APIEndpointData(TypedDict, total=False):
    model_id: Required[str]
    """The id of the model. How this is used depends on the API endpoint format."""

    url: Required[str]
    """The API endpoint URL."""

    api_key: str
    """The API key that should be used to access the endpoint."""

    format: APIEndpointFormat
    """API endpoint format.

    The format dictates the structure of the request and response.

    ## Values

    - `"nim"` - NVIDIA NIM format
    - `"openai"` - OpenAI format
    - `"lama_stack"` - Llama Stack format
    """
