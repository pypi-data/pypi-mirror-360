# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from .._models import BaseModel
from .shared.ownership import Ownership
from .task_result_output import TaskResultOutput
from .group_result_output import GroupResultOutput

__all__ = ["EvaluationResult"]


class EvaluationResult(BaseModel):
    job: str
    """The evaluation job associated with this results instance."""

    id: Optional[str] = None
    """The ID of the entity.

    With the exception of namespaces, this is always a semantically-prefixed
    base58-encoded uuid4 [<prefix>-base58(uuid4())].
    """

    created_at: Optional[datetime] = None
    """Timestamp for when the entity was created."""

    custom_fields: Optional[Dict[str, str]] = None
    """A set of custom fields that the user can define and use for various purposes."""

    description: Optional[str] = None
    """The description of the entity."""

    files_url: Optional[str] = None
    """The place for the output files, if any."""

    groups: Optional[Dict[str, GroupResultOutput]] = None
    """The results at the group-level."""

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

    tasks: Optional[Dict[str, TaskResultOutput]] = None
    """The results at the task-level."""

    updated_at: Optional[datetime] = None
    """Timestamp for when the entity was last updated."""
