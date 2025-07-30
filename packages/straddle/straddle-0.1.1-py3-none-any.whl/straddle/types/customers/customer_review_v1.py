# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import date, datetime
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel
from ..customer_address_v1 import CustomerAddressV1
from ..shared.response_metadata import ResponseMetadata
from .identity_verification_breakdown_v1 import IdentityVerificationBreakdownV1

__all__ = [
    "CustomerReviewV1",
    "Data",
    "DataCustomerDetails",
    "DataCustomerDetailsComplianceProfile",
    "DataCustomerDetailsComplianceProfileIndividualComplianceProfile",
    "DataCustomerDetailsComplianceProfileBusinessComplianceProfile",
    "DataCustomerDetailsComplianceProfileBusinessComplianceProfileRepresentative",
    "DataCustomerDetailsConfig",
    "DataCustomerDetailsDevice",
    "DataIdentityDetails",
    "DataIdentityDetailsBreakdown",
    "DataIdentityDetailsKYC",
    "DataIdentityDetailsKYCValidations",
    "DataIdentityDetailsNetworkAlerts",
    "DataIdentityDetailsReputation",
    "DataIdentityDetailsReputationInsights",
    "DataIdentityDetailsWatchList",
    "DataIdentityDetailsWatchListMatch",
]


class DataCustomerDetailsComplianceProfileIndividualComplianceProfile(BaseModel):
    dob: Optional[date] = None
    """Masked date of birth in \\****\\**-**-\\**\\** format."""

    ssn: Optional[str] = None
    """Masked Social Security Number in the format **\\**-**-\\**\\**\\**\\**."""


class DataCustomerDetailsComplianceProfileBusinessComplianceProfileRepresentative(BaseModel):
    name: str

    email: Optional[str] = None

    phone: Optional[str] = None


class DataCustomerDetailsComplianceProfileBusinessComplianceProfile(BaseModel):
    ein: Optional[str] = None
    """Masked Employer Identification Number in the format **-**\\******"""

    legal_business_name: Optional[str] = None
    """The official registered name of the business.

    This name should be correlated with the `ein` value.
    """

    representatives: Optional[List[DataCustomerDetailsComplianceProfileBusinessComplianceProfileRepresentative]] = None
    """A list of people related to the company.

    Only valid where customer type is 'business'.
    """

    website: Optional[str] = None
    """Official business website URL. Optional but recommended for enhanced KYB."""


DataCustomerDetailsComplianceProfile: TypeAlias = Union[
    DataCustomerDetailsComplianceProfileIndividualComplianceProfile,
    DataCustomerDetailsComplianceProfileBusinessComplianceProfile,
    None,
]


class DataCustomerDetailsConfig(BaseModel):
    processing_method: Optional[Literal["inline", "background", "skip"]] = None

    sandbox_outcome: Optional[Literal["standard", "verified", "rejected", "review"]] = None


class DataCustomerDetailsDevice(BaseModel):
    ip_address: str
    """The customer's IP address at the time of profile creation.

    Use `0.0.0.0` to represent an offline customer registration.
    """


class DataCustomerDetails(BaseModel):
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

    compliance_profile: Optional[DataCustomerDetailsComplianceProfile] = None
    """PII required to trigger Patriot Act compliant KYC verification."""

    config: Optional[DataCustomerDetailsConfig] = None

    device: Optional[DataCustomerDetailsDevice] = None

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


class DataIdentityDetailsBreakdown(BaseModel):
    address: Optional[IdentityVerificationBreakdownV1] = None

    business_evaluation: Optional[IdentityVerificationBreakdownV1] = None

    business_identification: Optional[IdentityVerificationBreakdownV1] = None

    business_validation: Optional[IdentityVerificationBreakdownV1] = None

    email: Optional[IdentityVerificationBreakdownV1] = None

    fraud: Optional[IdentityVerificationBreakdownV1] = None

    phone: Optional[IdentityVerificationBreakdownV1] = None

    synthetic: Optional[IdentityVerificationBreakdownV1] = None


class DataIdentityDetailsKYCValidations(BaseModel):
    address: Optional[bool] = None

    city: Optional[bool] = None

    dob: Optional[bool] = None

    email: Optional[bool] = None

    first_name: Optional[bool] = None

    last_name: Optional[bool] = None

    phone: Optional[bool] = None

    ssn: Optional[bool] = None

    state: Optional[bool] = None

    zip: Optional[bool] = None


