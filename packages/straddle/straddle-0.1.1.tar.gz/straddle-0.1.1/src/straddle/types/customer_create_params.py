# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from datetime import date
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo
from .device_unmasked_v1_param import DeviceUnmaskedV1Param
from .customer_address_v1_param import CustomerAddressV1Param

__all__ = [
    "CustomerCreateParams",
    "ComplianceProfile",
    "ComplianceProfileIndividualComplianceProfile",
    "ComplianceProfileBusinessComplianceProfile",
    "ComplianceProfileBusinessComplianceProfileRepresentative",
    "Config",
]


class CustomerCreateParams(TypedDict, total=False):
    device: Required[DeviceUnmaskedV1Param]

    email: Required[str]
    """The customer's email address."""

    name: Required[str]
    """Full name of the individual or business name."""

    phone: Required[str]
    """The customer's phone number in E.164 format. Mobile number is preferred."""

    type: Required[Literal["individual", "business"]]

    address: Optional[CustomerAddressV1Param]
    """An object containing the customer's address.

    **This is optional.** If used, all required fields must be present.
    """

    compliance_profile: Optional[ComplianceProfile]
    """An object containing the customer's compliance profile.

    **This is optional.** If all required fields must be present for the appropriate
    customer type.
    """

    config: Config

    external_id: Optional[str]
    """
    Unique identifier for the customer in your database, used for cross-referencing
    between Straddle and your systems.
    """

    metadata: Optional[Dict[str, str]]
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the customer in a structured
    format.
    """

    correlation_id: Annotated[str, PropertyInfo(alias="Correlation-Id")]

    request_id: Annotated[str, PropertyInfo(alias="Request-Id")]

    straddle_account_id: Annotated[str, PropertyInfo(alias="Straddle-Account-Id")]


class ComplianceProfileIndividualComplianceProfile(TypedDict, total=False):
    dob: Required[Annotated[Union[str, date, None], PropertyInfo(format="iso8601")]]
    """Date of birth (YYYY-MM-DD).

    Required for Patriot Act-compliant KYC verification.
    """

    ssn: Required[Optional[str]]
    """Social Security Number (format XXX-XX-XXXX).

    Required for Patriot Act-compliant KYC verification.
    """


class ComplianceProfileBusinessComplianceProfileRepresentative(TypedDict, total=False):
    name: Required[str]

    email: Optional[str]

    phone: Optional[str]


class ComplianceProfileBusinessComplianceProfile(TypedDict, total=False):
    ein: Required[Optional[str]]
    """Employer Identification Number (format XX-XXXXXXX).

    Required for Patriot Act-compliant KYB verification.
    """

    legal_business_name: Required[Optional[str]]
    """Official registered business name as listed with the IRS.

    This value will be matched against the 'legal_business name'.
    """

    representatives: Optional[Iterable[ComplianceProfileBusinessComplianceProfileRepresentative]]
    """A list of people related to the company.

    Only valid where customer type is 'business'.
    """

    website: Optional[str]
    """Official business website URL. Optional but recommended for enhanced KYB."""


ComplianceProfile: TypeAlias = Union[
    ComplianceProfileIndividualComplianceProfile, ComplianceProfileBusinessComplianceProfile
]


class Config(TypedDict, total=False):
    processing_method: Literal["inline", "background", "skip"]

    sandbox_outcome: Literal["standard", "verified", "rejected", "review"]
