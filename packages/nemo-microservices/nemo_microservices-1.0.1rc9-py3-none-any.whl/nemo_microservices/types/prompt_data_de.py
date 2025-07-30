# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .shared.inference_params import InferenceParams

__all__ = ["PromptDataDe"]


class PromptDataDe(BaseModel):
    icl_few_shot_examples: Optional[str] = None
    """A string including a set of examples. These are pre-pended to the prompt."""

    inference_params: Optional[InferenceParams] = None
    """Parameters that influence the inference of a model."""

    system_prompt: Optional[str] = None
    """The system prompt that should be applied during inference."""

    system_prompt_template: Optional[str] = None
    """
    The template which will be used to compile the final prompt used for prompting
    the LLM. Currently supports only {{icl_few_shot_examples}}
    """
