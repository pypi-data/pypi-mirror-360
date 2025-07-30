# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from datetime import datetime
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["CustomerListParams"]


class CustomerListParams(TypedDict, total=False):
    created_from: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Start date for filtering by `created_at` date."""

    created_to: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """End date for filtering by `created_at` date."""

    email: str
    """Filter customers by `email` address."""

    external_id: str
    """Filter by your system's `external_id`."""

    name: str
    """Filter customers by `name` (partial match)."""

    page_number: int
    """Page number for paginated results. Starts at 1."""

    page_size: int
    """Number of results per page. Maximum: 1000."""

    search_text: str
    """General search term to filter customers."""

    sort_by: Literal["name", "created_at"]

    sort_order: Literal["asc", "desc"]

    status: List[Literal["pending", "review", "verified", "inactive", "rejected"]]
    """Filter customers by their current `status`."""

    types: List[Literal["individual", "business"]]
    """Filter by customer type `individual` or `business`."""

    correlation_id: Annotated[str, PropertyInfo(alias="Correlation-Id")]

    request_id: Annotated[str, PropertyInfo(alias="Request-Id")]

    straddle_account_id: Annotated[str, PropertyInfo(alias="Straddle-Account-Id")]
