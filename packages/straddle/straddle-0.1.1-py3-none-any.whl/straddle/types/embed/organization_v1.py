# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel
from ..shared.response_metadata import ResponseMetadata

__all__ = ["OrganizationV1", "Data"]


class Data(BaseModel):
    id: str
    """Straddle's unique identifier for the organization."""

    created_at: datetime
    """Timestamp of when the organization was created."""

    name: str
    """The name of the organization."""

    updated_at: datetime
    """Timestamp of the most recent update to the organization."""

    external_id: Optional[str] = None
    """
    Unique identifier for the organization in your database, used for
    cross-referencing between Straddle and your systems.
    """

    metadata: Optional[Dict[str, Optional[str]]] = None
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the organization in a structured
    format.
    """


class OrganizationV1(BaseModel):
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
