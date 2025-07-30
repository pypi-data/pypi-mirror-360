# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from ..shared.model_precision import ModelPrecision
from ..customization_training_option import CustomizationTrainingOption

__all__ = ["CustomizationConfigJobOutputValue"]


class CustomizationConfigJobOutputValue(BaseModel):
    base_model: str
    """The base model that will be customized."""

    max_seq_length: int

    precision: ModelPrecision
    """Type of model precision.

    ## Values

    - `"int8"` - 8-bit integer precision
    - `"bf16"` - Brain floating point precision
    - `"fp16"` - 16-bit floating point precision
    - `"fp32"` - 32-bit floating point precision
    - `"fp8-mixed"` - Mixed 8-bit floating point precision available on Hopper and
      later architectures.
    - `"bf16-mixed"` - Mixed Brain floating point precision
    """

    training_option: CustomizationTrainingOption
    """Resource configuration for model training.

    Specifies the hardware and parallelization settings for training.
    """

    dataset_schema: Optional[object] = None
    """Description of the expected format of the dataset"""

    prompt_template: Optional[str] = None
    """Prompt template used to extract keys from the dataset.

    E.g. prompt_template='{input} {output}', and sample looks like '{\"input\": \"Q:
    2x2 A:\", \"output\": \"4\"}' then the model sees 'Q: 2x2 A: 4'
    """
