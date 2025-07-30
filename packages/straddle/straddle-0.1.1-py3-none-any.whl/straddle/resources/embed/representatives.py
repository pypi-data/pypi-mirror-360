# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import date
from typing_extensions import Literal

import httpx

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
from ...types.embed import representative_list_params, representative_create_params, representative_update_params
from ..._base_client import AsyncPaginator, make_request_options
from ...types.embed.representative import Representative
from ...types.embed.representative_paged import Data

__all__ = ["RepresentativesResource", "AsyncRepresentativesResource"]


class RepresentativesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RepresentativesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return RepresentativesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RepresentativesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return RepresentativesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        account_id: str,
        dob: Union[str, date],
        email: str,
        first_name: str,
        last_name: str,
        mobile_number: str,
        relationship: representative_create_params.Relationship,
        ssn_last4: str,
        external_id: Optional[str] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Representative:
        """Creates a new representative associated with an account.

        Representatives are
        individuals who have legal authority or significant responsibility within the
        business.

        Args:
          account_id: The unique identifier of the account this representative is associated with.

          dob: Date of birth for the representative in ISO 8601 format (YYYY-MM-DD).

          email: The company email address of the representative.

          first_name: The first name of the representative.

          last_name: The last name of the representative.

          mobile_number: The mobile phone number of the representative.

          ssn_last4: The last 4 digits of the representative's Social Security Number.

          external_id: Unique identifier for the representative in your database, used for
              cross-referencing between Straddle and your systems.

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
            "/v1/representatives",
            body=maybe_transform(
                {
                    "account_id": account_id,
                    "dob": dob,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "mobile_number": mobile_number,
                    "relationship": relationship,
                    "ssn_last4": ssn_last4,
                    "external_id": external_id,
                },
                representative_create_params.RepresentativeCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Representative,
        )

    def update(
        self,
        representative_id: str,
        *,
        dob: Union[str, date],
        email: str,
        first_name: str,
        last_name: str,
        mobile_number: str,
        relationship: representative_update_params.Relationship,
        ssn_last4: str,
        external_id: Optional[str] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Representative:
        """Updates an existing representative's information.

        This can be used to update
        personal details, contact information, or the relationship to the account or
        organization.

        Args:
          dob: The date of birth of the representative, in ISO 8601 format (YYYY-MM-DD).

          email: The email address of the representative.

          first_name: The first name of the representative.

          last_name: The last name of the representative.

          mobile_number: The mobile phone number of the representative.

          ssn_last4: The last 4 digits of the representative's Social Security Number.

          external_id: Unique identifier for the representative in your database, used for
              cross-referencing between Straddle and your systems.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not representative_id:
            raise ValueError(f"Expected a non-empty value for `representative_id` but received {representative_id!r}")
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
            f"/v1/representatives/{representative_id}",
            body=maybe_transform(
                {
                    "dob": dob,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "mobile_number": mobile_number,
                    "relationship": relationship,
                    "ssn_last4": ssn_last4,
                    "external_id": external_id,
                },
                representative_update_params.RepresentativeUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Representative,
        )

    def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        level: Literal["account", "platform"] | NotGiven = NOT_GIVEN,
        organization_id: str | NotGiven = NOT_GIVEN,
        page_number: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        platform_id: str | NotGiven = NOT_GIVEN,
        sort_by: str | NotGiven = NOT_GIVEN,
        sort_order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
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
        Returns a list of representatives associated with a specific account or
        organization. The representatives are returned sorted by creation date, with the
        most recently created representatives appearing first. This endpoint supports
        advanced sorting and filtering options.

        Args:
          account_id: The unique identifier of the account to list representatives for.

          page_number: Results page number. Starts at page 1.

          page_size: Page size. Max value: 1000

          sort_by: Sort By.

          sort_order: Sort Order.

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
            "/v1/representatives",
            page=SyncPageNumberSchema[Data],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "account_id": account_id,
                        "level": level,
                        "organization_id": organization_id,
                        "page_number": page_number,
                        "page_size": page_size,
                        "platform_id": platform_id,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                    },
                    representative_list_params.RepresentativeListParams,
                ),
            ),
            model=Data,
        )

    def get(
        self,
        representative_id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Representative:
        """Retrieves the details of an existing representative.

        Supply the unique
        representative ID, and Straddle will return the corresponding representative
        information.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not representative_id:
            raise ValueError(f"Expected a non-empty value for `representative_id` but received {representative_id!r}")
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
            f"/v1/representatives/{representative_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Representative,
        )

    def unmask(
        self,
        representative_id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Representative:
        """
        Retrieves the unmasked details of a representative that has previously been
        created. Supply the unique representative ID, and Straddle will return the
        corresponding representative information, including sensitive details. This
        endpoint requires additional authentication and should be used with caution.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not representative_id:
            raise ValueError(f"Expected a non-empty value for `representative_id` but received {representative_id!r}")
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
            f"/v1/representatives/{representative_id}/unmask",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Representative,
        )


class AsyncRepresentativesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRepresentativesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRepresentativesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRepresentativesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return AsyncRepresentativesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        account_id: str,
        dob: Union[str, date],
        email: str,
        first_name: str,
        last_name: str,
        mobile_number: str,
        relationship: representative_create_params.Relationship,
        ssn_last4: str,
        external_id: Optional[str] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Representative:
        """Creates a new representative associated with an account.

        Representatives are
        individuals who have legal authority or significant responsibility within the
        business.

        Args:
          account_id: The unique identifier of the account this representative is associated with.

          dob: Date of birth for the representative in ISO 8601 format (YYYY-MM-DD).

          email: The company email address of the representative.

          first_name: The first name of the representative.

          last_name: The last name of the representative.

          mobile_number: The mobile phone number of the representative.

          ssn_last4: The last 4 digits of the representative's Social Security Number.

          external_id: Unique identifier for the representative in your database, used for
              cross-referencing between Straddle and your systems.

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
            "/v1/representatives",
            body=await async_maybe_transform(
                {
                    "account_id": account_id,
                    "dob": dob,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "mobile_number": mobile_number,
                    "relationship": relationship,
                    "ssn_last4": ssn_last4,
                    "external_id": external_id,
                },
                representative_create_params.RepresentativeCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Representative,
        )

    async def update(
        self,
        representative_id: str,
        *,
        dob: Union[str, date],
        email: str,
        first_name: str,
        last_name: str,
        mobile_number: str,
        relationship: representative_update_params.Relationship,
        ssn_last4: str,
        external_id: Optional[str] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Representative:
        """Updates an existing representative's information.

        This can be used to update
        personal details, contact information, or the relationship to the account or
        organization.

        Args:
          dob: The date of birth of the representative, in ISO 8601 format (YYYY-MM-DD).

          email: The email address of the representative.

          first_name: The first name of the representative.

          last_name: The last name of the representative.

          mobile_number: The mobile phone number of the representative.

          ssn_last4: The last 4 digits of the representative's Social Security Number.

          external_id: Unique identifier for the representative in your database, used for
              cross-referencing between Straddle and your systems.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not representative_id:
            raise ValueError(f"Expected a non-empty value for `representative_id` but received {representative_id!r}")
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
            f"/v1/representatives/{representative_id}",
            body=await async_maybe_transform(
                {
                    "dob": dob,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "mobile_number": mobile_number,
                    "relationship": relationship,
                    "ssn_last4": ssn_last4,
                    "external_id": external_id,
                },
                representative_update_params.RepresentativeUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Representative,
        )

    def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        level: Literal["account", "platform"] | NotGiven = NOT_GIVEN,
        organization_id: str | NotGiven = NOT_GIVEN,
        page_number: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        platform_id: str | NotGiven = NOT_GIVEN,
        sort_by: str | NotGiven = NOT_GIVEN,
        sort_order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
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
        Returns a list of representatives associated with a specific account or
        organization. The representatives are returned sorted by creation date, with the
        most recently created representatives appearing first. This endpoint supports
        advanced sorting and filtering options.

        Args:
          account_id: The unique identifier of the account to list representatives for.

          page_number: Results page number. Starts at page 1.

          page_size: Page size. Max value: 1000

          sort_by: Sort By.

          sort_order: Sort Order.

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
            "/v1/representatives",
            page=AsyncPageNumberSchema[Data],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "account_id": account_id,
                        "level": level,
                        "organization_id": organization_id,
                        "page_number": page_number,
                        "page_size": page_size,
                        "platform_id": platform_id,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                    },
                    representative_list_params.RepresentativeListParams,
                ),
            ),
            model=Data,
        )

    async def get(
        self,
        representative_id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Representative:
        """Retrieves the details of an existing representative.

        Supply the unique
        representative ID, and Straddle will return the corresponding representative
        information.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not representative_id:
            raise ValueError(f"Expected a non-empty value for `representative_id` but received {representative_id!r}")
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
            f"/v1/representatives/{representative_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Representative,
        )

    async def unmask(
        self,
        representative_id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Representative:
        """
        Retrieves the unmasked details of a representative that has previously been
        created. Supply the unique representative ID, and Straddle will return the
        corresponding representative information, including sensitive details. This
        endpoint requires additional authentication and should be used with caution.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not representative_id:
            raise ValueError(f"Expected a non-empty value for `representative_id` but received {representative_id!r}")
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
            f"/v1/representatives/{representative_id}/unmask",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Representative,
        )


