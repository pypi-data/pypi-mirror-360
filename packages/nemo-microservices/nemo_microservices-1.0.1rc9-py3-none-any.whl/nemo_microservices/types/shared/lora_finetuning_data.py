# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["LoraFinetuningData"]


class LoraFinetuningData(BaseModel):
    alpha: int
    """
    A scaling factor that controls how much influence the LoRA adaptations have on
    the base model's behavior. The alpha parameter should typically be set to dim or
    0.5 \\** dim as the actual scaling applied in the training loop is alpha / dim.
    """

    apply_lora_to_mlp: bool
    """
    Controls whether to adapt the model's feed-forward neural network layers using
    LoRA.
    """

    apply_lora_to_output: bool
    """Controls whether to adapt the model's final output layer using LoRA."""
