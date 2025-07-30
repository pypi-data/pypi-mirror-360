# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from .._compat import PYDANTIC_V2, ConfigDict
from .._models import BaseModel
from .target_status import TargetStatus
from .shared.ownership import Ownership
from .shared.model_precision import ModelPrecision

__all__ = ["CustomizationTarget"]


class CustomizationTarget(BaseModel):
    model_path: str
    """Path to the model checkpoints to use for training.

    Absolute path or local path from the models cache
    """

    num_parameters: int
    """Number of parameters used for training the model"""

    precision: ModelPrecision
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

    id: Optional[str] = None
    """The ID of the entity.

    With the exception of namespaces, this is always a semantically-prefixed
    base58-encoded uuid4 [<prefix>-base58(uuid4())].
    """

    base_model: Optional[str] = None
    """
    Default to being the same as the the configuration entry name, maps to the name
    in NIM
    """

    created_at: Optional[datetime] = None
    """Timestamp for when the entity was created."""

    custom_fields: Optional[Dict[str, str]] = None
    """A set of custom fields that the user can define and use for various purposes."""

    description: Optional[str] = None
    """The description of the entity."""

    enabled: Optional[bool] = None
    """Enable the model for training jobs"""

    hf_endpoint: Optional[str] = None
    """Configure HuggingFace Hub base URL.

    Defaults to NeMo Data Store. Set value as "https://huggingface.co" to download
    model_uri from HuggingFace.
    """

    model_uri: Optional[str] = None
    """The URI of the model to download to the model cache at the model_path directory.

    To download from NGC, specify ngc://org/optional-team/model-name:version. To
    download from Nemo Data Store, specify hf://namespace/model-name@checkpoint-name
    """

    name: Optional[str] = None
    """The name of the entity.

    Must be unique inside the namespace. If not specified, it will be the same as
    the automatically generated id.
    """

    namespace: Optional[str] = None
    """The namespace of the entity.

    This can be missing for namespace entities or in deployments that don't use
    namespaces.
    """

    ownership: Optional[Ownership] = None
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: Optional[str] = None
    """The URN of the project associated with this entity."""

    schema_version: Optional[str] = None
    """The version of the schema for the object. Internal use only."""

    status: Optional[TargetStatus] = None
    """Normalized statuses for targets.

    - **CREATED**: The target is created, but not yet scheduled.
    - **PENDING**: The target is waiting for resource allocation.
    - **DOWNLOADING**: The target is downloading.
    - **FAILED**: The target failed to execute and terminated.
    - **READY**: The target is ready to be used.
    - **CANCELLED**: The target download was cancelled.
    - **UNKNOWN**: The target status is unknown.
    - **DELETED**: The target is deleted.
    - **DELETING**: The target is currently being deleted.
    - **DELETE_FAILED**: Failed to delete the target.
    """

    tokenizer: Optional[object] = None
    """Overrides for the model tokenizer"""

    type_prefix: Optional[str] = None
    """The type prefix of the entity ID.

    If not specified, it will be inferred from the entity type name, but this will
    likely result in long prefixes.
    """

    updated_at: Optional[datetime] = None
    """Timestamp for when the entity was last updated."""

    if PYDANTIC_V2:
        # allow fields with a `model_` prefix
        model_config = ConfigDict(protected_namespaces=tuple())
