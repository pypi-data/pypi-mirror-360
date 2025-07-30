# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from datetime import date, datetime
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["PaymentListParams"]


class PaymentListParams(TypedDict, total=False):
    customer_id: str
    """Search using the `customer_id` of a `charge` or `payout`."""

    default_page_size: int

    default_sort: Literal["created_at", "payment_date", "effective_at", "id", "amount"]
    """The field to sort the results by."""

    default_sort_order: Literal["asc", "desc"]

    external_id: str
    """Search using the `external_id` of a `charge` or `payout`."""

    funding_id: str
    """Search using the `funding_id` of a `charge` or `payout`."""

    max_amount: int
    """Search using a maximum `amount` of a `charge` or `payout`."""

    max_created_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Search using the latest `created_at` date of a `charge` or `payout`."""

    max_effective_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Search using the latest `effective_date` of a `charge` or `payout`."""

    max_payment_date: Annotated[Union[str, date], PropertyInfo(format="iso8601")]
    """Search using the latest `payment_date` of a `charge` or `payout`."""

    min_amount: int
    """Search using the minimum `amount of a `charge`or`payout`."""

    min_created_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Search using the earliest `created_at` date of a `charge` or `payout`."""

    min_effective_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Search using the earliest `effective_date` of a `charge` or `payout`."""

    min_payment_date: Annotated[Union[str, date], PropertyInfo(format="iso8601")]
    """Search using the earliest ` `of a `charge` or `payout`."""

    page_number: int
    """Results page number. Starts at page 1."""

    page_size: int
    """Results page size. Max value: 1000"""

    paykey: str
    """Search using the `paykey` of a `charge` or `payout`."""

    paykey_id: str
    """Search using the `paykey_id` of a `charge` or `payout`."""

    payment_id: str
    """Search using the `id` of a `charge` or `payout`."""

    payment_status: List[
        Literal["created", "scheduled", "failed", "cancelled", "on_hold", "pending", "paid", "reversed"]
    ]
    """Search by the status of a `charge` or `payout`."""

    payment_type: List[Literal["charge", "payout"]]
    """Search by the type of a `charge` or `payout`."""

    search_text: str
    """Search using a text string associated with a `charge` or `payout`."""

    sort_by: Literal["created_at", "payment_date", "effective_at", "id", "amount"]
    """The field to sort the results by."""

    sort_order: Literal["asc", "desc"]

    status_reason: List[
        Literal[
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
    ]
    """Reason for latest payment status change."""

    status_source: List[Literal["watchtower", "bank_decline", "customer_dispute", "user_action", "system"]]
    """Source of latest payment status change."""

    correlation_id: Annotated[str, PropertyInfo(alias="Correlation-Id")]

    request_id: Annotated[str, PropertyInfo(alias="Request-Id")]

    straddle_account_id: Annotated[str, PropertyInfo(alias="Straddle-Account-Id")]
