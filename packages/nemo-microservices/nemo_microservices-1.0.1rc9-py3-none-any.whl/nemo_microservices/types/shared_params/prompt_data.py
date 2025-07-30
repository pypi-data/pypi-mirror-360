# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .inference_params import InferenceParams
from .reasoning_params import ReasoningParams

__all__ = ["PromptData"]


class PromptData(TypedDict, total=False):
    icl_few_shot_examples: str
    """
    Example input-output pairs that guide the model in understanding the desired
    task format and behavior.
    """

    inference_params: InferenceParams
    """Parameters that influence the inference of a model."""

    reasoning_params: ReasoningParams
    """Custom settings that control the model's reasoning behavior."""

    system_prompt: str
    """
    Initial instructions that define the model's role and behavior for the
    conversation.
    """

    system_prompt_template: str
    """
    The template which will be used to compile the final prompt used for prompting
    the LLM. Currently supports only {{icl_few_shot_examples}}
    """
