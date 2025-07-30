# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .reasoning_model_config import ReasoningModelConfig

__all__ = ["Model"]


class Model(TypedDict, total=False):
    engine: Required[str]

    type: Required[str]

    api_key_env_var: str
    """Optional environment variable with model's API Key. Do not include "$"."""

    mode: Literal["chat", "text"]
    """Whether the mode is 'text' completion or 'chat' completion.

    Allowed values are 'chat' or 'text'.
    """

    model: str
    """The name of the model.

    If not specified, it should be specified through the parameters attribute.
    """

    parameters: object

    reasoning_config: ReasoningModelConfig
    """
    Configuration for reasoning models/LLMs, including start and end tokens for
    reasoning traces.
    """
