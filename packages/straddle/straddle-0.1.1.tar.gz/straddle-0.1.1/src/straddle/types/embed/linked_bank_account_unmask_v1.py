# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel
from ..shared.response_metadata import ResponseMetadata

__all__ = ["LinkedBankAccountUnmaskV1", "Data", "DataBankAccount", "DataStatusDetail"]


class DataBankAccount(BaseModel):
    account_holder: str

    account_number: str

    institution_name: str

    routing_number: str


class DataStatusDetail(BaseModel):
    code: str
    """
    A machine-readable code for the specific status, useful for programmatic
    handling.
    """

    message: str
    """A human-readable message describing the current status."""

    reason: Literal["unverified", "in_review", "pending", "stuck", "verified", "failed_verification", "disabled", "new"]
    """
    A machine-readable identifier for the specific status, useful for programmatic
    handling.
    """

    source: Literal["watchtower"]
    """Identifies the origin of the status change (e.g., `watchtower`).

    This helps in tracking the cause of status updates.
    """


class Data(BaseModel):
    id: str
    """Unique identifier for the linked bank account."""

    account_id: str
    """Unique identifier for the Straddle account related to this bank account."""

    bank_account: DataBankAccount
    """The bank account details associated with the linked bank account."""

    created_at: datetime
    """Timestamp of when the linked bank account was created."""

    status: Literal["created", "onboarding", "active", "rejected", "inactive"]
    """The current status of the linked bank account."""

    status_detail: DataStatusDetail
    """Additional details about the current status of the linked bank account."""

    updated_at: datetime
    """Timestamp of when the linked bank account was last updated."""

    metadata: Optional[Dict[str, Optional[str]]] = None


class LinkedBankAccountUnmaskV1(BaseModel):
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
