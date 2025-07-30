# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from typing_extensions import TypedDict

from .shared_params.ownership import Ownership
from .shared_params.model_spec import ModelSpec
from .shared_params.prompt_data import PromptData
from .shared_params.model_artifact import ModelArtifact
from .shared_params.api_endpoint_data import APIEndpointData
from .shared_params.guardrail_config_input import GuardrailConfigInput
from .shared_params.parameter_efficient_finetuning_data import ParameterEfficientFinetuningData

__all__ = ["ModelInputParam"]


class ModelInputParam(TypedDict, total=False):
    api_endpoint: APIEndpointData
    """Data about an API endpoint."""

    artifact: ModelArtifact
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
    """Link to another model which is used as a base for the current model."""

    custom_fields: Dict[str, str]
    """A set of custom fields that the user can define and use for various purposes."""

    description: str
    """The description of the entity."""

    guardrails: GuardrailConfigInput
    """A guardrail configuration"""

    name: str
    """The name of the entity.

    Must be unique inside the namespace. If not specified, it will be the same as
    the automatically generated id.
    """

    namespace: str
    """The namespace of the entity.

    This can be missing for namespace entities or in deployments that don't use
    namespaces.
    """

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    peft: ParameterEfficientFinetuningData
    """Data about a parameter-efficient finetuning."""

    project: str
    """The URN of the project associated with this entity."""

    prompt: PromptData
    """Prompt engineering data."""

    spec: ModelSpec
    """Detailed specification about a model."""
