# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import date, datetime
from typing_extensions import Literal

from .._models import BaseModel
from .shared.paykey_details_v1 import PaykeyDetailsV1
from .shared.response_metadata import ResponseMetadata
from .shared.status_details_v1 import StatusDetailsV1
from .shared.customer_details_v1 import CustomerDetailsV1

__all__ = ["PayoutUnmaskResponse", "Data", "DataConfig", "DataDevice", "DataStatusHistory"]


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


class DataDevice(BaseModel):
    ip_address: str
    """Ip address."""


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
    """Id."""

    amount: int
    """Amount."""

    config: DataConfig

    currency: str
    """Currency."""

    description: str
    """Description."""

    device: DataDevice

    external_id: str
    """External id."""

    funding_ids: List[str]
    """Funding Ids"""

    paykey: str
    """Paykey."""

    payment_date: date
    """Payment date."""

    status: Literal["created", "scheduled", "failed", "cancelled", "on_hold", "pending", "paid", "reversed"]
    """The current status of the `charge` or `payout`."""

    status_details: StatusDetailsV1

    status_history: List[DataStatusHistory]
    """Status history."""

    created_at: Optional[datetime] = None
    """Created at."""

    customer_details: Optional[CustomerDetailsV1] = None
    """Information about the customer associated with the charge or payout."""

    effective_at: Optional[datetime] = None
    """Effective at."""

    metadata: Optional[Dict[str, str]] = None
    """Metadata."""

    paykey_details: Optional[PaykeyDetailsV1] = None

    payment_rail: Optional[Literal["ach"]] = None
    """The payment rail used for the charge or payout."""

    processed_at: Optional[datetime] = None
    """Processed at."""

    updated_at: Optional[datetime] = None
    """Updated at."""


class PayoutUnmaskResponse(BaseModel):
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
