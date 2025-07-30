# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import date
from typing_extensions import Literal

from .._models import BaseModel
from .shared.response_metadata import ResponseMetadata

__all__ = ["FundingEventSummaryItemV1", "Data"]


class Data(BaseModel):
    id: str
    """Unique identifier for the funding event."""

    amount: int
    """The amount of the funding event in cents."""

    direction: Literal["deposit", "withdrawal"]
    """
    Describes the direction of the funding event from the perspective of the
    `linked_bank_account`.
    """

    event_type: Literal["charge_deposit", "charge_reversal", "payout_return", "payout_withdrawal"]
    """
    The funding event types describes the direction and reason for the funding
    event.
    """

    payment_count: int
    """The number of payments associated with the funding event."""

    trace_numbers: List[str]
    """Trace number."""

    transfer_date: date
    """The date on which the funding event occurred.

    For `deposits` and `returns`, this is the date the funds were credited to your
    bank account. For `withdrawals` and `reversals`, this is the date the funds were
    debited from your bank account.
    """

    trace_number: Optional[str] = None
    """The trace number of the funding event."""


class FundingEventSummaryItemV1(BaseModel):
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
