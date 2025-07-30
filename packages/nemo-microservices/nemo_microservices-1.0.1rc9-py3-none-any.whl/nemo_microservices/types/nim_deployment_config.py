# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from .._models import BaseModel

__all__ = ["NIMDeploymentConfig"]


class NIMDeploymentConfig(BaseModel):
    gpu: int
    """The number of GPUs needed for a deployment."""

    image_name: str
    """The name of the Docker image."""

    image_tag: str
    """The tag of the Docker image."""

    additional_envs: Optional[Dict[str, str]] = None
    """Additional environment variables to pass to the deployment."""

    disable_lora_support: Optional[bool] = None
    """
    **EXPERIMENTAL**: When true, prevents setting default values for
    NIM_PEFT_SOURCE, NIM_PEFT_REFRESH_INTERVAL and related service-level environment
    variables. This will load the NIM without support for LoRAs. This is required
    for some NIMs which do not support LoRAs. This feature is experimental and may
    change in future versions.
    """

    namespace: Optional[str] = None
    """The Kubernetes namespace of the deployment."""
