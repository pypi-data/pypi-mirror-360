# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from datetime import date
from typing_extensions import Literal

import httpx

from ..types import (
    charge_hold_params,
    charge_cancel_params,
    charge_create_params,
    charge_update_params,
    charge_release_params,
)
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
from .._base_client import make_request_options
from ..types.charge_v1 import ChargeV1
from ..types.charge_unmask_response import ChargeUnmaskResponse
from ..types.shared_params.device_info_v1 import DeviceInfoV1

__all__ = ["ChargesResource", "AsyncChargesResource"]


class ChargesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ChargesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return ChargesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ChargesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return ChargesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        amount: int,
        config: charge_create_params.Config,
        consent_type: Literal["internet", "signed"],
        currency: str,
        description: str,
        device: DeviceInfoV1,
        external_id: str,
        paykey: str,
        payment_date: Union[str, date],
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
    ) -> ChargeV1:
        """
        Use charges to collect money from a customer for the sale of goods or services.

        Args:
          amount: The amount of the charge in cents.

          consent_type: The channel or mechanism through which the payment was authorized. Use
              `internet` for payments made online or through a mobile app and `signed` for
              signed agreements where there is a consent form or contract. Use `signed` for
              PDF signatures.

          currency: The currency of the charge. Only USD is supported.

          description: An arbitrary description for the charge.

          external_id: Unique identifier for the charge in your database. This value must be unique
              across all charges.

          paykey: Value of the `paykey` used for the charge.

          payment_date: The desired date on which the payment should be occur. For charges, this means
              the date you want the customer to be debited on.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the charge in a structured format.

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
            "/v1/charges",
            body=maybe_transform(
                {
                    "amount": amount,
                    "config": config,
                    "consent_type": consent_type,
                    "currency": currency,
                    "description": description,
                    "device": device,
                    "external_id": external_id,
                    "paykey": paykey,
                    "payment_date": payment_date,
                    "metadata": metadata,
                },
                charge_create_params.ChargeCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChargeV1,
        )

    def update(
        self,
        id: str,
        *,
        amount: int,
        description: str,
        payment_date: Union[str, date],
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
    ) -> ChargeV1:
        """
        Change the values of parameters associated with a charge prior to processing.
        The status of the charge must be `created`, `scheduled`, or `on_hold`.

        Args:
          amount: The amount of the charge in cents.

          description: An arbitrary description for the charge.

          payment_date: The desired date on which the payment should be occur. For charges, this means
              the date you want the customer to be debited on.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the charge in a structured format.

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
            f"/v1/charges/{id}",
            body=maybe_transform(
                {
                    "amount": amount,
                    "description": description,
                    "payment_date": payment_date,
                    "metadata": metadata,
                },
                charge_update_params.ChargeUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChargeV1,
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
    ) -> ChargeV1:
        """Cancel a charge to prevent it from being originated for processing.

        The status
        of the charge must be `created`, `scheduled`, or `on_hold`.

        Args:
          reason: Details about why the charge status was updated.

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
            f"/v1/charges/{id}/cancel",
            body=maybe_transform({"reason": reason}, charge_cancel_params.ChargeCancelParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChargeV1,
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
    ) -> ChargeV1:
        """Retrieves the details of an existing charge.

        Supply the unique charge `id`, and
        Straddle will return the corresponding charge information.

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
            f"/v1/charges/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChargeV1,
        )

    def hold(
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
    ) -> ChargeV1:
        """Place a charge on hold to prevent it from being originated for processing.

        The
        status of the charge must be `created` or `scheduled`.

        Args:
          reason: Details about why the charge status was updated.

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
            f"/v1/charges/{id}/hold",
            body=maybe_transform({"reason": reason}, charge_hold_params.ChargeHoldParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChargeV1,
        )

    def release(
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
    ) -> ChargeV1:
        """
        Release a charge from an `on_hold` status to allow it to be rescheduled for
        processing.

        Args:
          reason: Details about why the charge status was updated.

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
            f"/v1/charges/{id}/release",
            body=maybe_transform({"reason": reason}, charge_release_params.ChargeReleaseParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChargeV1,
        )

    def unmask(
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
    ) -> ChargeUnmaskResponse:
        """
        Get a charge by id.

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
            f"/v1/charges/{id}/unmask",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChargeUnmaskResponse,
        )


class AsyncChargesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncChargesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return AsyncChargesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncChargesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return AsyncChargesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        amount: int,
        config: charge_create_params.Config,
        consent_type: Literal["internet", "signed"],
        currency: str,
        description: str,
        device: DeviceInfoV1,
        external_id: str,
        paykey: str,
        payment_date: Union[str, date],
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
    ) -> ChargeV1:
        """
        Use charges to collect money from a customer for the sale of goods or services.

        Args:
          amount: The amount of the charge in cents.

          consent_type: The channel or mechanism through which the payment was authorized. Use
              `internet` for payments made online or through a mobile app and `signed` for
              signed agreements where there is a consent form or contract. Use `signed` for
              PDF signatures.

          currency: The currency of the charge. Only USD is supported.

          description: An arbitrary description for the charge.

          external_id: Unique identifier for the charge in your database. This value must be unique
              across all charges.

          paykey: Value of the `paykey` used for the charge.

          payment_date: The desired date on which the payment should be occur. For charges, this means
              the date you want the customer to be debited on.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the charge in a structured format.

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
            "/v1/charges",
            body=await async_maybe_transform(
                {
                    "amount": amount,
                    "config": config,
                    "consent_type": consent_type,
                    "currency": currency,
                    "description": description,
                    "device": device,
                    "external_id": external_id,
                    "paykey": paykey,
                    "payment_date": payment_date,
                    "metadata": metadata,
                },
                charge_create_params.ChargeCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChargeV1,
        )

    async def update(
        self,
        id: str,
        *,
        amount: int,
        description: str,
        payment_date: Union[str, date],
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
    ) -> ChargeV1:
        """
        Change the values of parameters associated with a charge prior to processing.
        The status of the charge must be `created`, `scheduled`, or `on_hold`.

        Args:
          amount: The amount of the charge in cents.

          description: An arbitrary description for the charge.

          payment_date: The desired date on which the payment should be occur. For charges, this means
              the date you want the customer to be debited on.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the charge in a structured format.

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
            f"/v1/charges/{id}",
            body=await async_maybe_transform(
                {
                    "amount": amount,
                    "description": description,
                    "payment_date": payment_date,
                    "metadata": metadata,
                },
                charge_update_params.ChargeUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChargeV1,
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
    ) -> ChargeV1:
        """Cancel a charge to prevent it from being originated for processing.

        The status
        of the charge must be `created`, `scheduled`, or `on_hold`.

        Args:
          reason: Details about why the charge status was updated.

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
            f"/v1/charges/{id}/cancel",
            body=await async_maybe_transform({"reason": reason}, charge_cancel_params.ChargeCancelParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChargeV1,
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
    ) -> ChargeV1:
        """Retrieves the details of an existing charge.

        Supply the unique charge `id`, and
        Straddle will return the corresponding charge information.

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
            f"/v1/charges/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChargeV1,
        )

    async def hold(
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
    ) -> ChargeV1:
        """Place a charge on hold to prevent it from being originated for processing.

        The
        status of the charge must be `created` or `scheduled`.

        Args:
          reason: Details about why the charge status was updated.

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
            f"/v1/charges/{id}/hold",
            body=await async_maybe_transform({"reason": reason}, charge_hold_params.ChargeHoldParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChargeV1,
        )

    async def release(
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
    ) -> ChargeV1:
        """
        Release a charge from an `on_hold` status to allow it to be rescheduled for
        processing.

        Args:
          reason: Details about why the charge status was updated.

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
            f"/v1/charges/{id}/release",
            body=await async_maybe_transform({"reason": reason}, charge_release_params.ChargeReleaseParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChargeV1,
        )

    async def unmask(
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
    ) -> ChargeUnmaskResponse:
        """
        Get a charge by id.

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
            f"/v1/charges/{id}/unmask",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChargeUnmaskResponse,
        )


