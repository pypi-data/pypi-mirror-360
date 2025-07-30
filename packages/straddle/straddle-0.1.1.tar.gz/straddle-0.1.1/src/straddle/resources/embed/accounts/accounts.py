# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Literal

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, strip_not_given, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....pagination import SyncPageNumberSchema, AsyncPageNumberSchema
from ....types.embed import (
    account_list_params,
    account_create_params,
    account_update_params,
    account_onboard_params,
    account_simulate_params,
)
from ...._base_client import AsyncPaginator, make_request_options
from .capability_requests import (
    CapabilityRequestsResource,
    AsyncCapabilityRequestsResource,
    CapabilityRequestsResourceWithRawResponse,
    AsyncCapabilityRequestsResourceWithRawResponse,
    CapabilityRequestsResourceWithStreamingResponse,
    AsyncCapabilityRequestsResourceWithStreamingResponse,
)
from ....types.embed.account_v1 import AccountV1
from ....types.embed.account_paged_v1 import Data
from ....types.embed.business_profile_v1_param import BusinessProfileV1Param
from ....types.embed.terms_of_service_v1_param import TermsOfServiceV1Param

__all__ = ["AccountsResource", "AsyncAccountsResource"]


class AccountsResource(SyncAPIResource):
    @cached_property
    def capability_requests(self) -> CapabilityRequestsResource:
        return CapabilityRequestsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AccountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return AccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AccountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return AccountsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        access_level: Literal["standard", "managed"],
        account_type: Literal["business"],
        business_profile: BusinessProfileV1Param,
        organization_id: str,
        external_id: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[Dict[str, Optional[str]]] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AccountV1:
        """Creates a new account associated with your Straddle platform integration.

        This
        endpoint allows you to set up an account with specified details, including
        business information and access levels.

        Args:
          access_level: The access level granted to the account. This is determined by your platform
              configuration. Use `standard` unless instructed otherwise by Straddle.

          account_type: The type of account to be created. Currently, only `business` is supported.

          organization_id: The unique identifier of the organization related to this account.

          external_id: Unique identifier for the account in your database, used for cross-referencing
              between Straddle and your systems.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the account in a structured format.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "correlation-id": correlation_id,
                    "request-id": request_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            "/v1/accounts",
            body=maybe_transform(
                {
                    "access_level": access_level,
                    "account_type": account_type,
                    "business_profile": business_profile,
                    "organization_id": organization_id,
                    "external_id": external_id,
                    "metadata": metadata,
                },
                account_create_params.AccountCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccountV1,
        )

    def update(
        self,
        account_id: str,
        *,
        business_profile: BusinessProfileV1Param,
        external_id: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[Dict[str, Optional[str]]] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AccountV1:
        """Updates an existing account's information.

        This endpoint allows you to update
        various account details during onboarding or after the account has been created.

        Args:
          external_id: Unique identifier for the account in your database, used for cross-referencing
              between Straddle and your systems.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the account in a structured format.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "correlation-id": correlation_id,
                    "request-id": request_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._put(
            f"/v1/accounts/{account_id}",
            body=maybe_transform(
                {
                    "business_profile": business_profile,
                    "external_id": external_id,
                    "metadata": metadata,
                },
                account_update_params.AccountUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccountV1,
        )

    def list(
        self,
        *,
        page_number: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        search_text: str | NotGiven = NOT_GIVEN,
        sort_by: str | NotGiven = NOT_GIVEN,
        sort_order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        status: Literal["created", "onboarding", "active", "rejected", "inactive"] | NotGiven = NOT_GIVEN,
        type: Literal["business"] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncPageNumberSchema[Data]:
        """
        Returns a list of accounts associated with your Straddle platform integration.
        The accounts are returned sorted by creation date, with the most recently
        created accounts appearing first. This endpoint supports advanced sorting and
        filtering options.

        Args:
          page_number: Results page number. Starts at page 1. Default value: 1

          page_size: Page size. Default value: 100. Max value: 1000

          sort_by: Sort By. Default value: 'id'.

          sort_order: Sort Order. Default value: 'asc'.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "correlation-id": correlation_id,
                    "request-id": request_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._get_api_list(
            "/v1/accounts",
            page=SyncPageNumberSchema[Data],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "page_number": page_number,
                        "page_size": page_size,
                        "search_text": search_text,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "status": status,
                        "type": type,
                    },
                    account_list_params.AccountListParams,
                ),
            ),
            model=Data,
        )

    def get(
        self,
        account_id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AccountV1:
        """Retrieves the details of an account that has previously been created.

        Supply the
        unique account ID that was returned from your previous request, and Straddle
        will return the corresponding account information.

        Args:
          account_id: The unique identifier of the account to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "correlation-id": correlation_id,
                    "request-id": request_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._get(
            f"/v1/accounts/{account_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccountV1,
        )

    def onboard(
        self,
        account_id: str,
        *,
        terms_of_service: TermsOfServiceV1Param,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AccountV1:
        """Initiates the onboarding process for a new account.

        This endpoint can only be
        used for accounts where at least one representative and one bank account have
        already been created.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "correlation-id": correlation_id,
                    "request-id": request_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/v1/accounts/{account_id}/onboard",
            body=maybe_transform({"terms_of_service": terms_of_service}, account_onboard_params.AccountOnboardParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccountV1,
        )

    def simulate(
        self,
        account_id: str,
        *,
        final_status: Literal["onboarding", "active"] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AccountV1:
        """Simulate the status transitions for sandbox accounts.

        This endpoint can only be
        used for sandbox accounts.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "correlation-id": correlation_id,
                    "request-id": request_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/v1/accounts/{account_id}/simulate",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"final_status": final_status}, account_simulate_params.AccountSimulateParams),
            ),
            cast_to=AccountV1,
        )


class AsyncAccountsResource(AsyncAPIResource):
    @cached_property
    def capability_requests(self) -> AsyncCapabilityRequestsResource:
        return AsyncCapabilityRequestsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAccountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAccountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return AsyncAccountsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        access_level: Literal["standard", "managed"],
        account_type: Literal["business"],
        business_profile: BusinessProfileV1Param,
        organization_id: str,
        external_id: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[Dict[str, Optional[str]]] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AccountV1:
        """Creates a new account associated with your Straddle platform integration.

        This
        endpoint allows you to set up an account with specified details, including
        business information and access levels.

        Args:
          access_level: The access level granted to the account. This is determined by your platform
              configuration. Use `standard` unless instructed otherwise by Straddle.

          account_type: The type of account to be created. Currently, only `business` is supported.

          organization_id: The unique identifier of the organization related to this account.

          external_id: Unique identifier for the account in your database, used for cross-referencing
              between Straddle and your systems.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the account in a structured format.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "correlation-id": correlation_id,
                    "request-id": request_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            "/v1/accounts",
            body=await async_maybe_transform(
                {
                    "access_level": access_level,
                    "account_type": account_type,
                    "business_profile": business_profile,
                    "organization_id": organization_id,
                    "external_id": external_id,
                    "metadata": metadata,
                },
                account_create_params.AccountCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccountV1,
        )

    async def update(
        self,
        account_id: str,
        *,
        business_profile: BusinessProfileV1Param,
        external_id: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[Dict[str, Optional[str]]] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AccountV1:
        """Updates an existing account's information.

        This endpoint allows you to update
        various account details during onboarding or after the account has been created.

        Args:
          external_id: Unique identifier for the account in your database, used for cross-referencing
              between Straddle and your systems.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the account in a structured format.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "correlation-id": correlation_id,
                    "request-id": request_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._put(
            f"/v1/accounts/{account_id}",
            body=await async_maybe_transform(
                {
                    "business_profile": business_profile,
                    "external_id": external_id,
                    "metadata": metadata,
                },
                account_update_params.AccountUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccountV1,
        )

    def list(
        self,
        *,
        page_number: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        search_text: str | NotGiven = NOT_GIVEN,
        sort_by: str | NotGiven = NOT_GIVEN,
        sort_order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        status: Literal["created", "onboarding", "active", "rejected", "inactive"] | NotGiven = NOT_GIVEN,
        type: Literal["business"] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[Data, AsyncPageNumberSchema[Data]]:
        """
        Returns a list of accounts associated with your Straddle platform integration.
        The accounts are returned sorted by creation date, with the most recently
        created accounts appearing first. This endpoint supports advanced sorting and
        filtering options.

        Args:
          page_number: Results page number. Starts at page 1. Default value: 1

          page_size: Page size. Default value: 100. Max value: 1000

          sort_by: Sort By. Default value: 'id'.

          sort_order: Sort Order. Default value: 'asc'.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "correlation-id": correlation_id,
                    "request-id": request_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._get_api_list(
            "/v1/accounts",
            page=AsyncPageNumberSchema[Data],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "page_number": page_number,
                        "page_size": page_size,
                        "search_text": search_text,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "status": status,
                        "type": type,
                    },
                    account_list_params.AccountListParams,
                ),
            ),
            model=Data,
        )

    async def get(
        self,
        account_id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AccountV1:
        """Retrieves the details of an account that has previously been created.

        Supply the
        unique account ID that was returned from your previous request, and Straddle
        will return the corresponding account information.

        Args:
          account_id: The unique identifier of the account to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "correlation-id": correlation_id,
                    "request-id": request_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._get(
            f"/v1/accounts/{account_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccountV1,
        )

    async def onboard(
        self,
        account_id: str,
        *,
        terms_of_service: TermsOfServiceV1Param,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AccountV1:
        """Initiates the onboarding process for a new account.

        This endpoint can only be
        used for accounts where at least one representative and one bank account have
        already been created.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "correlation-id": correlation_id,
                    "request-id": request_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/v1/accounts/{account_id}/onboard",
            body=await async_maybe_transform(
                {"terms_of_service": terms_of_service}, account_onboard_params.AccountOnboardParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccountV1,
        )

    async def simulate(
        self,
        account_id: str,
        *,
        final_status: Literal["onboarding", "active"] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AccountV1:
        """Simulate the status transitions for sandbox accounts.

        This endpoint can only be
        used for sandbox accounts.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "correlation-id": correlation_id,
                    "request-id": request_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/v1/accounts/{account_id}/simulate",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"final_status": final_status}, account_simulate_params.AccountSimulateParams
                ),
            ),
            cast_to=AccountV1,
        )


class AccountsResourceWithRawResponse:
    def __init__(self, accounts: AccountsResource) -> None:
        self._accounts = accounts

        self.create = to_raw_response_wrapper(
            accounts.create,
        )
        self.update = to_raw_response_wrapper(
            accounts.update,
        )
        self.list = to_raw_response_wrapper(
            accounts.list,
        )
        self.get = to_raw_response_wrapper(
            accounts.get,
        )
        self.onboard = to_raw_response_wrapper(
            accounts.onboard,
        )
        self.simulate = to_raw_response_wrapper(
            accounts.simulate,
        )

    @cached_property
    def capability_requests(self) -> CapabilityRequestsResourceWithRawResponse:
        return CapabilityRequestsResourceWithRawResponse(self._accounts.capability_requests)


class AsyncAccountsResourceWithRawResponse:
    def __init__(self, accounts: AsyncAccountsResource) -> None:
        self._accounts = accounts

        self.create = async_to_raw_response_wrapper(
            accounts.create,
        )
        self.update = async_to_raw_response_wrapper(
            accounts.update,
        )
        self.list = async_to_raw_response_wrapper(
            accounts.list,
        )
        self.get = async_to_raw_response_wrapper(
            accounts.get,
        )
        self.onboard = async_to_raw_response_wrapper(
            accounts.onboard,
        )
        self.simulate = async_to_raw_response_wrapper(
            accounts.simulate,
        )

    @cached_property
    def capability_requests(self) -> AsyncCapabilityRequestsResourceWithRawResponse:
        return AsyncCapabilityRequestsResourceWithRawResponse(self._accounts.capability_requests)


class AccountsResourceWithStreamingResponse:
    def __init__(self, accounts: AccountsResource) -> None:
        self._accounts = accounts

        self.create = to_streamed_response_wrapper(
            accounts.create,
        )
        self.update = to_streamed_response_wrapper(
            accounts.update,
        )
        self.list = to_streamed_response_wrapper(
            accounts.list,
        )
        self.get = to_streamed_response_wrapper(
            accounts.get,
        )
        self.onboard = to_streamed_response_wrapper(
            accounts.onboard,
        )
        self.simulate = to_streamed_response_wrapper(
            accounts.simulate,
        )

    @cached_property
    def capability_requests(self) -> CapabilityRequestsResourceWithStreamingResponse:
        return CapabilityRequestsResourceWithStreamingResponse(self._accounts.capability_requests)


class AsyncAccountsResourceWithStreamingResponse:
    def __init__(self, accounts: AsyncAccountsResource) -> None:
        self._accounts = accounts

        self.create = async_to_streamed_response_wrapper(
            accounts.create,
        )
        self.update = async_to_streamed_response_wrapper(
            accounts.update,
        )
        self.list = async_to_streamed_response_wrapper(
            accounts.list,
        )
        self.get = async_to_streamed_response_wrapper(
            accounts.get,
        )
        self.onboard = async_to_streamed_response_wrapper(
            accounts.onboard,
        )
        self.simulate = async_to_streamed_response_wrapper(
            accounts.simulate,
        )

    @cached_property
    def capability_requests(self) -> AsyncCapabilityRequestsResourceWithStreamingResponse:
        return AsyncCapabilityRequestsResourceWithStreamingResponse(self._accounts.capability_requests)
