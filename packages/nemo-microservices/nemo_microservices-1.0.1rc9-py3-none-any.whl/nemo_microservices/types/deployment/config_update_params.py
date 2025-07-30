# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, TypeAlias, TypedDict

from ..model_input_de_param import ModelInputDeParam
from ..shared_params.ownership import Ownership
from ..nim_deployment_config_param import NIMDeploymentConfigParam
from ..external_endpoint_config_param import ExternalEndpointConfigParam

__all__ = ["ConfigUpdateParams", "Model"]


class ConfigUpdateParams(TypedDict, total=False):
    namespace: Required[str]

    custom_fields: object
    """A set of custom fields that the user can define and use for various purposes."""

    description: str
    """The description of the entity."""

    external_endpoint: ExternalEndpointConfigParam
    """Configuration for an external endpoint."""

    model: Model
    """The model to be deployed."""

    nim_deployment: NIMDeploymentConfigParam
    """Configuration for a NIM deployment."""

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: str
    """The id of project associated with this entity."""

    schema_version: str
    """The version of the schema for the object. Internal use only."""


Model: TypeAlias = Union[str, ModelInputDeParam]
