# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import TypedDict

from .task_result_input_param import TaskResultInputParam
from ..shared_params.ownership import Ownership
from .group_result_input_param import GroupResultInputParam

__all__ = ["ResultUpdateParams"]


class ResultUpdateParams(TypedDict, total=False):
    custom_fields: Dict[str, str]
    """A set of custom fields that the user can define and use for various purposes."""

    description: str
    """The description of the entity."""

    files_url: str
    """The place for the output files, if any."""

    groups: Dict[str, GroupResultInputParam]
    """The results at the group-level."""

    job: str
    """The evaluation job associated with this results instance."""

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

    tasks: Dict[str, TaskResultInputParam]
    """The results at the task-level."""
