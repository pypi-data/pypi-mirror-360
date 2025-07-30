# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import TypedDict

from .shared_params.ownership import Ownership

__all__ = ["NamespaceCreateParams"]


class NamespaceCreateParams(TypedDict, total=False):
    id: str
    """The ID of the entity.

    With the exception of namespaces, this is always a semantically-prefixed
    base58-encoded uuid4 [<prefix>-base58(uuid4())].
    """

    custom_fields: Dict[str, str]
    """A set of custom fields that the user can define and use for various purposes."""

    description: str
    """The description of the entity."""

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: str
    """The URN of the project associated with this entity."""
