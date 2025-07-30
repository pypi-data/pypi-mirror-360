# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["RepresentativeListParams"]


class RepresentativeListParams(TypedDict, total=False):
    account_id: str
    """The unique identifier of the account to list representatives for."""

    level: Literal["account", "platform"]

    organization_id: str

    page_number: int
    """Results page number. Starts at page 1."""

    page_size: int
    """Page size. Max value: 1000"""

    platform_id: str

    sort_by: str
    """Sort By."""

    sort_order: Literal["asc", "desc"]
    """Sort Order."""

    correlation_id: Annotated[str, PropertyInfo(alias="correlation-id")]

    request_id: Annotated[str, PropertyInfo(alias="request-id")]
