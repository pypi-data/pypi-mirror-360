# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, TypedDict

__all__ = ["NIMDeploymentConfigParam"]


class NIMDeploymentConfigParam(TypedDict, total=False):
    gpu: Required[int]
    """The number of GPUs needed for a deployment."""

    image_name: Required[str]
    """The name of the Docker image."""

    image_tag: Required[str]
    """The tag of the Docker image."""

    additional_envs: Dict[str, str]
    """Additional environment variables to pass to the deployment."""

    disable_lora_support: bool
    """
    **EXPERIMENTAL**: When true, prevents setting default values for
    NIM_PEFT_SOURCE, NIM_PEFT_REFRESH_INTERVAL and related service-level environment
    variables. This will load the NIM without support for LoRAs. This is required
    for some NIMs which do not support LoRAs. This feature is experimental and may
    change in future versions.
    """

    namespace: str
    """The Kubernetes namespace of the deployment."""
