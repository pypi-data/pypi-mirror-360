# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from ..._models import BaseModel

__all__ = ["ResponseMetadata"]


class ResponseMetadata(BaseModel):
    api_request_id: str
    """Unique identifier for this API request, useful for troubleshooting."""

    api_request_timestamp: datetime
    """Timestamp for this API request, useful for troubleshooting."""
