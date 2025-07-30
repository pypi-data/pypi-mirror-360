# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .inference_params import InferenceParams
from .reasoning_params import ReasoningParams

__all__ = ["PromptData"]


class PromptData(BaseModel):
    icl_few_shot_examples: Optional[str] = None
    """
    Example input-output pairs that guide the model in understanding the desired
    task format and behavior.
    """

    inference_params: Optional[InferenceParams] = None
    """Parameters that influence the inference of a model."""

    reasoning_params: Optional[ReasoningParams] = None
    """Custom settings that control the model's reasoning behavior."""

    system_prompt: Optional[str] = None
    """
    Initial instructions that define the model's role and behavior for the
    conversation.
    """

    system_prompt_template: Optional[str] = None
    """
    The template which will be used to compile the final prompt used for prompting
    the LLM. Currently supports only {{icl_few_shot_examples}}
    """
