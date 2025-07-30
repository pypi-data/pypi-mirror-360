# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._compat import PYDANTIC_V2, ConfigDict
from ..._models import BaseModel
from .api_endpoint_format import APIEndpointFormat

__all__ = ["APIEndpointData"]


class APIEndpointData(BaseModel):
    model_id: str
    """The id of the model. How this is used depends on the API endpoint format."""

    url: str
    """The API endpoint URL."""

    api_key: Optional[str] = None
    """The API key that should be used to access the endpoint."""

    format: Optional[APIEndpointFormat] = None
    """API endpoint format.

    The format dictates the structure of the request and response.

    ## Values

    - `"nim"` - NVIDIA NIM format
    - `"openai"` - OpenAI format
    - `"lama_stack"` - Llama Stack format
    """

    if PYDANTIC_V2:
        # allow fields with a `model_` prefix
        model_config = ConfigDict(protected_namespaces=tuple())
