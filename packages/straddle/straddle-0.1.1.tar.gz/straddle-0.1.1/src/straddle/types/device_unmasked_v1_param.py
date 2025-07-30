# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["DeviceUnmaskedV1Param"]


class DeviceUnmaskedV1Param(TypedDict, total=False):
    ip_address: Required[str]
    """The customer's IP address at the time of profile creation.

    Use `0.0.0.0` to represent an offline customer registration.
    """
