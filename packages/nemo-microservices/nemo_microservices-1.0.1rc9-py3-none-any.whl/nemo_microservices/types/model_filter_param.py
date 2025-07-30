# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import TypeAlias, TypedDict

from .base_model_filter_param import BaseModelFilterParam
from .created_at_filter_param import CreatedAtFilterParam
from .model_peft_filter_param import ModelPeftFilterParam

__all__ = ["ModelFilterParam", "BaseModel", "Peft"]

BaseModel: TypeAlias = Union[BaseModelFilterParam, str]

Peft: TypeAlias = Union[ModelPeftFilterParam, bool]


class ModelFilterParam(TypedDict, total=False):
    base_model: BaseModel
    """Filter models based on base model properties."""

    created_at: CreatedAtFilterParam
    """Filter entities based on creation date."""

    namespace: str
    """Filter by namespace id."""

    peft: Peft
    """Filter models with Parameter Efficient Fine-tuning."""

    project: str
    """Filter by project name."""

    prompt: bool
    """Filter models with prompt engineering data."""
