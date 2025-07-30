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
from ...pagination import SyncPageNumberSchema, AsyncPageNumberSchema
from ...types.embed import (
    linked_bank_account_list_params,
    linked_bank_account_create_params,
    linked_bank_account_update_params,
)
from ..._base_client import AsyncPaginator, make_request_options
from ...types.embed.linked_bank_account_v1 import LinkedBankAccountV1
from ...types.embed.linked_bank_account_paged_v1 import Data
from ...types.embed.linked_bank_account_unmask_v1 import LinkedBankAccountUnmaskV1

__all__ = ["LinkedBankAccountsResource", "AsyncLinkedBankAccountsResource"]


class LinkedBankAccountsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> LinkedBankAccountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return LinkedBankAccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LinkedBankAccountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return LinkedBankAccountsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        account_id: str,
        bank_account: linked_bank_account_create_params.BankAccount,
        metadata: Optional[Dict[str, Optional[str]]] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LinkedBankAccountV1:
        """Creates a new linked bank account associated with a Straddle account.

        This
        endpoint allows you to associate external bank accounts with a Straddle account
        for various payment operations such as payment deposits, payout withdrawals, and
        more.

        Args:
          account_id: The unique identifier of the Straddle account to associate this bank account
              with.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the linked bank account in a structured format.

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
            "/v1/linked_bank_accounts",
            body=maybe_transform(
                {
                    "account_id": account_id,
                    "bank_account": bank_account,
                    "metadata": metadata,
                },
                linked_bank_account_create_params.LinkedBankAccountCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LinkedBankAccountV1,
        )

    def update(
        self,
        linked_bank_account_id: str,
        *,
        bank_account: linked_bank_account_update_params.BankAccount,
        metadata: Optional[Dict[str, Optional[str]]] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LinkedBankAccountV1:
        """Updates an existing linked bank account's information.

        This can be used to
        update account details during onboarding or to update metadata associated with
        the linked account. The linked bank account must be in 'created' or 'onboarding'
        status.

        Args:
          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the linked bank account in a structured format.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not linked_bank_account_id:
            raise ValueError(
                f"Expected a non-empty value for `linked_bank_account_id` but received {linked_bank_account_id!r}"
            )
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
            f"/v1/linked_bank_accounts/{linked_bank_account_id}",
            body=maybe_transform(
                {
                    "bank_account": bank_account,
                    "metadata": metadata,
                },
                linked_bank_account_update_params.LinkedBankAccountUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LinkedBankAccountV1,
        )

    def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        level: Literal["account", "platform"] | NotGiven = NOT_GIVEN,
        page_number: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
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
        """Returns a list of bank accounts associated with a specific Straddle account.

        The
        linked bank accounts are returned sorted by creation date, with the most
        recently created appearing first. This endpoint supports pagination to handle
        accounts with multiple linked bank accounts.

        Args:
          account_id: The unique identifier of the related account.

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
            "/v1/linked_bank_accounts",
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
                        "page_number": page_number,
                        "page_size": page_size,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                    },
                    linked_bank_account_list_params.LinkedBankAccountListParams,
                ),
            ),
            model=Data,
        )

    def get(
        self,
        linked_bank_account_id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LinkedBankAccountV1:
        """
        Retrieves the details of a linked bank account that has previously been created.
        Supply the unique linked bank account `id`, and Straddle will return the
        corresponding information. The response includes masked account details for
        security purposes.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not linked_bank_account_id:
            raise ValueError(
                f"Expected a non-empty value for `linked_bank_account_id` but received {linked_bank_account_id!r}"
            )
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
            f"/v1/linked_bank_accounts/{linked_bank_account_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LinkedBankAccountV1,
        )

    def unmask(
        self,
        linked_bank_account_id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LinkedBankAccountUnmaskV1:
        """
        Retrieves the unmasked details of a linked bank account that has previously been
        created. Supply the unique linked bank account `id`, and Straddle will return
        the corresponding information, including sensitive details. This endpoint needs
        to be enabled by Straddle for your account and should only be used when
        absolutely necessary.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not linked_bank_account_id:
            raise ValueError(
                f"Expected a non-empty value for `linked_bank_account_id` but received {linked_bank_account_id!r}"
            )
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
            f"/v1/linked_bank_accounts/{linked_bank_account_id}/unmask",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LinkedBankAccountUnmaskV1,
        )


class AsyncLinkedBankAccountsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncLinkedBankAccountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return AsyncLinkedBankAccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLinkedBankAccountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return AsyncLinkedBankAccountsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        account_id: str,
        bank_account: linked_bank_account_create_params.BankAccount,
        metadata: Optional[Dict[str, Optional[str]]] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LinkedBankAccountV1:
        """Creates a new linked bank account associated with a Straddle account.

        This
        endpoint allows you to associate external bank accounts with a Straddle account
        for various payment operations such as payment deposits, payout withdrawals, and
        more.

        Args:
          account_id: The unique identifier of the Straddle account to associate this bank account
              with.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the linked bank account in a structured format.

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
            "/v1/linked_bank_accounts",
            body=await async_maybe_transform(
                {
                    "account_id": account_id,
                    "bank_account": bank_account,
                    "metadata": metadata,
                },
                linked_bank_account_create_params.LinkedBankAccountCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LinkedBankAccountV1,
        )

    async def update(
        self,
        linked_bank_account_id: str,
        *,
        bank_account: linked_bank_account_update_params.BankAccount,
        metadata: Optional[Dict[str, Optional[str]]] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LinkedBankAccountV1:
        """Updates an existing linked bank account's information.

        This can be used to
        update account details during onboarding or to update metadata associated with
        the linked account. The linked bank account must be in 'created' or 'onboarding'
        status.

        Args:
          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the linked bank account in a structured format.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not linked_bank_account_id:
            raise ValueError(
                f"Expected a non-empty value for `linked_bank_account_id` but received {linked_bank_account_id!r}"
            )
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
            f"/v1/linked_bank_accounts/{linked_bank_account_id}",
            body=await async_maybe_transform(
                {
                    "bank_account": bank_account,
                    "metadata": metadata,
                },
                linked_bank_account_update_params.LinkedBankAccountUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LinkedBankAccountV1,
        )

    def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        level: Literal["account", "platform"] | NotGiven = NOT_GIVEN,
        page_number: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
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
        """Returns a list of bank accounts associated with a specific Straddle account.

        The
        linked bank accounts are returned sorted by creation date, with the most
        recently created appearing first. This endpoint supports pagination to handle
        accounts with multiple linked bank accounts.

        Args:
          account_id: The unique identifier of the related account.

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
            "/v1/linked_bank_accounts",
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
                        "page_number": page_number,
                        "page_size": page_size,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                    },
                    linked_bank_account_list_params.LinkedBankAccountListParams,
                ),
            ),
            model=Data,
        )

    async def get(
        self,
        linked_bank_account_id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LinkedBankAccountV1:
        """
        Retrieves the details of a linked bank account that has previously been created.
        Supply the unique linked bank account `id`, and Straddle will return the
        corresponding information. The response includes masked account details for
        security purposes.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not linked_bank_account_id:
            raise ValueError(
                f"Expected a non-empty value for `linked_bank_account_id` but received {linked_bank_account_id!r}"
            )
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
            f"/v1/linked_bank_accounts/{linked_bank_account_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LinkedBankAccountV1,
        )

    async def unmask(
        self,
        linked_bank_account_id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LinkedBankAccountUnmaskV1:
        """
        Retrieves the unmasked details of a linked bank account that has previously been
        created. Supply the unique linked bank account `id`, and Straddle will return
        the corresponding information, including sensitive details. This endpoint needs
        to be enabled by Straddle for your account and should only be used when
        absolutely necessary.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not linked_bank_account_id:
            raise ValueError(
                f"Expected a non-empty value for `linked_bank_account_id` but received {linked_bank_account_id!r}"
            )
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
            f"/v1/linked_bank_accounts/{linked_bank_account_id}/unmask",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LinkedBankAccountUnmaskV1,
        )


