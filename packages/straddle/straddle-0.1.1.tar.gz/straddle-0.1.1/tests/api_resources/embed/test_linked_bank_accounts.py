# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from straddle import Straddle, AsyncStraddle
from tests.utils import assert_matches_type
from straddle.pagination import SyncPageNumberSchema, AsyncPageNumberSchema
from straddle.types.embed import (
    LinkedBankAccountV1,
    LinkedBankAccountUnmaskV1,
)
from straddle.types.embed.linked_bank_account_paged_v1 import Data

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLinkedBankAccounts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Straddle) -> None:
        linked_bank_account = client.embed.linked_bank_accounts.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            bank_account={
                "account_holder": "account_holder",
                "account_number": "account_number",
                "routing_number": "xxxxxxxxx",
            },
        )
        assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Straddle) -> None:
        linked_bank_account = client.embed.linked_bank_accounts.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            bank_account={
                "account_holder": "account_holder",
                "account_number": "account_number",
                "routing_number": "xxxxxxxxx",
            },
            metadata={"foo": "string"},
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Straddle) -> None:
        response = client.embed.linked_bank_accounts.with_raw_response.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            bank_account={
                "account_holder": "account_holder",
                "account_number": "account_number",
                "routing_number": "xxxxxxxxx",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        linked_bank_account = response.parse()
        assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Straddle) -> None:
        with client.embed.linked_bank_accounts.with_streaming_response.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            bank_account={
                "account_holder": "account_holder",
                "account_number": "account_number",
                "routing_number": "xxxxxxxxx",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            linked_bank_account = response.parse()
            assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_update(self, client: Straddle) -> None:
        linked_bank_account = client.embed.linked_bank_accounts.update(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            bank_account={
                "account_holder": "account_holder",
                "account_number": "account_number",
                "routing_number": "xxxxxxxxx",
            },
        )
        assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Straddle) -> None:
        linked_bank_account = client.embed.linked_bank_accounts.update(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            bank_account={
                "account_holder": "account_holder",
                "account_number": "account_number",
                "routing_number": "xxxxxxxxx",
            },
            metadata={"foo": "string"},
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Straddle) -> None:
        response = client.embed.linked_bank_accounts.with_raw_response.update(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            bank_account={
                "account_holder": "account_holder",
                "account_number": "account_number",
                "routing_number": "xxxxxxxxx",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        linked_bank_account = response.parse()
        assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Straddle) -> None:
        with client.embed.linked_bank_accounts.with_streaming_response.update(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            bank_account={
                "account_holder": "account_holder",
                "account_number": "account_number",
                "routing_number": "xxxxxxxxx",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            linked_bank_account = response.parse()
            assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Straddle) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `linked_bank_account_id` but received ''"
        ):
            client.embed.linked_bank_accounts.with_raw_response.update(
                linked_bank_account_id="",
                bank_account={
                    "account_holder": "account_holder",
                    "account_number": "account_number",
                    "routing_number": "xxxxxxxxx",
                },
            )

    @parametrize
    def test_method_list(self, client: Straddle) -> None:
        linked_bank_account = client.embed.linked_bank_accounts.list()
        assert_matches_type(SyncPageNumberSchema[Data], linked_bank_account, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Straddle) -> None:
        linked_bank_account = client.embed.linked_bank_accounts.list(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            level="account",
            page_number=0,
            page_size=0,
            sort_by="sort_by",
            sort_order="asc",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(SyncPageNumberSchema[Data], linked_bank_account, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Straddle) -> None:
        response = client.embed.linked_bank_accounts.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        linked_bank_account = response.parse()
        assert_matches_type(SyncPageNumberSchema[Data], linked_bank_account, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Straddle) -> None:
        with client.embed.linked_bank_accounts.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            linked_bank_account = response.parse()
            assert_matches_type(SyncPageNumberSchema[Data], linked_bank_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get(self, client: Straddle) -> None:
        linked_bank_account = client.embed.linked_bank_accounts.get(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

    @parametrize
    def test_method_get_with_all_params(self, client: Straddle) -> None:
        linked_bank_account = client.embed.linked_bank_accounts.get(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Straddle) -> None:
        response = client.embed.linked_bank_accounts.with_raw_response.get(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        linked_bank_account = response.parse()
        assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Straddle) -> None:
        with client.embed.linked_bank_accounts.with_streaming_response.get(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            linked_bank_account = response.parse()
            assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_get(self, client: Straddle) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `linked_bank_account_id` but received ''"
        ):
            client.embed.linked_bank_accounts.with_raw_response.get(
                linked_bank_account_id="",
            )

    @parametrize
    def test_method_unmask(self, client: Straddle) -> None:
        linked_bank_account = client.embed.linked_bank_accounts.unmask(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(LinkedBankAccountUnmaskV1, linked_bank_account, path=["response"])

    @parametrize
    def test_method_unmask_with_all_params(self, client: Straddle) -> None:
        linked_bank_account = client.embed.linked_bank_accounts.unmask(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(LinkedBankAccountUnmaskV1, linked_bank_account, path=["response"])

    @parametrize
    def test_raw_response_unmask(self, client: Straddle) -> None:
        response = client.embed.linked_bank_accounts.with_raw_response.unmask(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        linked_bank_account = response.parse()
        assert_matches_type(LinkedBankAccountUnmaskV1, linked_bank_account, path=["response"])

    @parametrize
    def test_streaming_response_unmask(self, client: Straddle) -> None:
        with client.embed.linked_bank_accounts.with_streaming_response.unmask(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            linked_bank_account = response.parse()
            assert_matches_type(LinkedBankAccountUnmaskV1, linked_bank_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_unmask(self, client: Straddle) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `linked_bank_account_id` but received ''"
        ):
            client.embed.linked_bank_accounts.with_raw_response.unmask(
                linked_bank_account_id="",
            )


class TestAsyncLinkedBankAccounts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncStraddle) -> None:
        linked_bank_account = await async_client.embed.linked_bank_accounts.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            bank_account={
                "account_holder": "account_holder",
                "account_number": "account_number",
                "routing_number": "xxxxxxxxx",
            },
        )
        assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncStraddle) -> None:
        linked_bank_account = await async_client.embed.linked_bank_accounts.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            bank_account={
                "account_holder": "account_holder",
                "account_number": "account_number",
                "routing_number": "xxxxxxxxx",
            },
            metadata={"foo": "string"},
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncStraddle) -> None:
        response = await async_client.embed.linked_bank_accounts.with_raw_response.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            bank_account={
                "account_holder": "account_holder",
                "account_number": "account_number",
                "routing_number": "xxxxxxxxx",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        linked_bank_account = await response.parse()
        assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncStraddle) -> None:
        async with async_client.embed.linked_bank_accounts.with_streaming_response.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            bank_account={
                "account_holder": "account_holder",
                "account_number": "account_number",
                "routing_number": "xxxxxxxxx",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            linked_bank_account = await response.parse()
            assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_update(self, async_client: AsyncStraddle) -> None:
        linked_bank_account = await async_client.embed.linked_bank_accounts.update(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            bank_account={
                "account_holder": "account_holder",
                "account_number": "account_number",
                "routing_number": "xxxxxxxxx",
            },
        )
        assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncStraddle) -> None:
        linked_bank_account = await async_client.embed.linked_bank_accounts.update(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            bank_account={
                "account_holder": "account_holder",
                "account_number": "account_number",
                "routing_number": "xxxxxxxxx",
            },
            metadata={"foo": "string"},
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncStraddle) -> None:
        response = await async_client.embed.linked_bank_accounts.with_raw_response.update(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            bank_account={
                "account_holder": "account_holder",
                "account_number": "account_number",
                "routing_number": "xxxxxxxxx",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        linked_bank_account = await response.parse()
        assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncStraddle) -> None:
        async with async_client.embed.linked_bank_accounts.with_streaming_response.update(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            bank_account={
                "account_holder": "account_holder",
                "account_number": "account_number",
                "routing_number": "xxxxxxxxx",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            linked_bank_account = await response.parse()
            assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `linked_bank_account_id` but received ''"
        ):
            await async_client.embed.linked_bank_accounts.with_raw_response.update(
                linked_bank_account_id="",
                bank_account={
                    "account_holder": "account_holder",
                    "account_number": "account_number",
                    "routing_number": "xxxxxxxxx",
                },
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncStraddle) -> None:
        linked_bank_account = await async_client.embed.linked_bank_accounts.list()
        assert_matches_type(AsyncPageNumberSchema[Data], linked_bank_account, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncStraddle) -> None:
        linked_bank_account = await async_client.embed.linked_bank_accounts.list(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            level="account",
            page_number=0,
            page_size=0,
            sort_by="sort_by",
            sort_order="asc",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(AsyncPageNumberSchema[Data], linked_bank_account, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncStraddle) -> None:
        response = await async_client.embed.linked_bank_accounts.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        linked_bank_account = await response.parse()
        assert_matches_type(AsyncPageNumberSchema[Data], linked_bank_account, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncStraddle) -> None:
        async with async_client.embed.linked_bank_accounts.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            linked_bank_account = await response.parse()
            assert_matches_type(AsyncPageNumberSchema[Data], linked_bank_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get(self, async_client: AsyncStraddle) -> None:
        linked_bank_account = await async_client.embed.linked_bank_accounts.get(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncStraddle) -> None:
        linked_bank_account = await async_client.embed.linked_bank_accounts.get(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncStraddle) -> None:
        response = await async_client.embed.linked_bank_accounts.with_raw_response.get(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        linked_bank_account = await response.parse()
        assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncStraddle) -> None:
        async with async_client.embed.linked_bank_accounts.with_streaming_response.get(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            linked_bank_account = await response.parse()
            assert_matches_type(LinkedBankAccountV1, linked_bank_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_get(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `linked_bank_account_id` but received ''"
        ):
            await async_client.embed.linked_bank_accounts.with_raw_response.get(
                linked_bank_account_id="",
            )

    @parametrize
    async def test_method_unmask(self, async_client: AsyncStraddle) -> None:
        linked_bank_account = await async_client.embed.linked_bank_accounts.unmask(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(LinkedBankAccountUnmaskV1, linked_bank_account, path=["response"])

    @parametrize
    async def test_method_unmask_with_all_params(self, async_client: AsyncStraddle) -> None:
        linked_bank_account = await async_client.embed.linked_bank_accounts.unmask(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(LinkedBankAccountUnmaskV1, linked_bank_account, path=["response"])

    @parametrize
    async def test_raw_response_unmask(self, async_client: AsyncStraddle) -> None:
        response = await async_client.embed.linked_bank_accounts.with_raw_response.unmask(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        linked_bank_account = await response.parse()
        assert_matches_type(LinkedBankAccountUnmaskV1, linked_bank_account, path=["response"])

    @parametrize
    async def test_streaming_response_unmask(self, async_client: AsyncStraddle) -> None:
        async with async_client.embed.linked_bank_accounts.with_streaming_response.unmask(
            linked_bank_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            linked_bank_account = await response.parse()
            assert_matches_type(LinkedBankAccountUnmaskV1, linked_bank_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_unmask(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `linked_bank_account_id` but received ''"
        ):
            await async_client.embed.linked_bank_accounts.with_raw_response.unmask(
                linked_bank_account_id="",
            )