class DataIdentityDetailsKYC(BaseModel):
    validations: DataIdentityDetailsKYCValidations
    """Boolean values indicating the result of each validation in the KYC process."""

    codes: Optional[List[str]] = None
    """List of specific result codes from the KYC screening process."""

    decision: Optional[Literal["accept", "reject", "review"]] = None


class DataIdentityDetailsNetworkAlerts(BaseModel):
    alerts: Optional[List[str]] = None
    """Any alerts or flags raised during the consortium alert screening."""

    codes: Optional[List[str]] = None
    """List of specific result codes from the consortium alert screening."""

    decision: Optional[Literal["accept", "reject", "review"]] = None


class DataIdentityDetailsReputationInsights(BaseModel):
    accounts_active_count: Optional[int] = None

    accounts_closed_count: Optional[int] = None

    accounts_closed_dates: Optional[List[date]] = None

    accounts_count: Optional[int] = None

    accounts_fraud_count: Optional[int] = None

    accounts_fraud_labeled_dates: Optional[List[date]] = None

    accounts_fraud_loss_total_amount: Optional[float] = None

    ach_fraud_transactions_count: Optional[int] = None

    ach_fraud_transactions_dates: Optional[List[date]] = None

    ach_fraud_transactions_total_amount: Optional[float] = None

    ach_returned_transactions_count: Optional[int] = None

    ach_returned_transactions_dates: Optional[List[date]] = None

    ach_returned_transactions_total_amount: Optional[float] = None

    applications_approved_count: Optional[int] = None

    applications_count: Optional[int] = None

    applications_dates: Optional[List[date]] = None

    applications_declined_count: Optional[int] = None

    applications_fraud_count: Optional[int] = None

    card_disputed_transactions_count: Optional[int] = None

    card_disputed_transactions_dates: Optional[List[date]] = None

    card_disputed_transactions_total_amount: Optional[float] = None

    card_fraud_transactions_count: Optional[int] = None

    card_fraud_transactions_dates: Optional[List[date]] = None

    card_fraud_transactions_total_amount: Optional[float] = None

    card_stopped_transactions_count: Optional[int] = None

    card_stopped_transactions_dates: Optional[List[date]] = None

    user_active_profile_count: Optional[int] = None

    user_address_count: Optional[int] = None

    user_closed_profile_count: Optional[int] = None

    user_dob_count: Optional[int] = None

    user_email_count: Optional[int] = None

    user_institution_count: Optional[int] = None

    user_mobile_count: Optional[int] = None


class DataIdentityDetailsReputation(BaseModel):
    codes: Optional[List[str]] = None
    """Specific codes related to the Straddle reputation screening results."""

    decision: Optional[Literal["accept", "reject", "review"]] = None

    insights: Optional[DataIdentityDetailsReputationInsights] = None

    risk_score: Optional[float] = None


class DataIdentityDetailsWatchListMatch(BaseModel):
    correlation: Literal["low_confidence", "potential_match", "likely_match", "high_confidence"]

    list_name: str
    """The name of the list the match was found."""

    match_fields: List[str]
    """Data fields that matched."""

    urls: List[str]
    """Relevent Urls to review."""


class DataIdentityDetailsWatchList(BaseModel):
    codes: Optional[List[str]] = None
    """Specific codes related to the Straddle watchlist screening results."""

    decision: Optional[Literal["accept", "reject", "review"]] = None

    matched: Optional[List[str]] = None
    """Information about any matches found during screening."""

    matches: Optional[List[DataIdentityDetailsWatchListMatch]] = None
    """Information about any matches found during screening."""


class DataIdentityDetails(BaseModel):
    breakdown: DataIdentityDetailsBreakdown
    """
    Detailed breakdown of the customer verification results, including decisions,
    risk scores, correlation score, and more.
    """

    created_at: datetime
    """Timestamp of when the review was initiated."""

    decision: Literal["accept", "reject", "review"]

    review_id: str
    """Unique identifier for the review."""

    updated_at: datetime
    """Timestamp of the most recent update to the review."""

    kyc: Optional[DataIdentityDetailsKYC] = None

    messages: Optional[Dict[str, str]] = None
    """Dictionary of all messages from the customer verification process."""

    network_alerts: Optional[DataIdentityDetailsNetworkAlerts] = None

    reputation: Optional[DataIdentityDetailsReputation] = None

    watch_list: Optional[DataIdentityDetailsWatchList] = None


class Data(BaseModel):
    customer_details: DataCustomerDetails

    identity_details: Optional[DataIdentityDetails] = None


class CustomerReviewV1(BaseModel):
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
