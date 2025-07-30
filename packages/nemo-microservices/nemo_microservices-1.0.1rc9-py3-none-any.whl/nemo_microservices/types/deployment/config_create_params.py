# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import TypeAlias, TypedDict

from ..model_input_de_param import ModelInputDeParam
from ..shared_params.ownership import Ownership
from ..nim_deployment_config_param import NIMDeploymentConfigParam
from ..external_endpoint_config_param import ExternalEndpointConfigParam

__all__ = ["ConfigCreateParams", "Model"]


class ConfigCreateParams(TypedDict, total=False):
    custom_fields: object
    """A set of custom fields that the user can define and use for various purposes."""

    description: str
    """The description of the entity."""

    external_endpoint: ExternalEndpointConfigParam
    """Configuration for an external endpoint."""

    model: Model
    """The model to be deployed."""

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

    nim_deployment: NIMDeploymentConfigParam
    """Configuration for a NIM deployment."""

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: str
    """The id of project associated with this entity."""


Model: TypeAlias = Union[str, ModelInputDeParam]
