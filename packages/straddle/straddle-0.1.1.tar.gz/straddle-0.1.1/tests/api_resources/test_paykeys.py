# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from straddle import Straddle, AsyncStraddle
from tests.utils import assert_matches_type
from straddle.types import PaykeyV1, PaykeyUnmaskedV1, PaykeyRevealResponse
from straddle.pagination import SyncPageNumberSchema, AsyncPageNumberSchema
from straddle.types.paykey_summary_paged_v1 import Data

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPaykeys:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Straddle) -> None:
        paykey = client.paykeys.list()
        assert_matches_type(SyncPageNumberSchema[Data], paykey, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Straddle) -> None:
        paykey = client.paykeys.list(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            page_number=0,
            page_size=0,
            sort_by="institution_name",
            sort_order="asc",
            source=["bank_account"],
            status=["pending"],
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncPageNumberSchema[Data], paykey, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Straddle) -> None:
        response = client.paykeys.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        paykey = response.parse()
        assert_matches_type(SyncPageNumberSchema[Data], paykey, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Straddle) -> None:
        with client.paykeys.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            paykey = response.parse()
            assert_matches_type(SyncPageNumberSchema[Data], paykey, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_cancel(self, client: Straddle) -> None:
        paykey = client.paykeys.cancel(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(PaykeyV1, paykey, path=["response"])

    @parametrize
    def test_method_cancel_with_all_params(self, client: Straddle) -> None:
        paykey = client.paykeys.cancel(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reason="reason",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(PaykeyV1, paykey, path=["response"])

    @parametrize
    def test_raw_response_cancel(self, client: Straddle) -> None:
        response = client.paykeys.with_raw_response.cancel(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        paykey = response.parse()
        assert_matches_type(PaykeyV1, paykey, path=["response"])

    @parametrize
    def test_streaming_response_cancel(self, client: Straddle) -> None:
        with client.paykeys.with_streaming_response.cancel(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            paykey = response.parse()
            assert_matches_type(PaykeyV1, paykey, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_cancel(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.paykeys.with_raw_response.cancel(
                id="",
            )

    @parametrize
    def test_method_get(self, client: Straddle) -> None:
        paykey = client.paykeys.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(PaykeyV1, paykey, path=["response"])

    @parametrize
    def test_method_get_with_all_params(self, client: Straddle) -> None:
        paykey = client.paykeys.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(PaykeyV1, paykey, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Straddle) -> None:
        response = client.paykeys.with_raw_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        paykey = response.parse()
        assert_matches_type(PaykeyV1, paykey, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Straddle) -> None:
        with client.paykeys.with_streaming_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            paykey = response.parse()
            assert_matches_type(PaykeyV1, paykey, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_get(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.paykeys.with_raw_response.get(
                id="",
            )

    @parametrize
    def test_method_reveal(self, client: Straddle) -> None:
        paykey = client.paykeys.reveal(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(PaykeyRevealResponse, paykey, path=["response"])

    @parametrize
    def test_method_reveal_with_all_params(self, client: Straddle) -> None:
        paykey = client.paykeys.reveal(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(PaykeyRevealResponse, paykey, path=["response"])

    @parametrize
    def test_raw_response_reveal(self, client: Straddle) -> None:
        response = client.paykeys.with_raw_response.reveal(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        paykey = response.parse()
        assert_matches_type(PaykeyRevealResponse, paykey, path=["response"])

    @parametrize
    def test_streaming_response_reveal(self, client: Straddle) -> None:
        with client.paykeys.with_streaming_response.reveal(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            paykey = response.parse()
            assert_matches_type(PaykeyRevealResponse, paykey, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_reveal(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.paykeys.with_raw_response.reveal(
                id="",
            )

    @parametrize
    def test_method_unmasked(self, client: Straddle) -> None:
        paykey = client.paykeys.unmasked(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(PaykeyUnmaskedV1, paykey, path=["response"])

    @parametrize
    def test_method_unmasked_with_all_params(self, client: Straddle) -> None:
        paykey = client.paykeys.unmasked(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(PaykeyUnmaskedV1, paykey, path=["response"])

    @parametrize
    def test_raw_response_unmasked(self, client: Straddle) -> None:
        response = client.paykeys.with_raw_response.unmasked(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        paykey = response.parse()
        assert_matches_type(PaykeyUnmaskedV1, paykey, path=["response"])

    @parametrize
    def test_streaming_response_unmasked(self, client: Straddle) -> None:
        with client.paykeys.with_streaming_response.unmasked(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            paykey = response.parse()
            assert_matches_type(PaykeyUnmaskedV1, paykey, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_unmasked(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.paykeys.with_raw_response.unmasked(
                id="",
            )


class TestAsyncPaykeys:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncStraddle) -> None:
        paykey = await async_client.paykeys.list()
        assert_matches_type(AsyncPageNumberSchema[Data], paykey, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncStraddle) -> None:
        paykey = await async_client.paykeys.list(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            page_number=0,
            page_size=0,
            sort_by="institution_name",
            sort_order="asc",
            source=["bank_account"],
            status=["pending"],
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AsyncPageNumberSchema[Data], paykey, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncStraddle) -> None:
        response = await async_client.paykeys.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        paykey = await response.parse()
        assert_matches_type(AsyncPageNumberSchema[Data], paykey, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncStraddle) -> None:
        async with async_client.paykeys.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            paykey = await response.parse()
            assert_matches_type(AsyncPageNumberSchema[Data], paykey, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_cancel(self, async_client: AsyncStraddle) -> None:
        paykey = await async_client.paykeys.cancel(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(PaykeyV1, paykey, path=["response"])

    @parametrize
    async def test_method_cancel_with_all_params(self, async_client: AsyncStraddle) -> None:
        paykey = await async_client.paykeys.cancel(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reason="reason",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(PaykeyV1, paykey, path=["response"])

    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncStraddle) -> None:
        response = await async_client.paykeys.with_raw_response.cancel(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        paykey = await response.parse()
        assert_matches_type(PaykeyV1, paykey, path=["response"])

    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncStraddle) -> None:
        async with async_client.paykeys.with_streaming_response.cancel(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            paykey = await response.parse()
            assert_matches_type(PaykeyV1, paykey, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.paykeys.with_raw_response.cancel(
                id="",
            )

    @parametrize
    async def test_method_get(self, async_client: AsyncStraddle) -> None:
        paykey = await async_client.paykeys.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(PaykeyV1, paykey, path=["response"])

    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncStraddle) -> None:
        paykey = await async_client.paykeys.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(PaykeyV1, paykey, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncStraddle) -> None:
        response = await async_client.paykeys.with_raw_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        paykey = await response.parse()
        assert_matches_type(PaykeyV1, paykey, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncStraddle) -> None:
        async with async_client.paykeys.with_streaming_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            paykey = await response.parse()
            assert_matches_type(PaykeyV1, paykey, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_get(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.paykeys.with_raw_response.get(
                id="",
            )

    @parametrize
    async def test_method_reveal(self, async_client: AsyncStraddle) -> None:
        paykey = await async_client.paykeys.reveal(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(PaykeyRevealResponse, paykey, path=["response"])

    @parametrize
    async def test_method_reveal_with_all_params(self, async_client: AsyncStraddle) -> None:
        paykey = await async_client.paykeys.reveal(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(PaykeyRevealResponse, paykey, path=["response"])

    @parametrize
    async def test_raw_response_reveal(self, async_client: AsyncStraddle) -> None:
        response = await async_client.paykeys.with_raw_response.reveal(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        paykey = await response.parse()
        assert_matches_type(PaykeyRevealResponse, paykey, path=["response"])

    @parametrize
    async def test_streaming_response_reveal(self, async_client: AsyncStraddle) -> None:
        async with async_client.paykeys.with_streaming_response.reveal(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            paykey = await response.parse()
            assert_matches_type(PaykeyRevealResponse, paykey, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_reveal(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.paykeys.with_raw_response.reveal(
                id="",
            )

    @parametrize
    async def test_method_unmasked(self, async_client: AsyncStraddle) -> None:
        paykey = await async_client.paykeys.unmasked(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(PaykeyUnmaskedV1, paykey, path=["response"])

    @parametrize
    async def test_method_unmasked_with_all_params(self, async_client: AsyncStraddle) -> None:
        paykey = await async_client.paykeys.unmasked(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(PaykeyUnmaskedV1, paykey, path=["response"])

    @parametrize
    async def test_raw_response_unmasked(self, async_client: AsyncStraddle) -> None:
        response = await async_client.paykeys.with_raw_response.unmasked(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        paykey = await response.parse()
        assert_matches_type(PaykeyUnmaskedV1, paykey, path=["response"])

    @parametrize
    async def test_streaming_response_unmasked(self, async_client: AsyncStraddle) -> None:
        async with async_client.paykeys.with_streaming_response.unmasked(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            paykey = await response.parse()
            assert_matches_type(PaykeyUnmaskedV1, paykey, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_unmasked(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.paykeys.with_raw_response.unmasked(
                id="",
            )
