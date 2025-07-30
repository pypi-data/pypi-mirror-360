# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["PaginationData"]


class PaginationData(BaseModel):
    current_page_size: int
    """The size for the current page."""

    page: int
    """The current page number."""

    page_size: int
    """The page size used for the query."""

    total_pages: int
    """The total number of pages."""

    total_results: int
    """The total number of results."""
