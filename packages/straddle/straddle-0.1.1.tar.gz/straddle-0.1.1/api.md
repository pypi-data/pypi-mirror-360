# Shared Types

```python
from straddle.types import (
    CustomerDetailsV1,
    DeviceInfoV1,
    PagedResponseMetadata,
    PaykeyDetailsV1,
    ResponseMetadata,
    StatusDetailsV1,
)
```

# Embed

## Accounts

Types:

```python
from straddle.types.embed import (
    AccountPagedV1,
    AccountV1,
    AddressV1,
    BusinessProfileV1,
    CapabilityV1,
    IndustryV1,
    SupportChannelsV1,
    TermsOfServiceV1,
)
```

Methods:

- <code title="post /v1/accounts">client.embed.accounts.<a href="./src/straddle/resources/embed/accounts/accounts.py">create</a>(\*\*<a href="src/straddle/types/embed/account_create_params.py">params</a>) -> <a href="./src/straddle/types/embed/account_v1.py">AccountV1</a></code>
- <code title="put /v1/accounts/{account_id}">client.embed.accounts.<a href="./src/straddle/resources/embed/accounts/accounts.py">update</a>(account_id, \*\*<a href="src/straddle/types/embed/account_update_params.py">params</a>) -> <a href="./src/straddle/types/embed/account_v1.py">AccountV1</a></code>
- <code title="get /v1/accounts">client.embed.accounts.<a href="./src/straddle/resources/embed/accounts/accounts.py">list</a>(\*\*<a href="src/straddle/types/embed/account_list_params.py">params</a>) -> SyncPageNumberSchema[Data]</code>
- <code title="get /v1/accounts/{account_id}">client.embed.accounts.<a href="./src/straddle/resources/embed/accounts/accounts.py">get</a>(account_id) -> <a href="./src/straddle/types/embed/account_v1.py">AccountV1</a></code>
- <code title="post /v1/accounts/{account_id}/onboard">client.embed.accounts.<a href="./src/straddle/resources/embed/accounts/accounts.py">onboard</a>(account_id, \*\*<a href="src/straddle/types/embed/account_onboard_params.py">params</a>) -> <a href="./src/straddle/types/embed/account_v1.py">AccountV1</a></code>
- <code title="post /v1/accounts/{account_id}/simulate">client.embed.accounts.<a href="./src/straddle/resources/embed/accounts/accounts.py">simulate</a>(account_id, \*\*<a href="src/straddle/types/embed/account_simulate_params.py">params</a>) -> <a href="./src/straddle/types/embed/account_v1.py">AccountV1</a></code>

### CapabilityRequests

Types:

```python
from straddle.types.embed.accounts import CapabilityRequestPagedV1
```

Methods:

- <code title="post /v1/accounts/{account_id}/capability_requests">client.embed.accounts.capability_requests.<a href="./src/straddle/resources/embed/accounts/capability_requests.py">create</a>(account_id, \*\*<a href="src/straddle/types/embed/accounts/capability_request_create_params.py">params</a>) -> <a href="./src/straddle/types/embed/accounts/capability_request_paged_v1.py">CapabilityRequestPagedV1</a></code>
- <code title="get /v1/accounts/{account_id}/capability_requests">client.embed.accounts.capability_requests.<a href="./src/straddle/resources/embed/accounts/capability_requests.py">list</a>(account_id, \*\*<a href="src/straddle/types/embed/accounts/capability_request_list_params.py">params</a>) -> SyncPageNumberSchema[Data]</code>

## LinkedBankAccounts

Types:

```python
from straddle.types.embed import (
    LinkedBankAccountPagedV1,
    LinkedBankAccountUnmaskV1,
    LinkedBankAccountV1,
)
```

Methods:

