# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from datetime import datetime

from .._models import BaseModel
from .model_spec_de import ModelSpecDe
from .prompt_data_de import PromptDataDe
from .shared.ownership import Ownership
from .model_artifact_de import ModelArtifactDe
from .guardrail_config_de import GuardrailConfigDe
from .shared.api_endpoint_data import APIEndpointData
from .parameter_efficient_finetuning_data_de import ParameterEfficientFinetuningDataDe

__all__ = ["ModelOutputDe"]


class ModelOutputDe(BaseModel):
    api_endpoint: Optional[APIEndpointData] = None
    """Data about an API endpoint."""

    artifact: Optional[ModelArtifactDe] = None
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

    base_model: Union[str, object, None] = None
    """Link to another model which is used as a base for the current model.

    Used in conjunction with `peft`, `prompt` and `guardrails`.
    """

    created_at: Optional[datetime] = None
    """Timestamp for when the entity was created."""

    custom_fields: Optional[object] = None
    """A set of custom fields that the user can define and use for various purposes."""

    description: Optional[str] = None
    """The description of the entity."""

    guardrails: Optional[GuardrailConfigDe] = None
    """A guardrail configuration"""

    name: Optional[str] = None
    """The name of the identity.

    Must be unique inside the namespace. If not specified, it will be the same as
    the automatically generated id.
    """

    namespace: Optional[str] = None
    """The if of the namespace of the entity.

    This can be missing for namespace entities or in deployments that don't use
    namespaces.
    """

    ownership: Optional[Ownership] = None
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    peft: Optional[ParameterEfficientFinetuningDataDe] = None
    """Data about a parameter-efficient finetuning."""

    project: Optional[str] = None
    """The id of project associated with this entity."""

    prompt: Optional[PromptDataDe] = None
    """Prompt engineering data."""

    schema_version: Optional[str] = None
    """The version of the schema for the object. Internal use only."""

    spec: Optional[ModelSpecDe] = None
    """Detailed spec about a model."""

    updated_at: Optional[datetime] = None
    """Timestamp for when the entity was last updated."""
