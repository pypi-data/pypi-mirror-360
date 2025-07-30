# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, TypedDict

from ..shared_params.ownership import Ownership
from ..shared_params.config_data_input import ConfigDataInput

__all__ = ["ConfigUpdateParams"]


class ConfigUpdateParams(TypedDict, total=False):
    namespace: Required[str]

    custom_fields: Dict[str, str]
    """A set of custom fields that the user can define and use for various purposes."""

    data: ConfigDataInput
    """Configuration object for the models and the rails."""

    description: str
    """The description of the entity."""

    files_url: str
    """The location where the artifact files are stored."""

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: str
    """The URN of the project associated with this entity."""

    schema_version: str
    """The version of the schema for the object. Internal use only."""
