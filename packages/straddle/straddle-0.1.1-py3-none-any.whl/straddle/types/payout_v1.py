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

__all__ = ["PayoutV1", "Data", "DataConfig", "DataStatusHistory"]


class DataConfig(BaseModel):
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
    """Unique identifier for the payout."""

    amount: int
    """The amount of the payout in cents."""

    config: DataConfig
    """Configuration for the payout."""

    currency: str
    """The currency of the payout. Only USD is supported."""

    description: str
    """An arbitrary description for the payout."""

    device: DeviceInfoV1
    """Information about the device used when the customer authorized the payout."""

    external_id: str
    """Unique identifier for the payout in your database.

    This value must be unique across all payouts.
    """

    funding_ids: List[str]
    """Funding Ids"""

    paykey: str
    """Value of the `paykey` used for the payout."""

    payment_date: date
    """The desired date on which the payment should be occur.

    For payouts, this means the date you want the funds to be sent from your bank
    account.
    """

    status: Literal["created", "scheduled", "failed", "cancelled", "on_hold", "pending", "paid", "reversed"]
    """The current status of the payout."""

    status_details: StatusDetailsV1
    """Details about the current status of the payout."""

    status_history: List[DataStatusHistory]
    """History of the status changes for the payout."""

    created_at: Optional[datetime] = None
    """The time the payout was created."""

    customer_details: Optional[CustomerDetailsV1] = None
    """Information about the customer associated with the payout."""

    effective_at: Optional[datetime] = None
    """The actual date on which the payment occurred.

    For payouts, this is the date the funds were sent from your bank account.
    """

    metadata: Optional[Dict[str, str]] = None
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the payout in a structured
    format.
    """

    paykey_details: Optional[PaykeyDetailsV1] = None
    """Information about the paykey used for the payout."""

    payment_rail: Optional[Literal["ach"]] = None
    """The payment rail used for the payout."""

    processed_at: Optional[datetime] = None
    """
    The time the payout was processed by Straddle and originated to the payment
    rail.
    """

    updated_at: Optional[datetime] = None
    """The time the payout was last updated."""


class PayoutV1(BaseModel):
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
