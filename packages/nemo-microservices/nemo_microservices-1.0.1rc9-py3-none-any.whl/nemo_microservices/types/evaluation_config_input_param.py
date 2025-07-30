# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, TypedDict

from .evaluation_params_param import EvaluationParamsParam
from .shared_params.ownership import Ownership
from .task_config_input_param import TaskConfigInputParam
from .group_config_input_param import GroupConfigInputParam

__all__ = ["EvaluationConfigInputParam"]


class EvaluationConfigInputParam(TypedDict, total=False):
    type: Required[str]
    """
    The type of the evaluation, e.g., 'mmlu', 'big_code'.For custom evaluations,
    this is set to `custom`.
    """

    custom_fields: Dict[str, str]
    """A set of custom fields that the user can define and use for various purposes."""

    description: str
    """The description of the entity."""

    groups: Dict[str, GroupConfigInputParam]
    """Evaluation tasks belonging to the evaluation."""

    name: str
    """The name of the entity.

    Must be unique inside the namespace. If not specified, it will be the same as
    the automatically generated id.
    """

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

    params: EvaluationParamsParam
    """Global parameters for an evaluation."""

    project: str
    """The URN of the project associated with this entity."""

    tasks: Dict[str, TaskConfigInputParam]
    """Evaluation tasks belonging to the evaluation."""
