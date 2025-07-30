# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["CustomerSummaryPagedV1", "Data", "Meta"]


class Data(BaseModel):
    id: str
    """Unique identifier for the customer."""

    created_at: datetime
    """Timestamp of when the customer record was created."""

    email: str
    """The customer's email address."""

    name: str
    """Full name of the individual or business name."""

    phone: str
    """The customer's phone number in E.164 format."""

    status: Literal["pending", "review", "verified", "inactive", "rejected"]

    type: Literal["individual", "business"]

    updated_at: datetime
    """Timestamp of the most recent update to the customer record."""

    external_id: Optional[str] = None
    """
    Unique identifier for the customer in your database, used for cross-referencing
    between Straddle and your systems.
    """


class Meta(BaseModel):
    api_request_id: str
    """Unique identifier for this API request, useful for troubleshooting."""

    api_request_timestamp: datetime
    """Timestamp for this API request, useful for troubleshooting."""

    max_page_size: int
    """Maximum allowed page size for this endpoint."""

    page_number: int
    """Page number for paginated results."""

    page_size: int
    """Number of items per page in this response."""

    sort_by: str
    """The field that the results were sorted by."""

    sort_order: Literal["asc", "desc"]

    total_items: int

    total_pages: int
    """The number of pages available."""


class CustomerSummaryPagedV1(BaseModel):
    data: List[Data]

    meta: Meta

    response_type: Literal["object", "array", "error", "none"]
    """Indicates the structure of the returned content.

    - "object" means the `data` field contains a single JSON object.
    - "array" means the `data` field contains an array of objects.
    - "error" means the `data` field contains an error object with details of the
      issue.
    - "none" means no data is returned.
    """
