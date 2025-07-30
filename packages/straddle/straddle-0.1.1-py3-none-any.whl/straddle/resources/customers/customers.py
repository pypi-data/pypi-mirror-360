# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import Literal

import httpx

from .review import (
    ReviewResource,
    AsyncReviewResource,
    ReviewResourceWithRawResponse,
    AsyncReviewResourceWithRawResponse,
    ReviewResourceWithStreamingResponse,
    AsyncReviewResourceWithStreamingResponse,
)
from ...types import (
    customer_list_params,
    customer_create_params,
    customer_update_params,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, strip_not_given, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...pagination import SyncPageNumberSchema, AsyncPageNumberSchema
from ..._base_client import AsyncPaginator, make_request_options
from ...types.customer_v1 import CustomerV1
from ...types.customer_unmasked_v1 import CustomerUnmaskedV1
from ...types.device_unmasked_v1_param import DeviceUnmaskedV1Param
from ...types.customer_address_v1_param import CustomerAddressV1Param
from ...types.customer_summary_paged_v1 import Data

__all__ = ["CustomersResource", "AsyncCustomersResource"]


class CustomersResource(SyncAPIResource):
    @cached_property
    def review(self) -> ReviewResource:
        return ReviewResource(self._client)

    @cached_property
    def with_raw_response(self) -> CustomersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return CustomersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CustomersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return CustomersResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        device: DeviceUnmaskedV1Param,
        email: str,
        name: str,
        phone: str,
        type: Literal["individual", "business"],
        address: Optional[CustomerAddressV1Param] | NotGiven = NOT_GIVEN,
        compliance_profile: Optional[customer_create_params.ComplianceProfile] | NotGiven = NOT_GIVEN,
        config: customer_create_params.Config | NotGiven = NOT_GIVEN,
        external_id: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[Dict[str, str]] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomerV1:
        """
        Creates a new customer record and automatically initiates identity, fraud, and
        risk assessment scores. This endpoint allows you to create a customer profile
        and associate it with paykeys and payments.

        Args:
          email: The customer's email address.

          name: Full name of the individual or business name.

          phone: The customer's phone number in E.164 format. Mobile number is preferred.

          address: An object containing the customer's address. **This is optional.** If used, all
              required fields must be present.

          compliance_profile: An object containing the customer's compliance profile. **This is optional.** If
              all required fields must be present for the appropriate customer type.

          external_id: Unique identifier for the customer in your database, used for cross-referencing
              between Straddle and your systems.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the customer in a structured format.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            "/v1/customers",
            body=maybe_transform(
                {
                    "device": device,
                    "email": email,
                    "name": name,
                    "phone": phone,
                    "type": type,
                    "address": address,
                    "compliance_profile": compliance_profile,
                    "config": config,
                    "external_id": external_id,
                    "metadata": metadata,
                },
                customer_create_params.CustomerCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomerV1,
        )

    def update(
        self,
        id: str,
        *,
        device: DeviceUnmaskedV1Param,
        email: str,
        name: str,
        phone: str,
        status: Literal["pending", "review", "verified", "inactive", "rejected"],
        address: Optional[CustomerAddressV1Param] | NotGiven = NOT_GIVEN,
        compliance_profile: Optional[customer_update_params.ComplianceProfile] | NotGiven = NOT_GIVEN,
        external_id: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[Dict[str, str]] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomerV1:
        """Updates an existing customer's information.

        This endpoint allows you to modify
        the customer's contact details, PII, and metadata.

        Args:
          email: The customer's email address.

          name: The customer's full name or business name.

          phone: The customer's phone number in E.164 format.

          address: An object containing the customer's address. This is optional, but if provided,
              all required fields must be present.

          compliance_profile: Individual PII data required to trigger Patriot Act compliant KYC verification.

          external_id: Unique identifier for the customer in your database, used for cross-referencing
              between Straddle and your systems.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the customer in a structured format.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._put(
            f"/v1/customers/{id}",
            body=maybe_transform(
                {
                    "device": device,
                    "email": email,
                    "name": name,
                    "phone": phone,
                    "status": status,
                    "address": address,
                    "compliance_profile": compliance_profile,
                    "external_id": external_id,
                    "metadata": metadata,
                },
                customer_update_params.CustomerUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomerV1,
        )

    def list(
        self,
        *,
        created_from: Union[str, datetime] | NotGiven = NOT_GIVEN,
        created_to: Union[str, datetime] | NotGiven = NOT_GIVEN,
        email: str | NotGiven = NOT_GIVEN,
        external_id: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        page_number: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        search_text: str | NotGiven = NOT_GIVEN,
        sort_by: Literal["name", "created_at"] | NotGiven = NOT_GIVEN,
        sort_order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        status: List[Literal["pending", "review", "verified", "inactive", "rejected"]] | NotGiven = NOT_GIVEN,
        types: List[Literal["individual", "business"]] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncPageNumberSchema[Data]:
        """Lists or searches customers connected to your account.

        All supported query
        parameters are optional. If none are provided, the response will include all
        customers connected to your account. This endpoint supports advanced sorting and
        filtering options.

        Args:
          created_from: Start date for filtering by `created_at` date.

          created_to: End date for filtering by `created_at` date.

          email: Filter customers by `email` address.

          external_id: Filter by your system's `external_id`.

          name: Filter customers by `name` (partial match).

          page_number: Page number for paginated results. Starts at 1.

          page_size: Number of results per page. Maximum: 1000.

          search_text: General search term to filter customers.

          status: Filter customers by their current `status`.

          types: Filter by customer type `individual` or `business`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._get_api_list(
            "/v1/customers",
            page=SyncPageNumberSchema[Data],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "created_from": created_from,
                        "created_to": created_to,
                        "email": email,
                        "external_id": external_id,
                        "name": name,
                        "page_number": page_number,
                        "page_size": page_size,
                        "search_text": search_text,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "status": status,
                        "types": types,
                    },
                    customer_list_params.CustomerListParams,
                ),
            ),
            model=Data,
        )

    def delete(
        self,
        id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomerV1:
        """Permanently removes a customer record from Straddle.

        This action cannot be
        undone and should only be used to satisfy regulatory requirements or for privacy
        compliance.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._delete(
            f"/v1/customers/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomerV1,
        )

    def get(
        self,
        id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomerV1:
        """Retrieves the details of an existing customer.

        Supply the unique customer ID
        that was returned from your 'create customer' request, and Straddle will return
        the corresponding customer information.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._get(
            f"/v1/customers/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomerV1,
        )

    def refresh_review(
        self,
        id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomerV1:
        """Updates the decision of a customer's identity validation.

        This endpoint allows
        you to modify the outcome of a customer decision and is useful for correcting or
        updating the status of a customer's verification.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._put(
            f"/v1/customers/{id}/refresh_review",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomerV1,
        )

    def unmasked(
        self,
        id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomerUnmaskedV1:
        """Retrieves the unmasked details, including PII, of an existing customer.

        Supply
        the unique customer ID that was returned from your 'create customer' request,
        and Straddle will return the corresponding customer information. This endpoint
        needs to be enabled by Straddle and should only be used when absolutely
        necessary.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._get(
            f"/v1/customers/{id}/unmasked",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomerUnmaskedV1,
        )


class AsyncCustomersResource(AsyncAPIResource):
    @cached_property
    def review(self) -> AsyncReviewResource:
        return AsyncReviewResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncCustomersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCustomersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCustomersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return AsyncCustomersResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        device: DeviceUnmaskedV1Param,
        email: str,
        name: str,
        phone: str,
        type: Literal["individual", "business"],
        address: Optional[CustomerAddressV1Param] | NotGiven = NOT_GIVEN,
        compliance_profile: Optional[customer_create_params.ComplianceProfile] | NotGiven = NOT_GIVEN,
        config: customer_create_params.Config | NotGiven = NOT_GIVEN,
        external_id: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[Dict[str, str]] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomerV1:
        """
        Creates a new customer record and automatically initiates identity, fraud, and
        risk assessment scores. This endpoint allows you to create a customer profile
        and associate it with paykeys and payments.

        Args:
          email: The customer's email address.

          name: Full name of the individual or business name.

          phone: The customer's phone number in E.164 format. Mobile number is preferred.

          address: An object containing the customer's address. **This is optional.** If used, all
              required fields must be present.

          compliance_profile: An object containing the customer's compliance profile. **This is optional.** If
              all required fields must be present for the appropriate customer type.

          external_id: Unique identifier for the customer in your database, used for cross-referencing
              between Straddle and your systems.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the customer in a structured format.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            "/v1/customers",
            body=await async_maybe_transform(
                {
                    "device": device,
                    "email": email,
                    "name": name,
                    "phone": phone,
                    "type": type,
                    "address": address,
                    "compliance_profile": compliance_profile,
                    "config": config,
                    "external_id": external_id,
                    "metadata": metadata,
                },
                customer_create_params.CustomerCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomerV1,
        )

    async def update(
        self,
        id: str,
        *,
        device: DeviceUnmaskedV1Param,
        email: str,
        name: str,
        phone: str,
        status: Literal["pending", "review", "verified", "inactive", "rejected"],
        address: Optional[CustomerAddressV1Param] | NotGiven = NOT_GIVEN,
        compliance_profile: Optional[customer_update_params.ComplianceProfile] | NotGiven = NOT_GIVEN,
        external_id: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[Dict[str, str]] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomerV1:
        """Updates an existing customer's information.

        This endpoint allows you to modify
        the customer's contact details, PII, and metadata.

        Args:
          email: The customer's email address.

          name: The customer's full name or business name.

          phone: The customer's phone number in E.164 format.

          address: An object containing the customer's address. This is optional, but if provided,
              all required fields must be present.

          compliance_profile: Individual PII data required to trigger Patriot Act compliant KYC verification.

          external_id: Unique identifier for the customer in your database, used for cross-referencing
              between Straddle and your systems.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the customer in a structured format.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._put(
            f"/v1/customers/{id}",
            body=await async_maybe_transform(
                {
                    "device": device,
                    "email": email,
                    "name": name,
                    "phone": phone,
                    "status": status,
                    "address": address,
                    "compliance_profile": compliance_profile,
                    "external_id": external_id,
                    "metadata": metadata,
                },
                customer_update_params.CustomerUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomerV1,
        )

    def list(
        self,
        *,
        created_from: Union[str, datetime] | NotGiven = NOT_GIVEN,
        created_to: Union[str, datetime] | NotGiven = NOT_GIVEN,
        email: str | NotGiven = NOT_GIVEN,
        external_id: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        page_number: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        search_text: str | NotGiven = NOT_GIVEN,
        sort_by: Literal["name", "created_at"] | NotGiven = NOT_GIVEN,
        sort_order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        status: List[Literal["pending", "review", "verified", "inactive", "rejected"]] | NotGiven = NOT_GIVEN,
        types: List[Literal["individual", "business"]] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[Data, AsyncPageNumberSchema[Data]]:
        """Lists or searches customers connected to your account.

        All supported query
        parameters are optional. If none are provided, the response will include all
        customers connected to your account. This endpoint supports advanced sorting and
        filtering options.

        Args:
          created_from: Start date for filtering by `created_at` date.

          created_to: End date for filtering by `created_at` date.

          email: Filter customers by `email` address.

          external_id: Filter by your system's `external_id`.

          name: Filter customers by `name` (partial match).

          page_number: Page number for paginated results. Starts at 1.

          page_size: Number of results per page. Maximum: 1000.

          search_text: General search term to filter customers.

          status: Filter customers by their current `status`.

          types: Filter by customer type `individual` or `business`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._get_api_list(
            "/v1/customers",
            page=AsyncPageNumberSchema[Data],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "created_from": created_from,
                        "created_to": created_to,
                        "email": email,
                        "external_id": external_id,
                        "name": name,
                        "page_number": page_number,
                        "page_size": page_size,
                        "search_text": search_text,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "status": status,
                        "types": types,
                    },
                    customer_list_params.CustomerListParams,
                ),
            ),
            model=Data,
        )

    async def delete(
        self,
        id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomerV1:
        """Permanently removes a customer record from Straddle.

        This action cannot be
        undone and should only be used to satisfy regulatory requirements or for privacy
        compliance.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._delete(
            f"/v1/customers/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomerV1,
        )

    async def get(
        self,
        id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomerV1:
        """Retrieves the details of an existing customer.

        Supply the unique customer ID
        that was returned from your 'create customer' request, and Straddle will return
        the corresponding customer information.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._get(
            f"/v1/customers/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomerV1,
        )

    async def refresh_review(
        self,
        id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomerV1:
        """Updates the decision of a customer's identity validation.

        This endpoint allows
        you to modify the outcome of a customer decision and is useful for correcting or
        updating the status of a customer's verification.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._put(
            f"/v1/customers/{id}/refresh_review",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomerV1,
        )

    async def unmasked(
        self,
        id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomerUnmaskedV1:
        """Retrieves the unmasked details, including PII, of an existing customer.

        Supply
        the unique customer ID that was returned from your 'create customer' request,
        and Straddle will return the corresponding customer information. This endpoint
        needs to be enabled by Straddle and should only be used when absolutely
        necessary.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._get(
            f"/v1/customers/{id}/unmasked",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomerUnmaskedV1,
        )


class CustomersResourceWithRawResponse:
    def __init__(self, customers: CustomersResource) -> None:
        self._customers = customers

        self.create = to_raw_response_wrapper(
            customers.create,
        )
        self.update = to_raw_response_wrapper(
            customers.update,
        )
        self.list = to_raw_response_wrapper(
            customers.list,
        )
        self.delete = to_raw_response_wrapper(
            customers.delete,
        )
        self.get = to_raw_response_wrapper(
            customers.get,
        )
        self.refresh_review = to_raw_response_wrapper(
            customers.refresh_review,
        )
        self.unmasked = to_raw_response_wrapper(
            customers.unmasked,
        )

    @cached_property
    def review(self) -> ReviewResourceWithRawResponse:
        return ReviewResourceWithRawResponse(self._customers.review)


class AsyncCustomersResourceWithRawResponse:
    def __init__(self, customers: AsyncCustomersResource) -> None:
        self._customers = customers

        self.create = async_to_raw_response_wrapper(
            customers.create,
        )
        self.update = async_to_raw_response_wrapper(
            customers.update,
        )
        self.list = async_to_raw_response_wrapper(
            customers.list,
        )
        self.delete = async_to_raw_response_wrapper(
            customers.delete,
        )
        self.get = async_to_raw_response_wrapper(
            customers.get,
        )
        self.refresh_review = async_to_raw_response_wrapper(
            customers.refresh_review,
        )
        self.unmasked = async_to_raw_response_wrapper(
            customers.unmasked,
        )

    @cached_property
    def review(self) -> AsyncReviewResourceWithRawResponse:
        return AsyncReviewResourceWithRawResponse(self._customers.review)


class CustomersResourceWithStreamingResponse:
    def __init__(self, customers: CustomersResource) -> None:
        self._customers = customers

        self.create = to_streamed_response_wrapper(
            customers.create,
        )
        self.update = to_streamed_response_wrapper(
            customers.update,
        )
        self.list = to_streamed_response_wrapper(
            customers.list,
        )
        self.delete = to_streamed_response_wrapper(
            customers.delete,
        )
        self.get = to_streamed_response_wrapper(
            customers.get,
        )
        self.refresh_review = to_streamed_response_wrapper(
            customers.refresh_review,
        )
        self.unmasked = to_streamed_response_wrapper(
            customers.unmasked,
        )

    @cached_property
    def review(self) -> ReviewResourceWithStreamingResponse:
        return ReviewResourceWithStreamingResponse(self._customers.review)


class AsyncCustomersResourceWithStreamingResponse:
    def __init__(self, customers: AsyncCustomersResource) -> None:
        self._customers = customers

        self.create = async_to_streamed_response_wrapper(
            customers.create,
        )
        self.update = async_to_streamed_response_wrapper(
            customers.update,
        )
        self.list = async_to_streamed_response_wrapper(
            customers.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            customers.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            customers.get,
        )
        self.refresh_review = async_to_streamed_response_wrapper(
            customers.refresh_review,
        )
        self.unmasked = async_to_streamed_response_wrapper(
            customers.unmasked,
        )

    @cached_property
    def review(self) -> AsyncReviewResourceWithStreamingResponse:
        return AsyncReviewResourceWithStreamingResponse(self._customers.review)
