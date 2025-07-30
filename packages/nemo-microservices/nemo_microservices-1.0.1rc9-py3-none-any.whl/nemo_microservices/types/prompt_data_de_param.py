# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .shared_params.inference_params import InferenceParams

__all__ = ["PromptDataDeParam"]


class PromptDataDeParam(TypedDict, total=False):
    icl_few_shot_examples: str
    """A string including a set of examples. These are pre-pended to the prompt."""

    inference_params: InferenceParams
    """Parameters that influence the inference of a model."""

    system_prompt: str
    """The system prompt that should be applied during inference."""

    system_prompt_template: str
    """
    The template which will be used to compile the final prompt used for prompting
    the LLM. Currently supports only {{icl_few_shot_examples}}
    """
