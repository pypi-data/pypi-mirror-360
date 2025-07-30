# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel
from .shared.response_metadata import ResponseMetadata

__all__ = ["ReportCreateTotalCustomersByStatusResponse", "Data"]


class Data(BaseModel):
    inactive: int

    pending: int

    rejected: int

    review: int

    verified: int


class ReportCreateTotalCustomersByStatusResponse(BaseModel):
    data: Data

    meta: ResponseMetadata
    """Metadata about the API request, including an identifier and timestamp."""

    response_type: Literal["object", "array", "error", "none"]
    """Indicates the structure of the returned content.

    - "object" means the `data` field contains a single JSON object.
    - "array" means the `data` field contains an array of objects.
    - "error" means the `data` field contains an error object with details of the
      issue.
    - "none" means no data is returned.
    """
