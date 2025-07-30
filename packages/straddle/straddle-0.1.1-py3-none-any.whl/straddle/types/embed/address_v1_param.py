# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["AddressV1Param"]


class AddressV1Param(TypedDict, total=False):
    address1: Required[str]
    """Primary address line (e.g., street, PO Box)."""

    city: Required[Optional[str]]
    """City, district, suburb, town, or village."""

    state: Required[Optional[str]]
    """Two-letter state code."""

    zip: Required[str]
    """Zip or postal code."""

    address2: Optional[str]
    """Secondary address line (e.g., apartment, suite, unit, or building)."""

    country: Optional[str]
    """The country of the address, in ISO 3166-1 alpha-2 format."""

    line1: Optional[str]
    """Primary address line (e.g., street, PO Box)."""

    line2: Optional[str]
    """Secondary address line (e.g., apartment, suite, unit, or building)."""

    postal_code: Optional[str]
    """Postal or ZIP code."""
