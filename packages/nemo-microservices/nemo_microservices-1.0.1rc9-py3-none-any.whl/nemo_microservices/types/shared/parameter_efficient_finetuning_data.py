# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .finetuning_type import FinetuningType
from .lora_finetuning_data import LoraFinetuningData
from .p_tuning_finetuning_data import PTuningFinetuningData

__all__ = ["ParameterEfficientFinetuningData"]


class ParameterEfficientFinetuningData(BaseModel):
    finetuning_type: FinetuningType
    """The type of finetuning."""

    lora: Optional[LoraFinetuningData] = None
    """Data about a LoRA fine-tuned model."""

    p_tuning: Optional[PTuningFinetuningData] = None
    """Data about a p-tuned model."""
