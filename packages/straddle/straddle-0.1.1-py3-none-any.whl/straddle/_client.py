# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Dict, Union, Mapping, cast
from typing_extensions import Self, Literal, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from .resources import charges, paykeys, payouts, reports, payments, funding_events
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import StraddleError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from .resources.embed import embed
from .resources.bridge import bridge
from .resources.customers import customers

__all__ = [
    "ENVIRONMENTS",
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Straddle",
    "AsyncStraddle",
    "Client",
    "AsyncClient",
]

ENVIRONMENTS: Dict[str, str] = {
    "sandbox": "https://sandbox.straddle.io",
    "production": "https://production.straddle.io",
}


class Straddle(SyncAPIClient):
    embed: embed.EmbedResource
    bridge: bridge.BridgeResource
    customers: customers.CustomersResource
    paykeys: paykeys.PaykeysResource
    charges: charges.ChargesResource
    funding_events: funding_events.FundingEventsResource
    payments: payments.PaymentsResource
    payouts: payouts.PayoutsResource
    reports: reports.ReportsResource
    with_raw_response: StraddleWithRawResponse
    with_streaming_response: StraddleWithStreamedResponse

    # client options
    api_key: str

    _environment: Literal["sandbox", "production"] | NotGiven

    def __init__(
        self,
        *,
        api_key: str | None = None,
        environment: Literal["sandbox", "production"] | NotGiven = NOT_GIVEN,
        base_url: str | httpx.URL | None | NotGiven = NOT_GIVEN,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Straddle client instance.

        This automatically infers the `api_key` argument from the `STRADDLE_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("STRADDLE_API_KEY")
        if api_key is None:
            raise StraddleError(
                "The api_key client option must be set either by passing api_key to the client or by setting the STRADDLE_API_KEY environment variable"
            )
        self.api_key = api_key

        self._environment = environment

        base_url_env = os.environ.get("STRADDLE_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `STRADDLE_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "sandbox"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.embed = embed.EmbedResource(self)
        self.bridge = bridge.BridgeResource(self)
        self.customers = customers.CustomersResource(self)
        self.paykeys = paykeys.PaykeysResource(self)
        self.charges = charges.ChargesResource(self)
        self.funding_events = funding_events.FundingEventsResource(self)
        self.payments = payments.PaymentsResource(self)
        self.payouts = payouts.PayoutsResource(self)
        self.reports = reports.ReportsResource(self)
        self.with_raw_response = StraddleWithRawResponse(self)
        self.with_streaming_response = StraddleWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        environment: Literal["sandbox", "production"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncStraddle(AsyncAPIClient):
    embed: embed.AsyncEmbedResource
    bridge: bridge.AsyncBridgeResource
    customers: customers.AsyncCustomersResource
    paykeys: paykeys.AsyncPaykeysResource
    charges: charges.AsyncChargesResource
    funding_events: funding_events.AsyncFundingEventsResource
    payments: payments.AsyncPaymentsResource
    payouts: payouts.AsyncPayoutsResource
    reports: reports.AsyncReportsResource
    with_raw_response: AsyncStraddleWithRawResponse
    with_streaming_response: AsyncStraddleWithStreamedResponse

    # client options
    api_key: str

    _environment: Literal["sandbox", "production"] | NotGiven

    def __init__(
        self,
        *,
        api_key: str | None = None,
        environment: Literal["sandbox", "production"] | NotGiven = NOT_GIVEN,
        base_url: str | httpx.URL | None | NotGiven = NOT_GIVEN,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncStraddle client instance.

        This automatically infers the `api_key` argument from the `STRADDLE_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("STRADDLE_API_KEY")
        if api_key is None:
            raise StraddleError(
                "The api_key client option must be set either by passing api_key to the client or by setting the STRADDLE_API_KEY environment variable"
            )
        self.api_key = api_key

        self._environment = environment

        base_url_env = os.environ.get("STRADDLE_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `STRADDLE_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "sandbox"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.embed = embed.AsyncEmbedResource(self)
        self.bridge = bridge.AsyncBridgeResource(self)
        self.customers = customers.AsyncCustomersResource(self)
        self.paykeys = paykeys.AsyncPaykeysResource(self)
        self.charges = charges.AsyncChargesResource(self)
        self.funding_events = funding_events.AsyncFundingEventsResource(self)
        self.payments = payments.AsyncPaymentsResource(self)
        self.payouts = payouts.AsyncPayoutsResource(self)
        self.reports = reports.AsyncReportsResource(self)
        self.with_raw_response = AsyncStraddleWithRawResponse(self)
        self.with_streaming_response = AsyncStraddleWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        environment: Literal["sandbox", "production"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class StraddleWithRawResponse:
    def __init__(self, client: Straddle) -> None:
        self.embed = embed.EmbedResourceWithRawResponse(client.embed)
        self.bridge = bridge.BridgeResourceWithRawResponse(client.bridge)
        self.customers = customers.CustomersResourceWithRawResponse(client.customers)
        self.paykeys = paykeys.PaykeysResourceWithRawResponse(client.paykeys)
        self.charges = charges.ChargesResourceWithRawResponse(client.charges)
        self.funding_events = funding_events.FundingEventsResourceWithRawResponse(client.funding_events)
        self.payments = payments.PaymentsResourceWithRawResponse(client.payments)
        self.payouts = payouts.PayoutsResourceWithRawResponse(client.payouts)
        self.reports = reports.ReportsResourceWithRawResponse(client.reports)


class AsyncStraddleWithRawResponse:
    def __init__(self, client: AsyncStraddle) -> None:
        self.embed = embed.AsyncEmbedResourceWithRawResponse(client.embed)
        self.bridge = bridge.AsyncBridgeResourceWithRawResponse(client.bridge)
        self.customers = customers.AsyncCustomersResourceWithRawResponse(client.customers)
        self.paykeys = paykeys.AsyncPaykeysResourceWithRawResponse(client.paykeys)
        self.charges = charges.AsyncChargesResourceWithRawResponse(client.charges)
        self.funding_events = funding_events.AsyncFundingEventsResourceWithRawResponse(client.funding_events)
        self.payments = payments.AsyncPaymentsResourceWithRawResponse(client.payments)
        self.payouts = payouts.AsyncPayoutsResourceWithRawResponse(client.payouts)
        self.reports = reports.AsyncReportsResourceWithRawResponse(client.reports)


class StraddleWithStreamedResponse:
    def __init__(self, client: Straddle) -> None:
        self.embed = embed.EmbedResourceWithStreamingResponse(client.embed)
        self.bridge = bridge.BridgeResourceWithStreamingResponse(client.bridge)
        self.customers = customers.CustomersResourceWithStreamingResponse(client.customers)
        self.paykeys = paykeys.PaykeysResourceWithStreamingResponse(client.paykeys)
        self.charges = charges.ChargesResourceWithStreamingResponse(client.charges)
        self.funding_events = funding_events.FundingEventsResourceWithStreamingResponse(client.funding_events)
        self.payments = payments.PaymentsResourceWithStreamingResponse(client.payments)
        self.payouts = payouts.PayoutsResourceWithStreamingResponse(client.payouts)
        self.reports = reports.ReportsResourceWithStreamingResponse(client.reports)


class AsyncStraddleWithStreamedResponse:
    def __init__(self, client: AsyncStraddle) -> None:
        self.embed = embed.AsyncEmbedResourceWithStreamingResponse(client.embed)
        self.bridge = bridge.AsyncBridgeResourceWithStreamingResponse(client.bridge)
        self.customers = customers.AsyncCustomersResourceWithStreamingResponse(client.customers)
        self.paykeys = paykeys.AsyncPaykeysResourceWithStreamingResponse(client.paykeys)
        self.charges = charges.AsyncChargesResourceWithStreamingResponse(client.charges)
        self.funding_events = funding_events.AsyncFundingEventsResourceWithStreamingResponse(client.funding_events)
        self.payments = payments.AsyncPaymentsResourceWithStreamingResponse(client.payments)
        self.payouts = payouts.AsyncPayoutsResourceWithStreamingResponse(client.payouts)
        self.reports = reports.AsyncReportsResourceWithStreamingResponse(client.reports)


Client = Straddle

AsyncClient = AsyncStraddle
