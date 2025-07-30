# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["CustomerAddressV1Param"]


class CustomerAddressV1Param(TypedDict, total=False):
    address1: Required[str]
    """Primary address line (e.g., street, PO Box)."""

    city: Required[str]
    """City, district, suburb, town, or village."""

    state: Required[str]
    """Two-letter state code."""

    zip: Required[str]
    """Zip or postal code."""

    address2: Optional[str]
    """Secondary address line (e.g., apartment, suite, unit, or building)."""
