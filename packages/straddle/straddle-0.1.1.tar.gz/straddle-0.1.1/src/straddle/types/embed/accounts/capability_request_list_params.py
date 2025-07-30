# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["CapabilityRequestListParams"]


class CapabilityRequestListParams(TypedDict, total=False):
    category: Literal["payment_type", "customer_type", "consent_type"]
    """Filter capability requests by category."""

    page_number: int
    """Results page number. Starts at page 1."""

    page_size: int
    """Page size.Max value: 1000"""

    sort_by: str
    """Sort By."""

    sort_order: Literal["asc", "desc"]
    """Sort Order."""

    status: Literal["active", "inactive", "in_review", "rejected"]
    """Filter capability requests by their current status."""

    type: Literal["charges", "payouts", "individuals", "businesses", "signed_agreement", "internet"]
    """Filter capability requests by the specific type of capability."""

    correlation_id: Annotated[str, PropertyInfo(alias="correlation-id")]

    request_id: Annotated[str, PropertyInfo(alias="request-id")]