- <code title="post /v1/linked_bank_accounts">client.embed.linked_bank_accounts.<a href="./src/straddle/resources/embed/linked_bank_accounts.py">create</a>(\*\*<a href="src/straddle/types/embed/linked_bank_account_create_params.py">params</a>) -> <a href="./src/straddle/types/embed/linked_bank_account_v1.py">LinkedBankAccountV1</a></code>
- <code title="put /v1/linked_bank_accounts/{linked_bank_account_id}">client.embed.linked_bank_accounts.<a href="./src/straddle/resources/embed/linked_bank_accounts.py">update</a>(linked_bank_account_id, \*\*<a href="src/straddle/types/embed/linked_bank_account_update_params.py">params</a>) -> <a href="./src/straddle/types/embed/linked_bank_account_v1.py">LinkedBankAccountV1</a></code>
- <code title="get /v1/linked_bank_accounts">client.embed.linked_bank_accounts.<a href="./src/straddle/resources/embed/linked_bank_accounts.py">list</a>(\*\*<a href="src/straddle/types/embed/linked_bank_account_list_params.py">params</a>) -> SyncPageNumberSchema[Data]</code>
- <code title="get /v1/linked_bank_accounts/{linked_bank_account_id}">client.embed.linked_bank_accounts.<a href="./src/straddle/resources/embed/linked_bank_accounts.py">get</a>(linked_bank_account_id) -> <a href="./src/straddle/types/embed/linked_bank_account_v1.py">LinkedBankAccountV1</a></code>
- <code title="get /v1/linked_bank_accounts/{linked_bank_account_id}/unmask">client.embed.linked_bank_accounts.<a href="./src/straddle/resources/embed/linked_bank_accounts.py">unmask</a>(linked_bank_account_id) -> <a href="./src/straddle/types/embed/linked_bank_account_unmask_v1.py">LinkedBankAccountUnmaskV1</a></code>

## Organizations

Types:

```python
from straddle.types.embed import OrganizationPagedV1, OrganizationV1
```

Methods:

- <code title="post /v1/organizations">client.embed.organizations.<a href="./src/straddle/resources/embed/organizations.py">create</a>(\*\*<a href="src/straddle/types/embed/organization_create_params.py">params</a>) -> <a href="./src/straddle/types/embed/organization_v1.py">OrganizationV1</a></code>
- <code title="get /v1/organizations">client.embed.organizations.<a href="./src/straddle/resources/embed/organizations.py">list</a>(\*\*<a href="src/straddle/types/embed/organization_list_params.py">params</a>) -> SyncPageNumberSchema[Data]</code>
- <code title="get /v1/organizations/{organization_id}">client.embed.organizations.<a href="./src/straddle/resources/embed/organizations.py">get</a>(organization_id) -> <a href="./src/straddle/types/embed/organization_v1.py">OrganizationV1</a></code>

## Representatives

Types:

```python
from straddle.types.embed import Representative, RepresentativePaged
```

Methods:

- <code title="post /v1/representatives">client.embed.representatives.<a href="./src/straddle/resources/embed/representatives.py">create</a>(\*\*<a href="src/straddle/types/embed/representative_create_params.py">params</a>) -> <a href="./src/straddle/types/embed/representative.py">Representative</a></code>
- <code title="put /v1/representatives/{representative_id}">client.embed.representatives.<a href="./src/straddle/resources/embed/representatives.py">update</a>(representative_id, \*\*<a href="src/straddle/types/embed/representative_update_params.py">params</a>) -> <a href="./src/straddle/types/embed/representative.py">Representative</a></code>
- <code title="get /v1/representatives">client.embed.representatives.<a href="./src/straddle/resources/embed/representatives.py">list</a>(\*\*<a href="src/straddle/types/embed/representative_list_params.py">params</a>) -> SyncPageNumberSchema[Data]</code>
- <code title="get /v1/representatives/{representative_id}">client.embed.representatives.<a href="./src/straddle/resources/embed/representatives.py">get</a>(representative_id) -> <a href="./src/straddle/types/embed/representative.py">Representative</a></code>
- <code title="get /v1/representatives/{representative_id}/unmask">client.embed.representatives.<a href="./src/straddle/resources/embed/representatives.py">unmask</a>(representative_id) -> <a href="./src/straddle/types/embed/representative.py">Representative</a></code>

