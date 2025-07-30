# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal

import httpx

from ..types import paykey_list_params, paykey_cancel_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, strip_not_given, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..pagination import SyncPageNumberSchema, AsyncPageNumberSchema
from .._base_client import AsyncPaginator, make_request_options
from ..types.paykey_v1 import PaykeyV1
from ..types.paykey_unmasked_v1 import PaykeyUnmaskedV1
from ..types.paykey_reveal_response import PaykeyRevealResponse
from ..types.paykey_summary_paged_v1 import Data

__all__ = ["PaykeysResource", "AsyncPaykeysResource"]


class PaykeysResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PaykeysResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return PaykeysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PaykeysResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return PaykeysResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        customer_id: str | NotGiven = NOT_GIVEN,
        page_number: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort_by: Literal["institution_name", "expires_at", "created_at"] | NotGiven = NOT_GIVEN,
        sort_order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        source: List[Literal["bank_account", "straddle", "mx", "plaid", "tan", "quiltt"]] | NotGiven = NOT_GIVEN,
        status: List[Literal["pending", "active", "inactive", "rejected", "review"]] | NotGiven = NOT_GIVEN,
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
        """Returns a list of paykeys associated with a Straddle account.

        This endpoint
        supports advanced sorting and filtering options.

        Args:
          customer_id: Filter paykeys by related customer ID.

          page_number: Page number for paginated results. Starts at 1.

          page_size: Number of results per page. Maximum: 1000.

          source: Filter paykeys by their source.

          status: Filter paykeys by their current status.

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
            "/v1/paykeys",
            page=SyncPageNumberSchema[Data],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "customer_id": customer_id,
                        "page_number": page_number,
                        "page_size": page_size,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "source": source,
                        "status": status,
                    },
                    paykey_list_params.PaykeyListParams,
                ),
            ),
            model=Data,
        )

    def cancel(
        self,
        id: str,
        *,
        reason: Optional[str] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PaykeyV1:
        """
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
            f"/v1/paykeys/{id}/cancel",
            body=maybe_transform({"reason": reason}, paykey_cancel_params.PaykeyCancelParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PaykeyV1,
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
    ) -> PaykeyV1:
        """Retrieves the details of an existing paykey.

        Supply the unique paykey `id` and
        Straddle will return the corresponding paykey record , including the `paykey`
        token value and masked bank account details.

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
            f"/v1/paykeys/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PaykeyV1,
        )

    def reveal(
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
    ) -> PaykeyRevealResponse:
        """
        Retrieves the details of a paykey that has previously been created, including
        unmasked bank account fields. Supply the unique paykey ID that was returned from
        your previous request, and Straddle will return the corresponding paykey
        information.

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
            f"/v1/paykeys/{id}/reveal",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PaykeyRevealResponse,
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
    ) -> PaykeyUnmaskedV1:
        """Retrieves the unmasked details of an existing paykey.

        Supply the unique paykey
        `id` and Straddle will return the corresponding paykey record, including the
        unmasked bank account details. This endpoint needs to be enabled by Straddle for
        your account and should only be used when absolutely necessary.

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
            f"/v1/paykeys/{id}/unmasked",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PaykeyUnmaskedV1,
        )


class AsyncPaykeysResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPaykeysResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPaykeysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPaykeysResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return AsyncPaykeysResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        customer_id: str | NotGiven = NOT_GIVEN,
        page_number: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort_by: Literal["institution_name", "expires_at", "created_at"] | NotGiven = NOT_GIVEN,
        sort_order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        source: List[Literal["bank_account", "straddle", "mx", "plaid", "tan", "quiltt"]] | NotGiven = NOT_GIVEN,
        status: List[Literal["pending", "active", "inactive", "rejected", "review"]] | NotGiven = NOT_GIVEN,
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
        """Returns a list of paykeys associated with a Straddle account.

        This endpoint
        supports advanced sorting and filtering options.

        Args:
          customer_id: Filter paykeys by related customer ID.

          page_number: Page number for paginated results. Starts at 1.

          page_size: Number of results per page. Maximum: 1000.

          source: Filter paykeys by their source.

          status: Filter paykeys by their current status.

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
            "/v1/paykeys",
            page=AsyncPageNumberSchema[Data],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "customer_id": customer_id,
                        "page_number": page_number,
                        "page_size": page_size,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "source": source,
                        "status": status,
                    },
                    paykey_list_params.PaykeyListParams,
                ),
            ),
            model=Data,
        )

    async def cancel(
        self,
        id: str,
        *,
        reason: Optional[str] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PaykeyV1:
        """
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
            f"/v1/paykeys/{id}/cancel",
            body=await async_maybe_transform({"reason": reason}, paykey_cancel_params.PaykeyCancelParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PaykeyV1,
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
    ) -> PaykeyV1:
        """Retrieves the details of an existing paykey.

        Supply the unique paykey `id` and
        Straddle will return the corresponding paykey record , including the `paykey`
        token value and masked bank account details.

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
            f"/v1/paykeys/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PaykeyV1,
        )

    async def reveal(
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
    ) -> PaykeyRevealResponse:
        """
        Retrieves the details of a paykey that has previously been created, including
        unmasked bank account fields. Supply the unique paykey ID that was returned from
        your previous request, and Straddle will return the corresponding paykey
        information.

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
            f"/v1/paykeys/{id}/reveal",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PaykeyRevealResponse,
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
    ) -> PaykeyUnmaskedV1:
        """Retrieves the unmasked details of an existing paykey.

        Supply the unique paykey
        `id` and Straddle will return the corresponding paykey record, including the
        unmasked bank account details. This endpoint needs to be enabled by Straddle for
        your account and should only be used when absolutely necessary.

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
            f"/v1/paykeys/{id}/unmasked",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PaykeyUnmaskedV1,
        )


