from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `nemo_microservices.resources` module.

    This is used so that we can lazily import `nemo_microservices.resources` only when
    needed *and* so that users can just import `nemo_microservices` and reference `nemo_microservices.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("nemo_microservices.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