# Bridge

Types:

```python
from straddle.types import BridgeTokenV1
```

Methods:

- <code title="post /v1/bridge/initialize">client.bridge.<a href="./src/straddle/resources/bridge/bridge.py">initialize</a>(\*\*<a href="src/straddle/types/bridge_initialize_params.py">params</a>) -> <a href="./src/straddle/types/bridge_token_v1.py">BridgeTokenV1</a></code>

## Link

Types:

```python
from straddle.types.bridge import LinkCreatePaykeyResponse, LinkCreateTanResponse
```

Methods:

- <code title="post /v1/bridge/bank_account">client.bridge.link.<a href="./src/straddle/resources/bridge/link.py">bank_account</a>(\*\*<a href="src/straddle/types/bridge/link_bank_account_params.py">params</a>) -> <a href="./src/straddle/types/paykey_v1.py">PaykeyV1</a></code>
- <code title="post /v1/bridge/quiltt">client.bridge.link.<a href="./src/straddle/resources/bridge/link.py">create_paykey</a>(\*\*<a href="src/straddle/types/bridge/link_create_paykey_params.py">params</a>) -> <a href="./src/straddle/types/bridge/link_create_paykey_response.py">LinkCreatePaykeyResponse</a></code>
- <code title="post /v1/bridge/tan">client.bridge.link.<a href="./src/straddle/resources/bridge/link.py">create_tan</a>(\*\*<a href="src/straddle/types/bridge/link_create_tan_params.py">params</a>) -> <a href="./src/straddle/types/bridge/link_create_tan_response.py">LinkCreateTanResponse</a></code>
- <code title="post /v1/bridge/plaid">client.bridge.link.<a href="./src/straddle/resources/bridge/link.py">plaid</a>(\*\*<a href="src/straddle/types/bridge/link_plaid_params.py">params</a>) -> <a href="./src/straddle/types/paykey_v1.py">PaykeyV1</a></code>

# Customers

Types:

```python
from straddle.types import (
    CustomerAddressV1,
    CustomerSummaryPagedV1,
    CustomerUnmaskedV1,
    CustomerV1,
    DeviceUnmaskedV1,
)
```

Methods:

- <code title="post /v1/customers">client.customers.<a href="./src/straddle/resources/customers/customers.py">create</a>(\*\*<a href="src/straddle/types/customer_create_params.py">params</a>) -> <a href="./src/straddle/types/customer_v1.py">CustomerV1</a></code>
- <code title="put /v1/customers/{id}">client.customers.<a href="./src/straddle/resources/customers/customers.py">update</a>(id, \*\*<a href="src/straddle/types/customer_update_params.py">params</a>) -> <a href="./src/straddle/types/customer_v1.py">CustomerV1</a></code>
- <code title="get /v1/customers">client.customers.<a href="./src/straddle/resources/customers/customers.py">list</a>(\*\*<a href="src/straddle/types/customer_list_params.py">params</a>) -> SyncPageNumberSchema[Data]</code>
- <code title="delete /v1/customers/{id}">client.customers.<a href="./src/straddle/resources/customers/customers.py">delete</a>(id) -> <a href="./src/straddle/types/customer_v1.py">CustomerV1</a></code>
- <code title="get /v1/customers/{id}">client.customers.<a href="./src/straddle/resources/customers/customers.py">get</a>(id) -> <a href="./src/straddle/types/customer_v1.py">CustomerV1</a></code>
- <code title="put /v1/customers/{id}/refresh_review">client.customers.<a href="./src/straddle/resources/customers/customers.py">refresh_review</a>(id) -> <a href="./src/straddle/types/customer_v1.py">CustomerV1</a></code>
- <code title="get /v1/customers/{id}/unmasked">client.customers.<a href="./src/straddle/resources/customers/customers.py">unmasked</a>(id) -> <a href="./src/straddle/types/customer_unmasked_v1.py">CustomerUnmaskedV1</a></code>

