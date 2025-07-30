# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, TypedDict

from ..shared.model_precision import ModelPrecision
from ..shared_params.ownership import Ownership
from ..training_pod_spec_input_param import TrainingPodSpecInputParam
from ..customization_training_option_param import CustomizationTrainingOptionParam
from .customization_training_option_removal_param import CustomizationTrainingOptionRemovalParam

__all__ = ["ConfigUpdateParams"]


class ConfigUpdateParams(TypedDict, total=False):
    namespace: Required[str]

    add_training_options: Iterable[CustomizationTrainingOptionParam]
    """
    List of training options to add in the existing training options for the config.
    """

    chat_prompt_template: str
    """
    Chat Prompt Template to apply to the model to make it compatible with chat
    datasets
    """

    custom_fields: Dict[str, str]
    """A set of custom fields that the user can define and use for various purposes."""

    dataset_schemas: Iterable[object]
    """Descriptions of the expected formats of the datasets uploaded."""

    description: str
    """The description of the entity."""

    max_seq_length: int
    """The largest context used for training.

    Datasets are truncated based on the maximum sequence length.
    """

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    pod_spec: TrainingPodSpecInputParam
    """
    Additional parameters to ensure these training jobs get run on the appropriate
    hardware.
    """

    project: str
    """The URN of the project associated with this entity."""

    prompt_template: str
    """Prompt template used to extract keys from the dataset.

    E.g. prompt_template='{input} {output}', and sample looks like '{\"input\": \"Q:
    2x2 A:\", \"output\": \"4\"}' then the model sees 'Q: 2x2 A: 4'
    """

    remove_training_options: Iterable[CustomizationTrainingOptionRemovalParam]
    """
    List of training options to remove from the existing training options for the
    config.
    """

    training_options: Iterable[CustomizationTrainingOptionParam]
    """Resource configuration for each training option for the model."""

    training_precision: ModelPrecision
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
