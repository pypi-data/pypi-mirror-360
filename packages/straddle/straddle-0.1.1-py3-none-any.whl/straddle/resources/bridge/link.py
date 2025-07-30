# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
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
from ..._base_client import make_request_options
from ...types.bridge import (
    link_plaid_params,
    link_create_tan_params,
    link_bank_account_params,
    link_create_paykey_params,
)
from ...types.paykey_v1 import PaykeyV1
from ...types.bridge.link_create_tan_response import LinkCreateTanResponse
from ...types.bridge.link_create_paykey_response import LinkCreatePaykeyResponse

__all__ = ["LinkResource", "AsyncLinkResource"]


class LinkResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> LinkResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return LinkResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LinkResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return LinkResourceWithStreamingResponse(self)

    def bank_account(
        self,
        *,
        account_number: str,
        account_type: Literal["checking", "savings"],
        customer_id: str,
        routing_number: str,
        config: link_bank_account_params.Config | NotGiven = NOT_GIVEN,
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
    ) -> PaykeyV1:
        """
        Use Bridge to create a new paykey using a bank routing and account number as the
        source. This endpoint allows you to create a secure payment token linked to a
        specific bank account.

        Args:
          account_number: The bank account number.

          customer_id: Unique identifier of the related customer object.

          routing_number: The routing number of the bank account.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the paykey in a structured format.

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
            "/v1/bridge/bank_account",
            body=maybe_transform(
                {
                    "account_number": account_number,
                    "account_type": account_type,
                    "customer_id": customer_id,
                    "routing_number": routing_number,
                    "config": config,
                    "metadata": metadata,
                },
                link_bank_account_params.LinkBankAccountParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PaykeyV1,
        )

    def create_paykey(
        self,
        *,
        customer_id: str,
        quiltt_token: str,
        config: link_create_paykey_params.Config | NotGiven = NOT_GIVEN,
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
    ) -> LinkCreatePaykeyResponse:
        """Creates a new paykey using a Quiltt token as the source.

        This endpoint allows
        you to create a secure payment token linked to a bank account authenticated
        through Quiltt.

        Args:
          customer_id: Unique identifier of the related customer object.

          quiltt_token: Quiltt processor token generated by your application for use with the Straddle
              API.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the paykey in a structured format.

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
            "/v1/bridge/quiltt",
            body=maybe_transform(
                {
                    "customer_id": customer_id,
                    "quiltt_token": quiltt_token,
                    "config": config,
                    "metadata": metadata,
                },
                link_create_paykey_params.LinkCreatePaykeyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LinkCreatePaykeyResponse,
        )

    def create_tan(
        self,
        *,
        account_type: Literal["checking", "savings"],
        customer_id: str,
        routing_number: str,
        tan: str,
        config: link_create_tan_params.Config | NotGiven = NOT_GIVEN,
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
    ) -> LinkCreateTanResponse:
        """
        Args:
          customer_id: Unique identifier of the related customer object.

          routing_number: Bank routing number.

          tan: Tokenized account number.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the paykey in a structured format.

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
            "/v1/bridge/tan",
            body=maybe_transform(
                {
                    "account_type": account_type,
                    "customer_id": customer_id,
                    "routing_number": routing_number,
                    "tan": tan,
                    "config": config,
                    "metadata": metadata,
                },
                link_create_tan_params.LinkCreateTanParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LinkCreateTanResponse,
        )

    def plaid(
        self,
        *,
        customer_id: str,
        plaid_token: str,
        config: link_plaid_params.Config | NotGiven = NOT_GIVEN,
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
    ) -> PaykeyV1:
        """Use Bridge to create a new paykey using a Plaid token as the source.

        This
        endpoint allows you to create a secure payment token linked to a bank account
        authenticated through Plaid.

        Args:
          customer_id: Unique identifier of the related customer object.

          plaid_token: Plaid processor token generated by your application for use with the Straddle
              API.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the paykey in a structured format.

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
            "/v1/bridge/plaid",
            body=maybe_transform(
                {
                    "customer_id": customer_id,
                    "plaid_token": plaid_token,
                    "config": config,
                    "metadata": metadata,
                },
                link_plaid_params.LinkPlaidParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PaykeyV1,
        )


class AsyncLinkResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncLinkResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return AsyncLinkResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLinkResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return AsyncLinkResourceWithStreamingResponse(self)

    async def bank_account(
        self,
        *,
        account_number: str,
        account_type: Literal["checking", "savings"],
        customer_id: str,
        routing_number: str,
        config: link_bank_account_params.Config | NotGiven = NOT_GIVEN,
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
    ) -> PaykeyV1:
        """
        Use Bridge to create a new paykey using a bank routing and account number as the
        source. This endpoint allows you to create a secure payment token linked to a
        specific bank account.

        Args:
          account_number: The bank account number.

          customer_id: Unique identifier of the related customer object.

          routing_number: The routing number of the bank account.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the paykey in a structured format.

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
            "/v1/bridge/bank_account",
            body=await async_maybe_transform(
                {
                    "account_number": account_number,
                    "account_type": account_type,
                    "customer_id": customer_id,
                    "routing_number": routing_number,
                    "config": config,
                    "metadata": metadata,
                },
                link_bank_account_params.LinkBankAccountParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PaykeyV1,
        )

    async def create_paykey(
        self,
        *,
        customer_id: str,
        quiltt_token: str,
        config: link_create_paykey_params.Config | NotGiven = NOT_GIVEN,
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
    ) -> LinkCreatePaykeyResponse:
        """Creates a new paykey using a Quiltt token as the source.

        This endpoint allows
        you to create a secure payment token linked to a bank account authenticated
        through Quiltt.

        Args:
          customer_id: Unique identifier of the related customer object.

          quiltt_token: Quiltt processor token generated by your application for use with the Straddle
              API.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the paykey in a structured format.

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
            "/v1/bridge/quiltt",
            body=await async_maybe_transform(
                {
                    "customer_id": customer_id,
                    "quiltt_token": quiltt_token,
                    "config": config,
                    "metadata": metadata,
                },
                link_create_paykey_params.LinkCreatePaykeyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LinkCreatePaykeyResponse,
        )

    async def create_tan(
        self,
        *,
        account_type: Literal["checking", "savings"],
        customer_id: str,
        routing_number: str,
        tan: str,
        config: link_create_tan_params.Config | NotGiven = NOT_GIVEN,
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
    ) -> LinkCreateTanResponse:
        """
        Args:
          customer_id: Unique identifier of the related customer object.

          routing_number: Bank routing number.

          tan: Tokenized account number.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the paykey in a structured format.

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
            "/v1/bridge/tan",
            body=await async_maybe_transform(
                {
                    "account_type": account_type,
                    "customer_id": customer_id,
                    "routing_number": routing_number,
                    "tan": tan,
                    "config": config,
                    "metadata": metadata,
                },
                link_create_tan_params.LinkCreateTanParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LinkCreateTanResponse,
        )

    async def plaid(
        self,
        *,
        customer_id: str,
        plaid_token: str,
        config: link_plaid_params.Config | NotGiven = NOT_GIVEN,
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
    ) -> PaykeyV1:
        """Use Bridge to create a new paykey using a Plaid token as the source.

        This
        endpoint allows you to create a secure payment token linked to a bank account
        authenticated through Plaid.

        Args:
          customer_id: Unique identifier of the related customer object.

          plaid_token: Plaid processor token generated by your application for use with the Straddle
              API.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the paykey in a structured format.

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
            "/v1/bridge/plaid",
            body=await async_maybe_transform(
                {
                    "customer_id": customer_id,
                    "plaid_token": plaid_token,
                    "config": config,
                    "metadata": metadata,
                },
                link_plaid_params.LinkPlaidParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PaykeyV1,
        )


class LinkResourceWithRawResponse:
    def __init__(self, link: LinkResource) -> None:
        self._link = link

        self.bank_account = to_raw_response_wrapper(
            link.bank_account,
        )
        self.create_paykey = to_raw_response_wrapper(
            link.create_paykey,
        )
        self.create_tan = to_raw_response_wrapper(
            link.create_tan,
        )
        self.plaid = to_raw_response_wrapper(
            link.plaid,
        )


class AsyncLinkResourceWithRawResponse:
    def __init__(self, link: AsyncLinkResource) -> None:
        self._link = link

        self.bank_account = async_to_raw_response_wrapper(
            link.bank_account,
        )
        self.create_paykey = async_to_raw_response_wrapper(
            link.create_paykey,
        )
        self.create_tan = async_to_raw_response_wrapper(
            link.create_tan,
        )
        self.plaid = async_to_raw_response_wrapper(
            link.plaid,
        )


class LinkResourceWithStreamingResponse:
    def __init__(self, link: LinkResource) -> None:
        self._link = link

        self.bank_account = to_streamed_response_wrapper(
            link.bank_account,
        )
        self.create_paykey = to_streamed_response_wrapper(
            link.create_paykey,
        )
        self.create_tan = to_streamed_response_wrapper(
            link.create_tan,
        )
        self.plaid = to_streamed_response_wrapper(
            link.plaid,
        )


class AsyncLinkResourceWithStreamingResponse:
    def __init__(self, link: AsyncLinkResource) -> None:
        self._link = link

        self.bank_account = async_to_streamed_response_wrapper(
            link.bank_account,
        )
        self.create_paykey = async_to_streamed_response_wrapper(
            link.create_paykey,
        )
        self.create_tan = async_to_streamed_response_wrapper(
            link.create_tan,
        )
        self.plaid = async_to_streamed_response_wrapper(
            link.plaid,
        )
