# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .finetuning_type_de import FinetuningTypeDe
from .shared_params.lora_finetuning_data import LoraFinetuningData
from .shared_params.p_tuning_finetuning_data import PTuningFinetuningData

__all__ = ["ParameterEfficientFinetuningDataDeParam"]


class ParameterEfficientFinetuningDataDeParam(TypedDict, total=False):
    finetuning_type: Required[FinetuningTypeDe]
    """The type of finetuning."""

    lora: LoraFinetuningData
    """Data about a LoRA fine-tuned model."""

    p_tuning: PTuningFinetuningData
    """Data about a p-tuned model."""
