# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import date, datetime
from typing_extensions import Literal

from .._models import BaseModel
from .shared.paykey_details_v1 import PaykeyDetailsV1
from .shared.status_details_v1 import StatusDetailsV1
from .shared.customer_details_v1 import CustomerDetailsV1

__all__ = ["PaymentSummaryPagedV1", "Data", "Meta"]


class Data(BaseModel):
    id: str
    """Unique identifier for the `charge` or `payout`."""

    amount: int
    """The amount of the `charge` or `payout` in cents."""

    created_at: datetime
    """The time the `charge` or `payout` was created."""

    currency: str
    """The currency of the `charge` or `payout`. Only USD is supported."""

    description: str
    """An arbitrary description for the `charge` or `payout`."""

    external_id: str
    """Unique identifier for the `charge` or `payout` in your database.

    This value must be unique across all charges or payouts.
    """

    funding_ids: List[str]
    """Funding ids."""

    paykey: str
    """Value of the `paykey` used for the `charge` or `payout`."""

    payment_date: date
    """The desired date on which the payment should be occur.

    For charges, this means the date you want the customer to be debited on. For
    payouts, this means the date you want the funds to be sent from your bank
    account.
    """

    payment_type: Literal["charge", "payout"]
    """The type of payment. Valid values are `charge` or `payout`."""

    status: Literal["created", "scheduled", "failed", "cancelled", "on_hold", "pending", "paid", "reversed"]
    """The current status of the `charge` or `payout`."""

    status_details: StatusDetailsV1
    """Details about the current status of the `charge` or `payout`."""

    updated_at: datetime
    """The time the `charge` or `payout` was last updated."""

    customer_details: Optional[CustomerDetailsV1] = None
    """Information about the customer associated with the charge or payout."""

    effective_at: Optional[datetime] = None
    """The actual date on which the payment occurred.

    For charges, this is the date the customer was debited. For payouts, this is the
    date the funds were sent from your bank account.
    """

    funding_id: Optional[str] = None
    """
    Unique identifier for the funding event associated with the `charge` or
    `payout`.
    """

    paykey_details: Optional[PaykeyDetailsV1] = None
    """Information about the paykey used for the `charge` or `payout`."""


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


class PaymentSummaryPagedV1(BaseModel):
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
