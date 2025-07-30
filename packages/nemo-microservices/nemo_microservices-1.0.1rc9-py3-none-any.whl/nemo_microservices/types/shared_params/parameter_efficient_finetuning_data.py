# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .lora_finetuning_data import LoraFinetuningData
from ..shared.finetuning_type import FinetuningType
from .p_tuning_finetuning_data import PTuningFinetuningData

__all__ = ["ParameterEfficientFinetuningData"]


class ParameterEfficientFinetuningData(TypedDict, total=False):
    finetuning_type: Required[FinetuningType]
    """The type of finetuning."""

    lora: LoraFinetuningData
    """Data about a LoRA fine-tuned model."""

    p_tuning: PTuningFinetuningData
    """Data about a p-tuned model."""
