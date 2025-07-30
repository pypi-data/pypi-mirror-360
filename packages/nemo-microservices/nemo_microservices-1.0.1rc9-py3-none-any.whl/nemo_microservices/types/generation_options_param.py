# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import TypedDict

from .generation_log_options_param import GenerationLogOptionsParam
from .generation_rails_options_param import GenerationRailsOptionsParam

__all__ = ["GenerationOptionsParam"]


class GenerationOptionsParam(TypedDict, total=False):
    llm_output: bool
    """Whether the response should also include any custom LLM output."""

    llm_params: object
    """Additional parameters that should be used for the LLM call"""

    log: GenerationLogOptionsParam
    """Options for what should be included in the generation log."""

    output_vars: Union[bool, List[str]]
    """Whether additional context information should be returned.

    When True is specified, the whole context is returned. Otherwise, a list of key
    names can be specified.
    """

    rails: GenerationRailsOptionsParam
    """Options for what rails should be used during the generation."""