class PaykeysResourceWithRawResponse:
    def __init__(self, paykeys: PaykeysResource) -> None:
        self._paykeys = paykeys

        self.list = to_raw_response_wrapper(
            paykeys.list,
        )
        self.cancel = to_raw_response_wrapper(
            paykeys.cancel,
        )
        self.get = to_raw_response_wrapper(
            paykeys.get,
        )
        self.reveal = to_raw_response_wrapper(
            paykeys.reveal,
        )
        self.unmasked = to_raw_response_wrapper(
            paykeys.unmasked,
        )


class AsyncPaykeysResourceWithRawResponse:
    def __init__(self, paykeys: AsyncPaykeysResource) -> None:
        self._paykeys = paykeys

        self.list = async_to_raw_response_wrapper(
            paykeys.list,
        )
        self.cancel = async_to_raw_response_wrapper(
            paykeys.cancel,
        )
        self.get = async_to_raw_response_wrapper(
            paykeys.get,
        )
        self.reveal = async_to_raw_response_wrapper(
            paykeys.reveal,
        )
        self.unmasked = async_to_raw_response_wrapper(
            paykeys.unmasked,
        )


class PaykeysResourceWithStreamingResponse:
    def __init__(self, paykeys: PaykeysResource) -> None:
        self._paykeys = paykeys

        self.list = to_streamed_response_wrapper(
            paykeys.list,
        )
        self.cancel = to_streamed_response_wrapper(
            paykeys.cancel,
        )
        self.get = to_streamed_response_wrapper(
            paykeys.get,
        )
        self.reveal = to_streamed_response_wrapper(
            paykeys.reveal,
        )
        self.unmasked = to_streamed_response_wrapper(
            paykeys.unmasked,
        )


class AsyncPaykeysResourceWithStreamingResponse:
    def __init__(self, paykeys: AsyncPaykeysResource) -> None:
        self._paykeys = paykeys

        self.list = async_to_streamed_response_wrapper(
            paykeys.list,
        )
        self.cancel = async_to_streamed_response_wrapper(
            paykeys.cancel,
        )
        self.get = async_to_streamed_response_wrapper(
            paykeys.get,
        )
        self.reveal = async_to_streamed_response_wrapper(
            paykeys.reveal,
        )
        self.unmasked = async_to_streamed_response_wrapper(
            paykeys.unmasked,
        )
