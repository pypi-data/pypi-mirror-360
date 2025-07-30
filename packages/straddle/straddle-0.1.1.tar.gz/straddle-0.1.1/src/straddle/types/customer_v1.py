# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import date, datetime
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel
from .customer_address_v1 import CustomerAddressV1
from .shared.response_metadata import ResponseMetadata

__all__ = [
    "CustomerV1",
    "Data",
    "DataComplianceProfile",
    "DataComplianceProfileIndividualComplianceProfile",
    "DataComplianceProfileBusinessComplianceProfile",
    "DataComplianceProfileBusinessComplianceProfileRepresentative",
    "DataConfig",
    "DataDevice",
]


class DataComplianceProfileIndividualComplianceProfile(BaseModel):
    dob: Optional[date] = None
    """Masked date of birth in \\****\\**-**-\\**\\** format."""

    ssn: Optional[str] = None
    """Masked Social Security Number in the format **\\**-**-\\**\\**\\**\\**."""


class DataComplianceProfileBusinessComplianceProfileRepresentative(BaseModel):
    name: str

    email: Optional[str] = None

    phone: Optional[str] = None


class DataComplianceProfileBusinessComplianceProfile(BaseModel):
    ein: Optional[str] = None
    """Masked Employer Identification Number in the format **-**\\******"""

    legal_business_name: Optional[str] = None
    """The official registered name of the business.

    This name should be correlated with the `ein` value.
    """

    representatives: Optional[List[DataComplianceProfileBusinessComplianceProfileRepresentative]] = None
    """A list of people related to the company.

    Only valid where customer type is 'business'.
    """

    website: Optional[str] = None
    """Official business website URL. Optional but recommended for enhanced KYB."""


DataComplianceProfile: TypeAlias = Union[
    DataComplianceProfileIndividualComplianceProfile, DataComplianceProfileBusinessComplianceProfile, None
]


class DataConfig(BaseModel):
    processing_method: Optional[Literal["inline", "background", "skip"]] = None

    sandbox_outcome: Optional[Literal["standard", "verified", "rejected", "review"]] = None


class DataDevice(BaseModel):
    ip_address: str
    """The customer's IP address at the time of profile creation.

    Use `0.0.0.0` to represent an offline customer registration.
    """


class Data(BaseModel):
    id: str
    """Unique identifier for the customer."""

    created_at: datetime
    """Timestamp of when the customer record was created."""

    email: str
    """The customer's email address."""

    name: str
    """Full name of the individual or business name."""

    phone: str
    """The customer's phone number in E.164 format."""

    status: Literal["pending", "review", "verified", "inactive", "rejected"]

    type: Literal["individual", "business"]

    updated_at: datetime
    """Timestamp of the most recent update to the customer record."""

    address: Optional[CustomerAddressV1] = None
    """An object containing the customer's address.

    This is optional, but if provided, all required fields must be present.
    """

    compliance_profile: Optional[DataComplianceProfile] = None
    """PII required to trigger Patriot Act compliant KYC verification."""

    config: Optional[DataConfig] = None

    device: Optional[DataDevice] = None

    external_id: Optional[str] = None
    """
    Unique identifier for the customer in your database, used for cross-referencing
    between Straddle and your systems.
    """

    metadata: Optional[Dict[str, str]] = None
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the customer in a structured
    format.
    """


class CustomerV1(BaseModel):
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
