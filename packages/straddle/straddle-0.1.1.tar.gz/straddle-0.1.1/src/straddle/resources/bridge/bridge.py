# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .link import (
    LinkResource,
    AsyncLinkResource,
    LinkResourceWithRawResponse,
    AsyncLinkResourceWithRawResponse,
    LinkResourceWithStreamingResponse,
    AsyncLinkResourceWithStreamingResponse,
)
from ...types import bridge_initialize_params
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
from ...types.bridge_token_v1 import BridgeTokenV1

__all__ = ["BridgeResource", "AsyncBridgeResource"]


class BridgeResource(SyncAPIResource):
    @cached_property
    def link(self) -> LinkResource:
        return LinkResource(self._client)

    @cached_property
    def with_raw_response(self) -> BridgeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return BridgeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BridgeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return BridgeResourceWithStreamingResponse(self)

    def initialize(
        self,
        *,
        customer_id: str,
        config: bridge_initialize_params.Config | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BridgeTokenV1:
        """
        Use this endpoint to generate a session token for use in the Bridge widget.

        Args:
          customer_id: The Straddle generated unique identifier of the `customer` to create a bridge
              token for.

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
            "/v1/bridge/initialize",
            body=maybe_transform(
                {
                    "customer_id": customer_id,
                    "config": config,
                },
                bridge_initialize_params.BridgeInitializeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BridgeTokenV1,
        )


class AsyncBridgeResource(AsyncAPIResource):
    @cached_property
    def link(self) -> AsyncLinkResource:
        return AsyncLinkResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncBridgeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return AsyncBridgeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBridgeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return AsyncBridgeResourceWithStreamingResponse(self)

    async def initialize(
        self,
        *,
        customer_id: str,
        config: bridge_initialize_params.Config | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BridgeTokenV1:
        """
        Use this endpoint to generate a session token for use in the Bridge widget.

        Args:
          customer_id: The Straddle generated unique identifier of the `customer` to create a bridge
              token for.

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
            "/v1/bridge/initialize",
            body=await async_maybe_transform(
                {
                    "customer_id": customer_id,
                    "config": config,
                },
                bridge_initialize_params.BridgeInitializeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BridgeTokenV1,
        )


class BridgeResourceWithRawResponse:
    def __init__(self, bridge: BridgeResource) -> None:
        self._bridge = bridge

        self.initialize = to_raw_response_wrapper(
            bridge.initialize,
        )

    @cached_property
    def link(self) -> LinkResourceWithRawResponse:
        return LinkResourceWithRawResponse(self._bridge.link)


class AsyncBridgeResourceWithRawResponse:
    def __init__(self, bridge: AsyncBridgeResource) -> None:
        self._bridge = bridge

        self.initialize = async_to_raw_response_wrapper(
            bridge.initialize,
        )

    @cached_property
    def link(self) -> AsyncLinkResourceWithRawResponse:
        return AsyncLinkResourceWithRawResponse(self._bridge.link)


class BridgeResourceWithStreamingResponse:
    def __init__(self, bridge: BridgeResource) -> None:
        self._bridge = bridge

        self.initialize = to_streamed_response_wrapper(
            bridge.initialize,
        )

    @cached_property
    def link(self) -> LinkResourceWithStreamingResponse:
        return LinkResourceWithStreamingResponse(self._bridge.link)


class AsyncBridgeResourceWithStreamingResponse:
    def __init__(self, bridge: AsyncBridgeResource) -> None:
        self._bridge = bridge

        self.initialize = async_to_streamed_response_wrapper(
            bridge.initialize,
        )

    @cached_property
    def link(self) -> AsyncLinkResourceWithStreamingResponse:
        return AsyncLinkResourceWithStreamingResponse(self._bridge.link)
