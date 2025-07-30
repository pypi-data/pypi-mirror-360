# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .reasoning_model_config import ReasoningModelConfig

__all__ = ["Model"]


class Model(BaseModel):
    engine: str

    type: str

    api_key_env_var: Optional[str] = None
    """Optional environment variable with model's API Key. Do not include "$"."""

    mode: Optional[Literal["chat", "text"]] = None
    """Whether the mode is 'text' completion or 'chat' completion.

    Allowed values are 'chat' or 'text'.
    """

    model: Optional[str] = None
    """The name of the model.

    If not specified, it should be specified through the parameters attribute.
    """

    parameters: Optional[object] = None

    reasoning_config: Optional[ReasoningModelConfig] = None
    """
    Configuration for reasoning models/LLMs, including start and end tokens for
    reasoning traces.
    """
