# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from straddle import Straddle, AsyncStraddle
from tests.utils import assert_matches_type
from straddle.pagination import SyncPageNumberSchema, AsyncPageNumberSchema
from straddle.types.embed.accounts import (
    CapabilityRequestPagedV1,
)
from straddle.types.embed.accounts.capability_request_paged_v1 import Data

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCapabilityRequests:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Straddle) -> None:
        capability_request = client.embed.accounts.capability_requests.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CapabilityRequestPagedV1, capability_request, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Straddle) -> None:
        capability_request = client.embed.accounts.capability_requests.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            businesses={"enable": True},
            charges={
                "daily_amount": 0,
                "enable": True,
                "max_amount": 0,
                "monthly_amount": 0,
                "monthly_count": 0,
            },
            individuals={"enable": True},
            internet={"enable": True},
            payouts={
                "daily_amount": 0,
                "enable": True,
                "max_amount": 0,
                "monthly_amount": 0,
                "monthly_count": 0,
            },
            signed_agreement={"enable": True},
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(CapabilityRequestPagedV1, capability_request, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Straddle) -> None:
        response = client.embed.accounts.capability_requests.with_raw_response.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        capability_request = response.parse()
        assert_matches_type(CapabilityRequestPagedV1, capability_request, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Straddle) -> None:
        with client.embed.accounts.capability_requests.with_streaming_response.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            capability_request = response.parse()
            assert_matches_type(CapabilityRequestPagedV1, capability_request, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.embed.accounts.capability_requests.with_raw_response.create(
                account_id="",
            )

    @parametrize
    def test_method_list(self, client: Straddle) -> None:
        capability_request = client.embed.accounts.capability_requests.list(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncPageNumberSchema[Data], capability_request, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Straddle) -> None:
        capability_request = client.embed.accounts.capability_requests.list(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            category="payment_type",
            page_number=0,
            page_size=0,
            sort_by="sort_by",
            sort_order="asc",
            status="active",
            type="charges",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(SyncPageNumberSchema[Data], capability_request, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Straddle) -> None:
        response = client.embed.accounts.capability_requests.with_raw_response.list(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        capability_request = response.parse()
        assert_matches_type(SyncPageNumberSchema[Data], capability_request, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Straddle) -> None:
        with client.embed.accounts.capability_requests.with_streaming_response.list(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            capability_request = response.parse()
            assert_matches_type(SyncPageNumberSchema[Data], capability_request, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.embed.accounts.capability_requests.with_raw_response.list(
                account_id="",
            )


class TestAsyncCapabilityRequests:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncStraddle) -> None:
        capability_request = await async_client.embed.accounts.capability_requests.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CapabilityRequestPagedV1, capability_request, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncStraddle) -> None:
        capability_request = await async_client.embed.accounts.capability_requests.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            businesses={"enable": True},
            charges={
                "daily_amount": 0,
                "enable": True,
                "max_amount": 0,
                "monthly_amount": 0,
                "monthly_count": 0,
            },
            individuals={"enable": True},
            internet={"enable": True},
            payouts={
                "daily_amount": 0,
                "enable": True,
                "max_amount": 0,
                "monthly_amount": 0,
                "monthly_count": 0,
            },
            signed_agreement={"enable": True},
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(CapabilityRequestPagedV1, capability_request, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncStraddle) -> None:
        response = await async_client.embed.accounts.capability_requests.with_raw_response.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        capability_request = await response.parse()
        assert_matches_type(CapabilityRequestPagedV1, capability_request, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncStraddle) -> None:
        async with async_client.embed.accounts.capability_requests.with_streaming_response.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            capability_request = await response.parse()
            assert_matches_type(CapabilityRequestPagedV1, capability_request, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.embed.accounts.capability_requests.with_raw_response.create(
                account_id="",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncStraddle) -> None:
        capability_request = await async_client.embed.accounts.capability_requests.list(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AsyncPageNumberSchema[Data], capability_request, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncStraddle) -> None:
        capability_request = await async_client.embed.accounts.capability_requests.list(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            category="payment_type",
            page_number=0,
            page_size=0,
            sort_by="sort_by",
            sort_order="asc",
            status="active",
            type="charges",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(AsyncPageNumberSchema[Data], capability_request, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncStraddle) -> None:
        response = await async_client.embed.accounts.capability_requests.with_raw_response.list(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        capability_request = await response.parse()
        assert_matches_type(AsyncPageNumberSchema[Data], capability_request, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncStraddle) -> None:
        async with async_client.embed.accounts.capability_requests.with_streaming_response.list(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            capability_request = await response.parse()
            assert_matches_type(AsyncPageNumberSchema[Data], capability_request, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.embed.accounts.capability_requests.with_raw_response.list(
                account_id="",
            )
