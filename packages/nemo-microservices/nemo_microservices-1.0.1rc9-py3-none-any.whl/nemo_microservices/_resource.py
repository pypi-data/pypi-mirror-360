# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import anyio

if TYPE_CHECKING:
    from ._client import NeMoMicroservices, AsyncNeMoMicroservices


class SyncAPIResource:
    _client: NeMoMicroservices

    def __init__(self, client: NeMoMicroservices) -> None:
        self._client = client
        self._get = client.get
        self._post = client.post
        self._patch = client.patch
        self._put = client.put
        self._delete = client.delete
        self._get_api_list = client.get_api_list

    def _sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    def create_from_dict(self, data: dict[str, object]) -> object:
        return self.create(**data)  # type: ignore


class AsyncAPIResource:
    _client: AsyncNeMoMicroservices

    def __init__(self, client: AsyncNeMoMicroservices) -> None:
        self._client = client
        self._get = client.get
        self._post = client.post
        self._patch = client.patch
        self._put = client.put
        self._delete = client.delete
        self._get_api_list = client.get_api_list

    async def _sleep(self, seconds: float) -> None:
        await anyio.sleep(seconds)

    def create_from_dict(self, data: dict[str, object]) -> object:
        return self.create(**data)  # type: ignore
