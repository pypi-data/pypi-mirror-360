# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .shared_params.ownership import Ownership

__all__ = ["GuardrailConfigInputDeParam"]


class GuardrailConfigInputDeParam(TypedDict, total=False):
    files_url: Required[str]
    """The location where the artifact files are stored."""

    custom_fields: object
    """A set of custom fields that the user can define and use for various purposes."""

    description: str
    """The description of the entity."""

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