## Review

Types:

```python
from straddle.types.customers import CustomerReviewV1, IdentityVerificationBreakdownV1
```

Methods:

- <code title="patch /v1/customers/{id}/review">client.customers.review.<a href="./src/straddle/resources/customers/review.py">decision</a>(id, \*\*<a href="src/straddle/types/customers/review_decision_params.py">params</a>) -> <a href="./src/straddle/types/customer_v1.py">CustomerV1</a></code>
- <code title="get /v1/customers/{id}/review">client.customers.review.<a href="./src/straddle/resources/customers/review.py">get</a>(id) -> <a href="./src/straddle/types/customers/customer_review_v1.py">CustomerReviewV1</a></code>

# Paykeys

Types:

```python
from straddle.types import PaykeySummaryPagedV1, PaykeyUnmaskedV1, PaykeyV1, PaykeyRevealResponse
```

Methods:

- <code title="get /v1/paykeys">client.paykeys.<a href="./src/straddle/resources/paykeys.py">list</a>(\*\*<a href="src/straddle/types/paykey_list_params.py">params</a>) -> SyncPageNumberSchema[Data]</code>
- <code title="put /v1/paykeys/{id}/cancel">client.paykeys.<a href="./src/straddle/resources/paykeys.py">cancel</a>(id, \*\*<a href="src/straddle/types/paykey_cancel_params.py">params</a>) -> <a href="./src/straddle/types/paykey_v1.py">PaykeyV1</a></code>
- <code title="get /v1/paykeys/{id}">client.paykeys.<a href="./src/straddle/resources/paykeys.py">get</a>(id) -> <a href="./src/straddle/types/paykey_v1.py">PaykeyV1</a></code>
- <code title="get /v1/paykeys/{id}/reveal">client.paykeys.<a href="./src/straddle/resources/paykeys.py">reveal</a>(id) -> <a href="./src/straddle/types/paykey_reveal_response.py">PaykeyRevealResponse</a></code>
- <code title="get /v1/paykeys/{id}/unmasked">client.paykeys.<a href="./src/straddle/resources/paykeys.py">unmasked</a>(id) -> <a href="./src/straddle/types/paykey_unmasked_v1.py">PaykeyUnmaskedV1</a></code>

# Charges

Types:

```python
from straddle.types import ChargeV1, ChargeUnmaskResponse
```

Methods:

- <code title="post /v1/charges">client.charges.<a href="./src/straddle/resources/charges.py">create</a>(\*\*<a href="src/straddle/types/charge_create_params.py">params</a>) -> <a href="./src/straddle/types/charge_v1.py">ChargeV1</a></code>
- <code title="put /v1/charges/{id}">client.charges.<a href="./src/straddle/resources/charges.py">update</a>(id, \*\*<a href="src/straddle/types/charge_update_params.py">params</a>) -> <a href="./src/straddle/types/charge_v1.py">ChargeV1</a></code>
- <code title="put /v1/charges/{id}/cancel">client.charges.<a href="./src/straddle/resources/charges.py">cancel</a>(id, \*\*<a href="src/straddle/types/charge_cancel_params.py">params</a>) -> <a href="./src/straddle/types/charge_v1.py">ChargeV1</a></code>
- <code title="get /v1/charges/{id}">client.charges.<a href="./src/straddle/resources/charges.py">get</a>(id) -> <a href="./src/straddle/types/charge_v1.py">ChargeV1</a></code>
- <code title="put /v1/charges/{id}/hold">client.charges.<a href="./src/straddle/resources/charges.py">hold</a>(id, \*\*<a href="src/straddle/types/charge_hold_params.py">params</a>) -> <a href="./src/straddle/types/charge_v1.py">ChargeV1</a></code>
- <code title="put /v1/charges/{id}/release">client.charges.<a href="./src/straddle/resources/charges.py">release</a>(id, \*\*<a href="src/straddle/types/charge_release_params.py">params</a>) -> <a href="./src/straddle/types/charge_v1.py">ChargeV1</a></code>
- <code title="get /v1/charges/{id}/unmask">client.charges.<a href="./src/straddle/resources/charges.py">unmask</a>(id) -> <a href="./src/straddle/types/charge_unmask_response.py">ChargeUnmaskResponse</a></code>

