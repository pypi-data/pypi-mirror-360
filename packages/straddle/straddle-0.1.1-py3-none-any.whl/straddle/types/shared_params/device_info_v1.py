# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["DeviceInfoV1"]


class DeviceInfoV1(TypedDict, total=False):
    ip_address: Required[str]
    """
    The IP address of the device used when the customer authorized the charge or
    payout. Use `0.0.0.0` to represent an offline consent interaction.
    """
