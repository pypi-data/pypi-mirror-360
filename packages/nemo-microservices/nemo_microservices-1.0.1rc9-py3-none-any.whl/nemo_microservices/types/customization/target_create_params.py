# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ..shared.model_precision import ModelPrecision

__all__ = ["TargetCreateParams"]


class TargetCreateParams(TypedDict, total=False):
    num_parameters: Required[int]
    """Number of parameters used for training the model"""

    precision: Required[ModelPrecision]
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

    base_model: str
    """
    Default to being the same as the the configuration entry name, maps to the name
    in NIM
    """

    description: str
    """The description of the entity."""

    enabled: bool
    """Enable the model for training jobs"""

    hf_endpoint: str
    """Configure the Hub base URL.

    Defaults to NeMo Data Store. Set value as "https://huggingface.co" to download
    model_uri from HuggingFace.
    """

    model_path: str
    """Path to the model checkpoints to use for training.

    Absolute path or local path from the models cache
    """

    model_uri: str
    """The URI of the model to download to the model cache at the model_path directory.

    To download from NGC, specify ngc://org/optional-team/model-name:version. To
    download from Nemo Data Store, specify hf://namespace/model-name@checkpoint-name
    """

    name: str
    """The name of the entity.

    Must be unique inside the namespace. If not specified, it will be the same as
    the automatically generated id.
    """

    namespace: str
    """The namespace of the entity.

    You can omit this field for namespace entities or in deployments that don't use
    namespaces.
    """

    project: str
    """The URN of the project associated with this entity."""

    tokenizer: object
    """Overrides for the model tokenizer"""
