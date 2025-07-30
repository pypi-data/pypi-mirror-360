# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import date
from typing_extensions import Literal

import httpx

from ..types import funding_event_list_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, strip_not_given
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
from ..types.funding_event_summary_item_v1 import FundingEventSummaryItemV1
from ..types.funding_event_summary_paged_v1 import Data

__all__ = ["FundingEventsResource", "AsyncFundingEventsResource"]


class FundingEventsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FundingEventsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return FundingEventsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FundingEventsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return FundingEventsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        created_from: Union[str, date, None] | NotGiven = NOT_GIVEN,
        created_to: Union[str, date, None] | NotGiven = NOT_GIVEN,
        direction: Literal["deposit", "withdrawal"] | NotGiven = NOT_GIVEN,
        event_type: Literal["charge_deposit", "charge_reversal", "payout_return", "payout_withdrawal"]
        | NotGiven = NOT_GIVEN,
        page_number: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort_by: Literal["transfer_date", "id", "amount"] | NotGiven = NOT_GIVEN,
        sort_order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        trace_number: Optional[str] | NotGiven = NOT_GIVEN,
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
        """Retrieves a list of funding events for your account.

        This endpoint supports
        advanced sorting and filtering options.

        Args:
          created_from: The start date of the range to filter by using the `YYYY-MM-DD` format.

          created_to: The end date of the range to filter by using the `YYYY-MM-DD` format.

          direction: Describes the direction of the funding event from the perspective of the
              `linked_bank_account`.

          event_type: The funding event types describes the direction and reason for the funding
              event.

          page_number: Results page number. Starts at page 1.

          page_size: Results page size. Max value: 1000

          sort_by: The field to sort the results by.

          sort_order: The order in which to sort the results.

          trace_number: Trace number.

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
            "/v1/funding_events",
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
                        "direction": direction,
                        "event_type": event_type,
                        "page_number": page_number,
                        "page_size": page_size,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "trace_number": trace_number,
                    },
                    funding_event_list_params.FundingEventListParams,
                ),
            ),
            model=Data,
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
    ) -> FundingEventSummaryItemV1:
        """Retrieves the details of an existing funding event.

        Supply the unique funding
        event `id`, and Straddle will return the individual transaction items that make
        up the funding event.

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
            f"/v1/funding_events/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FundingEventSummaryItemV1,
        )


class AsyncFundingEventsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFundingEventsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFundingEventsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFundingEventsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return AsyncFundingEventsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        created_from: Union[str, date, None] | NotGiven = NOT_GIVEN,
        created_to: Union[str, date, None] | NotGiven = NOT_GIVEN,
        direction: Literal["deposit", "withdrawal"] | NotGiven = NOT_GIVEN,
        event_type: Literal["charge_deposit", "charge_reversal", "payout_return", "payout_withdrawal"]
        | NotGiven = NOT_GIVEN,
        page_number: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort_by: Literal["transfer_date", "id", "amount"] | NotGiven = NOT_GIVEN,
        sort_order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        trace_number: Optional[str] | NotGiven = NOT_GIVEN,
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
        """Retrieves a list of funding events for your account.

        This endpoint supports
        advanced sorting and filtering options.

        Args:
          created_from: The start date of the range to filter by using the `YYYY-MM-DD` format.

          created_to: The end date of the range to filter by using the `YYYY-MM-DD` format.

          direction: Describes the direction of the funding event from the perspective of the
              `linked_bank_account`.

          event_type: The funding event types describes the direction and reason for the funding
              event.

          page_number: Results page number. Starts at page 1.

          page_size: Results page size. Max value: 1000

          sort_by: The field to sort the results by.

          sort_order: The order in which to sort the results.

          trace_number: Trace number.

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
            "/v1/funding_events",
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
                        "direction": direction,
                        "event_type": event_type,
                        "page_number": page_number,
                        "page_size": page_size,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "trace_number": trace_number,
                    },
                    funding_event_list_params.FundingEventListParams,
                ),
            ),
            model=Data,
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
    ) -> FundingEventSummaryItemV1:
        """Retrieves the details of an existing funding event.

        Supply the unique funding
        event `id`, and Straddle will return the individual transaction items that make
        up the funding event.

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
            f"/v1/funding_events/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FundingEventSummaryItemV1,
        )


class FundingEventsResourceWithRawResponse:
    def __init__(self, funding_events: FundingEventsResource) -> None:
        self._funding_events = funding_events

        self.list = to_raw_response_wrapper(
            funding_events.list,
        )
        self.get = to_raw_response_wrapper(
            funding_events.get,
        )


class AsyncFundingEventsResourceWithRawResponse:
    def __init__(self, funding_events: AsyncFundingEventsResource) -> None:
        self._funding_events = funding_events

        self.list = async_to_raw_response_wrapper(
            funding_events.list,
        )
        self.get = async_to_raw_response_wrapper(
            funding_events.get,
        )


class FundingEventsResourceWithStreamingResponse:
    def __init__(self, funding_events: FundingEventsResource) -> None:
        self._funding_events = funding_events

        self.list = to_streamed_response_wrapper(
            funding_events.list,
        )
        self.get = to_streamed_response_wrapper(
            funding_events.get,
        )


class AsyncFundingEventsResourceWithStreamingResponse:
    def __init__(self, funding_events: AsyncFundingEventsResource) -> None:
        self._funding_events = funding_events

        self.list = async_to_streamed_response_wrapper(
            funding_events.list,
        )
        self.get = async_to_streamed_response_wrapper(
            funding_events.get,
        )
