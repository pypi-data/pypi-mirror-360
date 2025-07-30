# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .wand_b_integration_data_param import WandBIntegrationDataParam

__all__ = ["WandBIntegrationParam"]


class WandBIntegrationParam(TypedDict, total=False):
    wandb: Required[WandBIntegrationDataParam]
    """
    Weights & Biases (W&B) configuration that is mapped to W&B python sdk settings:
    https://docs.wandb.ai/ref/python/init
    """

    type: Literal["wandb"]
