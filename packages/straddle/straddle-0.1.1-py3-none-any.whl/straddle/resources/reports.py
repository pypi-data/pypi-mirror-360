# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import strip_not_given
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.report_create_total_customers_by_status_response import ReportCreateTotalCustomersByStatusResponse

__all__ = ["ReportsResource", "AsyncReportsResource"]


class ReportsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ReportsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return ReportsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ReportsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return ReportsResourceWithStreamingResponse(self)

    def create_total_customers_by_status(
        self,
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
    ) -> ReportCreateTotalCustomersByStatusResponse:
        """
        Args:
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
            "/v1/reports/total_customers_by_status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ReportCreateTotalCustomersByStatusResponse,
        )


class AsyncReportsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncReportsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return AsyncReportsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncReportsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return AsyncReportsResourceWithStreamingResponse(self)

    async def create_total_customers_by_status(
        self,
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
    ) -> ReportCreateTotalCustomersByStatusResponse:
        """
        Args:
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
            "/v1/reports/total_customers_by_status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ReportCreateTotalCustomersByStatusResponse,
        )


class ReportsResourceWithRawResponse:
    def __init__(self, reports: ReportsResource) -> None:
        self._reports = reports

        self.create_total_customers_by_status = to_raw_response_wrapper(
            reports.create_total_customers_by_status,
        )


class AsyncReportsResourceWithRawResponse:
    def __init__(self, reports: AsyncReportsResource) -> None:
        self._reports = reports

        self.create_total_customers_by_status = async_to_raw_response_wrapper(
            reports.create_total_customers_by_status,
        )


class ReportsResourceWithStreamingResponse:
    def __init__(self, reports: ReportsResource) -> None:
        self._reports = reports

        self.create_total_customers_by_status = to_streamed_response_wrapper(
            reports.create_total_customers_by_status,
        )


class AsyncReportsResourceWithStreamingResponse:
    def __init__(self, reports: AsyncReportsResource) -> None:
        self._reports = reports

        self.create_total_customers_by_status = async_to_streamed_response_wrapper(
            reports.create_total_customers_by_status,
        )
