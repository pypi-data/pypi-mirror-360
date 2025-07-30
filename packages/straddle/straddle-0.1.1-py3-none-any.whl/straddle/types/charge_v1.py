# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import date, datetime
from typing_extensions import Literal

from .._models import BaseModel
from .shared.device_info_v1 import DeviceInfoV1
from .shared.paykey_details_v1 import PaykeyDetailsV1
from .shared.response_metadata import ResponseMetadata
from .shared.status_details_v1 import StatusDetailsV1
from .shared.customer_details_v1 import CustomerDetailsV1

__all__ = ["ChargeV1", "Data", "DataConfig", "DataStatusHistory"]


class DataConfig(BaseModel):
    balance_check: Literal["required", "enabled", "disabled"]
    """Defines whether to check the customer's balance before processing the charge."""

    sandbox_outcome: Optional[
        Literal[
            "standard",
            "paid",
            "on_hold_daily_limit",
            "cancelled_for_fraud_risk",
            "cancelled_for_balance_check",
            "failed_insufficient_funds",
            "reversed_insufficient_funds",
            "failed_customer_dispute",
            "reversed_customer_dispute",
            "failed_closed_bank_account",
            "reversed_closed_bank_account",
        ]
    ] = None
    """Payment will simulate processing if not Standard."""


class DataStatusHistory(BaseModel):
    changed_at: datetime
    """The time the status change occurred."""

    message: str
    """A human-readable description of the status."""

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
    """
    A machine-readable identifier for the specific status, useful for programmatic
    handling.
    """

    source: Literal["watchtower", "bank_decline", "customer_dispute", "user_action", "system"]
    """Identifies the origin of the status change (e.g., `bank_decline`, `watchtower`).

    This helps in tracking the cause of status updates.
    """

    status: Literal["created", "scheduled", "failed", "cancelled", "on_hold", "pending", "paid", "reversed"]
    """The current status of the `charge` or `payout`."""

    code: Optional[str] = None
    """The status code if applicable."""


class Data(BaseModel):
    id: str
    """Unique identifier for the charge."""

    amount: int
    """The amount of the charge in cents."""

    config: DataConfig
    """Configuration options for the charge."""

    consent_type: Literal["internet", "signed"]
    """The channel or mechanism through which the payment was authorized.

    Use `internet` for payments made online or through a mobile app and `signed` for
    signed agreements where there is a consent form or contract. Use `signed` for
    PDF signatures.
    """

    created_at: Optional[datetime] = None
    """Timestamp of when the charge was created."""

    currency: str
    """The currency of the charge. Only USD is supported."""

    description: str
    """An arbitrary description for the charge."""

    device: DeviceInfoV1
    """Information about the device used when the customer authorized the payment."""

    external_id: str
    """Unique identifier for the charge in your database.

    This value must be unique across all charges.
    """

    funding_ids: List[str]
    """Funding Ids"""

    paykey: str
    """Value of the `paykey` used for the charge."""

    payment_date: date
    """The desired date on which the payment should be occur.

    For charges, this means the date you want the customer to be debited on.
    """

    status: Literal["created", "scheduled", "failed", "cancelled", "on_hold", "pending", "paid", "reversed"]
    """The current status of the charge."""

    status_details: StatusDetailsV1
    """Additional details about the current status of the charge."""

    status_history: List[DataStatusHistory]
    """Status history."""

    updated_at: Optional[datetime] = None
    """Timestamp of when the charge was last updated."""

    customer_details: Optional[CustomerDetailsV1] = None
    """Information about the customer associated with the charge."""

    effective_at: Optional[datetime] = None
    """
    Timestamp of when the charge was effective in the customer's bank account,
    otherwise known as the date on which the customer is debited.
    """

    metadata: Optional[Dict[str, str]] = None
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the charge in a structured
    format.
    """

    paykey_details: Optional[PaykeyDetailsV1] = None
    """Information about the paykey used for the charge."""

    payment_rail: Optional[Literal["ach"]] = None
    """The payment rail that the charge will be processed through."""

    processed_at: Optional[datetime] = None
    """
    Timestamp of when the charge was processed by Straddle and originated to the
    payment rail.
    """


class ChargeV1(BaseModel):
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