# FundingEvents

Types:

```python
from straddle.types import FundingEventSummaryItemV1, FundingEventSummaryPagedV1
```

Methods:

- <code title="get /v1/funding_events">client.funding_events.<a href="./src/straddle/resources/funding_events.py">list</a>(\*\*<a href="src/straddle/types/funding_event_list_params.py">params</a>) -> SyncPageNumberSchema[Data]</code>
- <code title="get /v1/funding_events/{id}">client.funding_events.<a href="./src/straddle/resources/funding_events.py">get</a>(id) -> <a href="./src/straddle/types/funding_event_summary_item_v1.py">FundingEventSummaryItemV1</a></code>

# Payments

Types:

```python
from straddle.types import PaymentSummaryPagedV1
```

Methods:

- <code title="get /v1/payments">client.payments.<a href="./src/straddle/resources/payments.py">list</a>(\*\*<a href="src/straddle/types/payment_list_params.py">params</a>) -> SyncPageNumberSchema[Data]</code>

# Payouts

Types:

```python
from straddle.types import PayoutV1, PayoutUnmaskResponse
```

Methods:

- <code title="post /v1/payouts">client.payouts.<a href="./src/straddle/resources/payouts.py">create</a>(\*\*<a href="src/straddle/types/payout_create_params.py">params</a>) -> <a href="./src/straddle/types/payout_v1.py">PayoutV1</a></code>
- <code title="put /v1/payouts/{id}">client.payouts.<a href="./src/straddle/resources/payouts.py">update</a>(id, \*\*<a href="src/straddle/types/payout_update_params.py">params</a>) -> <a href="./src/straddle/types/payout_v1.py">PayoutV1</a></code>
- <code title="put /v1/payouts/{id}/cancel">client.payouts.<a href="./src/straddle/resources/payouts.py">cancel</a>(id, \*\*<a href="src/straddle/types/payout_cancel_params.py">params</a>) -> <a href="./src/straddle/types/payout_v1.py">PayoutV1</a></code>
- <code title="get /v1/payouts/{id}">client.payouts.<a href="./src/straddle/resources/payouts.py">get</a>(id) -> <a href="./src/straddle/types/payout_v1.py">PayoutV1</a></code>
- <code title="put /v1/payouts/{id}/hold">client.payouts.<a href="./src/straddle/resources/payouts.py">hold</a>(id, \*\*<a href="src/straddle/types/payout_hold_params.py">params</a>) -> <a href="./src/straddle/types/payout_v1.py">PayoutV1</a></code>
- <code title="put /v1/payouts/{id}/release">client.payouts.<a href="./src/straddle/resources/payouts.py">release</a>(id, \*\*<a href="src/straddle/types/payout_release_params.py">params</a>) -> <a href="./src/straddle/types/payout_v1.py">PayoutV1</a></code>
- <code title="get /v1/payouts/{id}/unmask">client.payouts.<a href="./src/straddle/resources/payouts.py">unmask</a>(id) -> <a href="./src/straddle/types/payout_unmask_response.py">PayoutUnmaskResponse</a></code>

# Reports

Types:

```python
from straddle.types import ReportCreateTotalCustomersByStatusResponse
```

Methods:

- <code title="post /v1/reports/total_customers_by_status">client.reports.<a href="./src/straddle/resources/reports.py">create_total_customers_by_status</a>() -> <a href="./src/straddle/types/report_create_total_customers_by_status_response.py">ReportCreateTotalCustomersByStatusResponse</a></code>
