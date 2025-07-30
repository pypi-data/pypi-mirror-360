# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["CustomizationConfigSortField"]

CustomizationConfigSortField: TypeAlias = Literal[
    "created_at",
    "-created_at",
    "updated_at",
    "-updated_at",
    "name",
    "-name",
    "enabled",
    "-enabled",
    "num_parameters",
    "-num_parameters",
]
