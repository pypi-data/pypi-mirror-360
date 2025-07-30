# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["DatasetInputCu"]


class DatasetInputCu(BaseModel):
    files_url: Optional[str] = None
    """The location where the artifact files are stored.

    This can be a URL pointing to NDS, Hugging Face, S3, or any other accessible
    resource location.
    """

    name: Optional[str] = None
    """The name of the entity.

    Must be unique inside the namespace. If not specified, it will be the same as
    the automatically generated id.
    """

    namespace: Optional[str] = None
    """The ID of the namespace of the entity.

    This can be missing for namespace entities or in deployments that don't use
    namespaces.
    """