class RepresentativesResourceWithRawResponse:
    def __init__(self, representatives: RepresentativesResource) -> None:
        self._representatives = representatives

        self.create = to_raw_response_wrapper(
            representatives.create,
        )
        self.update = to_raw_response_wrapper(
            representatives.update,
        )
        self.list = to_raw_response_wrapper(
            representatives.list,
        )
        self.get = to_raw_response_wrapper(
            representatives.get,
        )
        self.unmask = to_raw_response_wrapper(
            representatives.unmask,
        )


class AsyncRepresentativesResourceWithRawResponse:
    def __init__(self, representatives: AsyncRepresentativesResource) -> None:
        self._representatives = representatives

        self.create = async_to_raw_response_wrapper(
            representatives.create,
        )
        self.update = async_to_raw_response_wrapper(
            representatives.update,
        )
        self.list = async_to_raw_response_wrapper(
            representatives.list,
        )
        self.get = async_to_raw_response_wrapper(
            representatives.get,
        )
        self.unmask = async_to_raw_response_wrapper(
            representatives.unmask,
        )


class RepresentativesResourceWithStreamingResponse:
    def __init__(self, representatives: RepresentativesResource) -> None:
        self._representatives = representatives

        self.create = to_streamed_response_wrapper(
            representatives.create,
        )
        self.update = to_streamed_response_wrapper(
            representatives.update,
        )
        self.list = to_streamed_response_wrapper(
            representatives.list,
        )
        self.get = to_streamed_response_wrapper(
            representatives.get,
        )
        self.unmask = to_streamed_response_wrapper(
            representatives.unmask,
        )


class AsyncRepresentativesResourceWithStreamingResponse:
    def __init__(self, representatives: AsyncRepresentativesResource) -> None:
        self._representatives = representatives

        self.create = async_to_streamed_response_wrapper(
            representatives.create,
        )
        self.update = async_to_streamed_response_wrapper(
            representatives.update,
        )
        self.list = async_to_streamed_response_wrapper(
            representatives.list,
        )
        self.get = async_to_streamed_response_wrapper(
            representatives.get,
        )
        self.unmask = async_to_streamed_response_wrapper(
            representatives.unmask,
        )
