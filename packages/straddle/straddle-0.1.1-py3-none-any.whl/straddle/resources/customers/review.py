# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

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
from ...types.customers import review_decision_params
from ...types.customer_v1 import CustomerV1
from ...types.customers.customer_review_v1 import CustomerReviewV1

__all__ = ["ReviewResource", "AsyncReviewResource"]


class ReviewResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ReviewResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return ReviewResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ReviewResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return ReviewResourceWithStreamingResponse(self)

    def decision(
        self,
        id: str,
        *,
        status: Literal["verified", "rejected"],
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
        """Updates the status of a customer's identity decision.

        This endpoint allows you
        to modify the outcome of a customer risk screening and is useful for correcting
        or updating the status of a customer's verification. Note that this endpoint is
        only available for customers with a current status of `review`.

        Args:
          status: The final status of the customer review.

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
        return self._patch(
            f"/v1/customers/{id}/review",
            body=maybe_transform({"status": status}, review_decision_params.ReviewDecisionParams),
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
    ) -> CustomerReviewV1:
        """
        Retrieves and analyzes the results of a customer's identity validation and fraud
        score. This endpoint provides a comprehensive breakdown of the validation
        outcome, including:

        - Risk and correlation scores
        - Reason codes for the decision
        - Results of watchlist screening
        - Any network alerts detected Use this endpoint to gain insights into the
          verification process and make informed decisions about customer onboarding.

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
            f"/v1/customers/{id}/review",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomerReviewV1,
        )


class AsyncReviewResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncReviewResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return AsyncReviewResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncReviewResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return AsyncReviewResourceWithStreamingResponse(self)

    async def decision(
        self,
        id: str,
        *,
        status: Literal["verified", "rejected"],
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
        """Updates the status of a customer's identity decision.

        This endpoint allows you
        to modify the outcome of a customer risk screening and is useful for correcting
        or updating the status of a customer's verification. Note that this endpoint is
        only available for customers with a current status of `review`.

        Args:
          status: The final status of the customer review.

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
        return await self._patch(
            f"/v1/customers/{id}/review",
            body=await async_maybe_transform({"status": status}, review_decision_params.ReviewDecisionParams),
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
    ) -> CustomerReviewV1:
        """
        Retrieves and analyzes the results of a customer's identity validation and fraud
        score. This endpoint provides a comprehensive breakdown of the validation
        outcome, including:

        - Risk and correlation scores
        - Reason codes for the decision
        - Results of watchlist screening
        - Any network alerts detected Use this endpoint to gain insights into the
          verification process and make informed decisions about customer onboarding.

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
            f"/v1/customers/{id}/review",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomerReviewV1,
        )


class ReviewResourceWithRawResponse:
    def __init__(self, review: ReviewResource) -> None:
        self._review = review

        self.decision = to_raw_response_wrapper(
            review.decision,
        )
        self.get = to_raw_response_wrapper(
            review.get,
        )


class AsyncReviewResourceWithRawResponse:
    def __init__(self, review: AsyncReviewResource) -> None:
        self._review = review

        self.decision = async_to_raw_response_wrapper(
            review.decision,
        )
        self.get = async_to_raw_response_wrapper(
            review.get,
        )


class ReviewResourceWithStreamingResponse:
    def __init__(self, review: ReviewResource) -> None:
        self._review = review

        self.decision = to_streamed_response_wrapper(
            review.decision,
        )
        self.get = to_streamed_response_wrapper(
            review.get,
        )


class AsyncReviewResourceWithStreamingResponse:
    def __init__(self, review: AsyncReviewResource) -> None:
        self._review = review

        self.decision = async_to_streamed_response_wrapper(
            review.decision,
        )
        self.get = async_to_streamed_response_wrapper(
            review.get,
        )
