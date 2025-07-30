# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["DatasetInputCuParam"]


class DatasetInputCuParam(TypedDict, total=False):
    files_url: str
    """The location where the artifact files are stored.

    This can be a URL pointing to NDS, Hugging Face, S3, or any other accessible
    resource location.
    """

    name: str
    """The name of the entity.

    Must be unique inside the namespace. If not specified, it will be the same as
    the automatically generated id.
    """

    namespace: str
    """The ID of the namespace of the entity.

    This can be missing for namespace entities or in deployments that don't use
    namespaces.
    """
