# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .wand_b_integration_data import WandBIntegrationData

__all__ = ["WandBIntegration"]


class WandBIntegration(BaseModel):
    wandb: WandBIntegrationData
    """
    Weights & Biases (W&B) configuration that is mapped to W&B python sdk settings:
    https://docs.wandb.ai/ref/python/init
    """

    type: Optional[Literal["wandb"]] = None
