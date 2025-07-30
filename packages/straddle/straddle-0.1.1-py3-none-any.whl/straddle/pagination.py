# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Generic, TypeVar, Optional, cast
from typing_extensions import override

from ._models import BaseModel
from ._base_client import BasePage, PageInfo, BaseSyncPage, BaseAsyncPage

__all__ = ["PageNumberSchemaMeta", "SyncPageNumberSchema", "AsyncPageNumberSchema"]

_T = TypeVar("_T")


class PageNumberSchemaMeta(BaseModel):
    max_page_size: Optional[int] = None

    page_number: Optional[int] = None

    page_size: Optional[int] = None

    total_items: Optional[int] = None


class SyncPageNumberSchema(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    data: List[_T]
    meta: Optional[PageNumberSchemaMeta] = None

    @override
    def _get_page_items(self) -> List[_T]:
        data = self.data
        if not data:
            return []
        return data

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        last_page = cast("int | None", self._options.params.get("page_number")) or 1

        return PageInfo(params={"page_number": last_page + 1})


class AsyncPageNumberSchema(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    data: List[_T]
    meta: Optional[PageNumberSchemaMeta] = None

    @override
    def _get_page_items(self) -> List[_T]:
        data = self.data
        if not data:
            return []
        return data

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        last_page = cast("int | None", self._options.params.get("page_number")) or 1

        return PageInfo(params={"page_number": last_page + 1})
