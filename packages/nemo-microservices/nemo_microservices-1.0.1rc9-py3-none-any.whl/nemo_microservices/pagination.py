# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Generic, TypeVar, Optional, cast
from typing_extensions import override

from ._models import BaseModel
from ._base_client import BasePage, PageInfo, BaseSyncPage, BaseAsyncPage

__all__ = ["DefaultPaginationPagination", "SyncDefaultPagination", "AsyncDefaultPagination"]

_T = TypeVar("_T")


class DefaultPaginationPagination(BaseModel):
    current_page_size: Optional[int] = None
    """The size for the current page."""

    page: Optional[int] = None
    """The current page number."""

    page_size: Optional[int] = None
    """The page size used for the query."""

    total_pages: Optional[int] = None
    """The total number of pages."""

    total_results: Optional[int] = None
    """The total number of results."""


class SyncDefaultPagination(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    object: Optional[str] = None
    data: List[_T]
    sort: Optional[str] = None
    pagination: Optional[DefaultPaginationPagination] = None

    @override
    def _get_page_items(self) -> List[_T]:
        data = self.data
        if not data:
            return []
        return data

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        last_page = cast("int | None", self._options.params.get("page")) or 1

        return PageInfo(params={"page": last_page + 1})


class AsyncDefaultPagination(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    object: Optional[str] = None
    data: List[_T]
    sort: Optional[str] = None
    pagination: Optional[DefaultPaginationPagination] = None

    @override
    def _get_page_items(self) -> List[_T]:
        data = self.data
        if not data:
            return []
        return data

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        last_page = cast("int | None", self._options.params.get("page")) or 1

        return PageInfo(params={"page": last_page + 1})
