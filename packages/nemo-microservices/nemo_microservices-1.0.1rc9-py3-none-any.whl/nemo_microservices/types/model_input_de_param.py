# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import TypedDict

from .model_spec_de_param import ModelSpecDeParam
from .prompt_data_de_param import PromptDataDeParam
from .model_artifact_de_param import ModelArtifactDeParam
from .shared_params.ownership import Ownership
from .guardrail_config_input_de_param import GuardrailConfigInputDeParam
from .shared_params.api_endpoint_data import APIEndpointData
from .parameter_efficient_finetuning_data_de_param import ParameterEfficientFinetuningDataDeParam

__all__ = ["ModelInputDeParam"]


class ModelInputDeParam(TypedDict, total=False):
    api_endpoint: APIEndpointData
    """Data about an API endpoint."""

    artifact: ModelArtifactDeParam
    """
    Data about a model artifact (a set of checkpoint files, configs, and other
    auxiliary info).

    The `files_url` field can point to a DataStore location.

    Example:

    - nds://models/rdinu/my-lora-customization

    The `rdinu/my-lora-customization` part above is the actual repository.

    If a specific revision needs to be referred, the HuggingFace syntax is used.

    - nds://models/rdinu/my-lora-customization@v1
    - nds://models/rdinu/my-lora-customization@8df79a8
    """

    base_model: Union[str, object]
    """Link to another model which is used as a base for the current model.

    Used in conjunction with `peft`, `prompt` and `guardrails`.
    """

    custom_fields: object
    """A set of custom fields that the user can define and use for various purposes."""

    description: str
    """The description of the entity."""

    guardrails: GuardrailConfigInputDeParam
    """A guardrail configuration"""

    name: str
    """The name of the identity.

    Must be unique inside the namespace. If not specified, it will be the same as
    the automatically generated id.
    """

    namespace: str
    """The if of the namespace of the entity.

    This can be missing for namespace entities or in deployments that don't use
    namespaces.
    """

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    peft: ParameterEfficientFinetuningDataDeParam
    """Data about a parameter-efficient finetuning."""

    project: str
    """The id of project associated with this entity."""

    prompt: PromptDataDeParam
    """Prompt engineering data."""

    spec: ModelSpecDeParam
    """Detailed spec about a model."""
