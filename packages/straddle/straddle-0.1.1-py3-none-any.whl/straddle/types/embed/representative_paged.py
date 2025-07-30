# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import date, datetime
from typing_extensions import Literal

from ..._models import BaseModel
from ..shared.paged_response_metadata import PagedResponseMetadata

__all__ = ["RepresentativePaged", "Data", "DataRelationship", "DataStatusDetail"]


class DataRelationship(BaseModel):
    control: bool
    """
    Whether the representative has significant responsibility to control, manage, or
    direct the organization. One representative must be identified under the control
    prong for each legal entity.
    """

    owner: bool
    """
    Whether the representative owns any percentage of of the equity interests of the
    legal entity.
    """

    primary: bool
    """Whether the person is authorized as the primary representative of the account.

    This is the person chosen by the business to provide information about
    themselves, general information about the account, and who consented to the
    services agreement.

    There can be only one primary representative for an account at a time.
    """

    percent_ownership: Optional[float] = None
    """The percentage of ownership the representative has.

    Required if 'Owner' is true.
    """

    title: Optional[str] = None
    """The job title of the representative."""


class DataStatusDetail(BaseModel):
    code: str
    """
    A machine-readable code for the specific status, useful for programmatic
    handling.
    """

    message: str
    """A human-readable message describing the current status."""

    reason: Literal["unverified", "in_review", "pending", "stuck", "verified", "failed_verification", "disabled", "new"]
    """
    A machine-readable identifier for the specific status, useful for programmatic
    handling.
    """

    source: Literal["watchtower"]
    """Identifies the origin of the status change (e.g., `watchtower`).

    This helps in tracking the cause of status updates.
    """


class Data(BaseModel):
    id: str
    """Unique identifier for the representative."""

    account_id: str
    """The unique identifier of the account this representative is associated with."""

    created_at: datetime
    """Timestamp of when the representative was created."""

    dob: date
    """The date of birth of the representative, in ISO 8601 format (YYYY-MM-DD)."""

    email: Optional[str] = None
    """The email address of the representative."""

    first_name: str
    """The first name of the representative."""

    last_name: str
    """The last name of the representative."""

    mobile_number: str
    """The mobile phone number of the representative."""

    name: str

    relationship: DataRelationship

    ssn_last4: str
    """The last 4 digits of the representative's Social Security Number."""

    status: Literal["created", "onboarding", "active", "rejected", "inactive"]
    """The current status of the representative."""

    status_detail: DataStatusDetail

    updated_at: datetime
    """Timestamp of the most recent update to the representative."""

    external_id: Optional[str] = None
    """
    Unique identifier for the representative in your database, used for
    cross-referencing between Straddle and your systems.
    """

    phone: Optional[str] = None

    user_id: Optional[str] = None
    """
    The unique identifier of the user account associated with this representative,
    if applicable.
    """


class RepresentativePaged(BaseModel):
    data: List[Data]

    meta: PagedResponseMetadata
    """
    Metadata about the API request, including an identifier, timestamp, and
    pagination details.
    """

    response_type: Literal["object", "array", "error", "none"]
    """Indicates the structure of the returned content.

    - "object" means the `data` field contains a single JSON object.
    - "array" means the `data` field contains an array of objects.
    - "error" means the `data` field contains an error object with details of the
      issue.
    - "none" means no data is returned.
    """
