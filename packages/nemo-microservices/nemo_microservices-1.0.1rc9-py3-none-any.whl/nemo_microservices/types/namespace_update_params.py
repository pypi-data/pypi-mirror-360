# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import TypedDict

from .shared_params.ownership import Ownership

__all__ = ["NamespaceUpdateParams"]


class NamespaceUpdateParams(TypedDict, total=False):
    custom_fields: Dict[str, str]
    """A set of custom fields that the user can define and use for various purposes."""

    description: str
    """The description of the entity."""

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

    project: str
    """The URN of the project associated with this entity."""

    schema_version: str
    """The version of the schema for the object. Internal use only."""
