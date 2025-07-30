# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime

from ..._models import BaseModel
from .ownership import Ownership
from .version_tag import VersionTag
from .config_data_input import ConfigDataInput

__all__ = ["GuardrailConfigInput"]


class GuardrailConfigInput(BaseModel):
    id: Optional[str] = None
    """The ID of the entity.

    With the exception of namespaces, this is always a semantically-prefixed
    base58-encoded uuid4 [<prefix>-base58(uuid4())].
    """

    created_at: Optional[datetime] = None
    """Timestamp for when the entity was created."""

    custom_fields: Optional[Dict[str, str]] = None
    """A set of custom fields that the user can define and use for various purposes."""

    data: Optional[ConfigDataInput] = None
    """Configuration object for the models and the rails."""

    description: Optional[str] = None
    """The description of the entity."""

    files_url: Optional[str] = None
    """The location where the artifact files are stored."""

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

    type_prefix: Optional[str] = None

    updated_at: Optional[datetime] = None
    """Timestamp for when the entity was last updated."""

    version_id: Optional[str] = None
    """A unique, immutable id for the version. This is similar to the commit hash."""

    version_tags: Optional[List[VersionTag]] = None
    """The list of version tags associated with this entity."""
