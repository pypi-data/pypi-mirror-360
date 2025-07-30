# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Required, TypeAlias, TypedDict

from ..shared_params.ownership import Ownership
from ..deployment_config_input_param import DeploymentConfigInputParam

__all__ = ["ModelDeploymentCreateParams", "Config"]


class ModelDeploymentCreateParams(TypedDict, total=False):
    config: Required[Config]
    """The deployment configuration."""

    async_enabled: bool
    """Whether the async mode is enabled."""

    custom_fields: object
    """A set of custom fields that the user can define and use for various purposes."""

    description: str
    """The description of the entity."""

    models: List[str]
    """The models served by this deployment."""

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

    project: str
    """The id of project associated with this entity."""


Config: TypeAlias = Union[str, DeploymentConfigInputParam]
