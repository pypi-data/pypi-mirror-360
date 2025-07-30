# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import TypeAlias, TypedDict

from .generation_options_param import GenerationOptionsParam
from .shared_params.config_data_input import ConfigDataInput

__all__ = ["GuardrailsDataInputParam", "Config"]

Config: TypeAlias = Union[str, ConfigDataInput]


class GuardrailsDataInputParam(TypedDict, total=False):
    config: Config
    """The id of the configuration or its dict representation to be used."""

    config_id: str
    """The id of the configuration to be used."""

    config_ids: List[str]
    """The list of configuration ids to be used.

    If set, the configurations will be combined.
    """

    context: object
    """Additional context data to be added to the conversation."""

    options: GenerationOptionsParam
    """A set of options that should be applied during a generation.

    The GenerationOptions control various things such as what rails are enabled,
    additional parameters for the main LLM, whether the rails should be enforced or
    ran in parallel, what to be included in the generation log, etc.
    """

    return_choice: bool
    """If set, guardrails data will be included as a JSON in the choices array."""

    state: object
    """A state object that should be used to continue the interaction."""

    stream: bool
    """If set, partial message deltas will be sent, like in ChatGPT.

    Tokens will be sent as data-only server-sent events as they become available,
    with the stream terminated by a data: [DONE] message.
    """