class ChargesResourceWithRawResponse:
    def __init__(self, charges: ChargesResource) -> None:
        self._charges = charges

        self.create = to_raw_response_wrapper(
            charges.create,
        )
        self.update = to_raw_response_wrapper(
            charges.update,
        )
        self.cancel = to_raw_response_wrapper(
            charges.cancel,
        )
        self.get = to_raw_response_wrapper(
            charges.get,
        )
        self.hold = to_raw_response_wrapper(
            charges.hold,
        )
        self.release = to_raw_response_wrapper(
            charges.release,
        )
        self.unmask = to_raw_response_wrapper(
            charges.unmask,
        )


class AsyncChargesResourceWithRawResponse:
    def __init__(self, charges: AsyncChargesResource) -> None:
        self._charges = charges

        self.create = async_to_raw_response_wrapper(
            charges.create,
        )
        self.update = async_to_raw_response_wrapper(
            charges.update,
        )
        self.cancel = async_to_raw_response_wrapper(
            charges.cancel,
        )
        self.get = async_to_raw_response_wrapper(
            charges.get,
        )
        self.hold = async_to_raw_response_wrapper(
            charges.hold,
        )
        self.release = async_to_raw_response_wrapper(
            charges.release,
        )
        self.unmask = async_to_raw_response_wrapper(
            charges.unmask,
        )


class ChargesResourceWithStreamingResponse:
    def __init__(self, charges: ChargesResource) -> None:
        self._charges = charges

        self.create = to_streamed_response_wrapper(
            charges.create,
        )
        self.update = to_streamed_response_wrapper(
            charges.update,
        )
        self.cancel = to_streamed_response_wrapper(
            charges.cancel,
        )
        self.get = to_streamed_response_wrapper(
            charges.get,
        )
        self.hold = to_streamed_response_wrapper(
            charges.hold,
        )
        self.release = to_streamed_response_wrapper(
            charges.release,
        )
        self.unmask = to_streamed_response_wrapper(
            charges.unmask,
        )


class AsyncChargesResourceWithStreamingResponse:
    def __init__(self, charges: AsyncChargesResource) -> None:
        self._charges = charges

        self.create = async_to_streamed_response_wrapper(
            charges.create,
        )
        self.update = async_to_streamed_response_wrapper(
            charges.update,
        )
        self.cancel = async_to_streamed_response_wrapper(
            charges.cancel,
        )
        self.get = async_to_streamed_response_wrapper(
            charges.get,
        )
        self.hold = async_to_streamed_response_wrapper(
            charges.hold,
        )
        self.release = async_to_streamed_response_wrapper(
            charges.release,
        )
        self.unmask = async_to_streamed_response_wrapper(
            charges.unmask,
        )
