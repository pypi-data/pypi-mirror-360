# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel
from .shared.response_metadata import ResponseMetadata

__all__ = ["PaykeyUnmaskedV1", "Data", "DataConfig", "DataBalance", "DataBankData", "DataStatusDetails"]


class DataConfig(BaseModel):
    sandbox_outcome: Optional[Literal["standard", "active", "rejected"]] = None


class DataBalance(BaseModel):
    status: Literal["pending", "completed", "failed"]

    account_balance: Optional[int] = None
    """Account Balance when last retrieved"""

    updated_at: Optional[datetime] = None
    """Last time account balance was updated."""


class DataBankData(BaseModel):
    account_number: str
    """The bank account number"""

    account_type: Literal["checking", "savings"]

    routing_number: str
    """The routing number of the bank account."""


class DataStatusDetails(BaseModel):
    changed_at: datetime
    """The time the status change occurred."""

    message: str
    """A human-readable description of the current status."""

    reason: Literal[
        "insufficient_funds",
        "closed_bank_account",
        "invalid_bank_account",
        "invalid_routing",
        "disputed",
        "payment_stopped",
        "owner_deceased",
        "frozen_bank_account",
        "risk_review",
        "fraudulent",
        "duplicate_entry",
        "invalid_paykey",
        "payment_blocked",
        "amount_too_large",
        "too_many_attempts",
        "internal_system_error",
        "user_request",
        "ok",
        "other_network_return",
        "payout_refused",
    ]

    source: Literal["watchtower", "bank_decline", "customer_dispute", "user_action", "system"]

    code: Optional[str] = None
    """The status code if applicable."""


class Data(BaseModel):
    id: str
    """Unique identifier for the paykey."""

    config: DataConfig

    created_at: datetime
    """Timestamp of when the paykey was created."""

    label: str
    """Human-readable label used to represent this paykey in a UI."""

    paykey: str
    """The tokenized paykey value.

    This value is used to create payments and should be stored securely.
    """

    source: Literal["bank_account", "straddle", "mx", "plaid", "tan", "quiltt"]

    status: Literal["pending", "active", "inactive", "rejected", "review"]

    updated_at: datetime
    """Timestamp of the most recent update to the paykey."""

    balance: Optional[DataBalance] = None

    bank_data: Optional[DataBankData] = None

    customer_id: Optional[str] = None
    """Unique identifier of the related customer object."""

    expires_at: Optional[datetime] = None
    """Expiration date and time of the paykey, if applicable."""

    institution_name: Optional[str] = None
    """Name of the financial institution."""

    metadata: Optional[Dict[str, str]] = None
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the paykey in a structured
    format.
    """

    status_details: Optional[DataStatusDetails] = None


class PaykeyUnmaskedV1(BaseModel):
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