class LinkedBankAccountsResourceWithRawResponse:
    def __init__(self, linked_bank_accounts: LinkedBankAccountsResource) -> None:
        self._linked_bank_accounts = linked_bank_accounts

        self.create = to_raw_response_wrapper(
            linked_bank_accounts.create,
        )
        self.update = to_raw_response_wrapper(
            linked_bank_accounts.update,
        )
        self.list = to_raw_response_wrapper(
            linked_bank_accounts.list,
        )
        self.get = to_raw_response_wrapper(
            linked_bank_accounts.get,
        )
        self.unmask = to_raw_response_wrapper(
            linked_bank_accounts.unmask,
        )


class AsyncLinkedBankAccountsResourceWithRawResponse:
    def __init__(self, linked_bank_accounts: AsyncLinkedBankAccountsResource) -> None:
        self._linked_bank_accounts = linked_bank_accounts

        self.create = async_to_raw_response_wrapper(
            linked_bank_accounts.create,
        )
        self.update = async_to_raw_response_wrapper(
            linked_bank_accounts.update,
        )
        self.list = async_to_raw_response_wrapper(
            linked_bank_accounts.list,
        )
        self.get = async_to_raw_response_wrapper(
            linked_bank_accounts.get,
        )
        self.unmask = async_to_raw_response_wrapper(
            linked_bank_accounts.unmask,
        )


class LinkedBankAccountsResourceWithStreamingResponse:
    def __init__(self, linked_bank_accounts: LinkedBankAccountsResource) -> None:
        self._linked_bank_accounts = linked_bank_accounts

        self.create = to_streamed_response_wrapper(
            linked_bank_accounts.create,
        )
        self.update = to_streamed_response_wrapper(
            linked_bank_accounts.update,
        )
        self.list = to_streamed_response_wrapper(
            linked_bank_accounts.list,
        )
        self.get = to_streamed_response_wrapper(
            linked_bank_accounts.get,
        )
        self.unmask = to_streamed_response_wrapper(
            linked_bank_accounts.unmask,
        )


class AsyncLinkedBankAccountsResourceWithStreamingResponse:
    def __init__(self, linked_bank_accounts: AsyncLinkedBankAccountsResource) -> None:
        self._linked_bank_accounts = linked_bank_accounts

        self.create = async_to_streamed_response_wrapper(
            linked_bank_accounts.create,
        )
        self.update = async_to_streamed_response_wrapper(
            linked_bank_accounts.update,
        )
        self.list = async_to_streamed_response_wrapper(
            linked_bank_accounts.list,
        )
        self.get = async_to_streamed_response_wrapper(
            linked_bank_accounts.get,
        )
        self.unmask = async_to_streamed_response_wrapper(
            linked_bank_accounts.unmask,
        )
