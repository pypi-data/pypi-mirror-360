# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .finetuning_type_de import FinetuningTypeDe
from .shared.lora_finetuning_data import LoraFinetuningData
from .shared.p_tuning_finetuning_data import PTuningFinetuningData

__all__ = ["ParameterEfficientFinetuningDataDe"]


class ParameterEfficientFinetuningDataDe(BaseModel):
    finetuning_type: FinetuningTypeDe
    """The type of finetuning."""

    lora: Optional[LoraFinetuningData] = None
    """Data about a LoRA fine-tuned model."""

    p_tuning: Optional[PTuningFinetuningData] = None
    """Data about a p-tuned model."""
