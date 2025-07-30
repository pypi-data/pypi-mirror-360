# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from straddle import Straddle, AsyncStraddle
from tests.utils import assert_matches_type
from straddle._utils import parse_datetime
from straddle.pagination import SyncPageNumberSchema, AsyncPageNumberSchema
from straddle.types.embed import (
    AccountV1,
)
from straddle.types.embed.account_paged_v1 import Data

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAccounts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Straddle) -> None:
        account = client.embed.accounts.create(
            access_level="standard",
            account_type="business",
            business_profile={
                "name": "name",
                "website": "https://example.com",
            },
            organization_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Straddle) -> None:
        account = client.embed.accounts.create(
            access_level="standard",
            account_type="business",
            business_profile={
                "name": "name",
                "website": "https://example.com",
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "state": "SE",
                    "zip": "zip",
                    "address2": "address2",
                    "country": "country",
                    "line1": "line1",
                    "line2": "line2",
                    "postal_code": "21029-1360",
                },
                "description": "description",
                "industry": {
                    "category": "category",
                    "mcc": "mcc",
                    "sector": "sector",
                },
                "legal_name": "legal_name",
                "phone": "+46991022",
                "support_channels": {
                    "email": "dev@stainless.com",
                    "phone": "+46991022",
                    "url": "https://example.com",
                },
                "tax_id": "210297980",
                "use_case": "use_case",
            },
            organization_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            external_id="external_id",
            metadata={"foo": "string"},
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Straddle) -> None:
        response = client.embed.accounts.with_raw_response.create(
            access_level="standard",
            account_type="business",
            business_profile={
                "name": "name",
                "website": "https://example.com",
            },
            organization_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Straddle) -> None:
        with client.embed.accounts.with_streaming_response.create(
            access_level="standard",
            account_type="business",
            business_profile={
                "name": "name",
                "website": "https://example.com",
            },
            organization_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(AccountV1, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_update(self, client: Straddle) -> None:
        account = client.embed.accounts.update(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            business_profile={
                "name": "name",
                "website": "https://example.com",
            },
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Straddle) -> None:
        account = client.embed.accounts.update(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            business_profile={
                "name": "name",
                "website": "https://example.com",
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "state": "SE",
                    "zip": "zip",
                    "address2": "address2",
                    "country": "country",
                    "line1": "line1",
                    "line2": "line2",
                    "postal_code": "21029-1360",
                },
                "description": "description",
                "industry": {
                    "category": "category",
                    "mcc": "mcc",
                    "sector": "sector",
                },
                "legal_name": "legal_name",
                "phone": "+46991022",
                "support_channels": {
                    "email": "dev@stainless.com",
                    "phone": "+46991022",
                    "url": "https://example.com",
                },
                "tax_id": "210297980",
                "use_case": "use_case",
            },
            external_id="external_id",
            metadata={"foo": "string"},
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Straddle) -> None:
        response = client.embed.accounts.with_raw_response.update(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            business_profile={
                "name": "name",
                "website": "https://example.com",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Straddle) -> None:
        with client.embed.accounts.with_streaming_response.update(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            business_profile={
                "name": "name",
                "website": "https://example.com",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(AccountV1, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.embed.accounts.with_raw_response.update(
                account_id="",
                business_profile={
                    "name": "name",
                    "website": "https://example.com",
                },
            )

    @parametrize
    def test_method_list(self, client: Straddle) -> None:
        account = client.embed.accounts.list()
        assert_matches_type(SyncPageNumberSchema[Data], account, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Straddle) -> None:
        account = client.embed.accounts.list(
            page_number=0,
            page_size=0,
            search_text="search_text",
            sort_by="sort_by",
            sort_order="asc",
            status="created",
            type="business",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(SyncPageNumberSchema[Data], account, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Straddle) -> None:
        response = client.embed.accounts.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(SyncPageNumberSchema[Data], account, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Straddle) -> None:
        with client.embed.accounts.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(SyncPageNumberSchema[Data], account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get(self, client: Straddle) -> None:
        account = client.embed.accounts.get(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    def test_method_get_with_all_params(self, client: Straddle) -> None:
        account = client.embed.accounts.get(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Straddle) -> None:
        response = client.embed.accounts.with_raw_response.get(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Straddle) -> None:
        with client.embed.accounts.with_streaming_response.get(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(AccountV1, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_get(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.embed.accounts.with_raw_response.get(
                account_id="",
            )

    @parametrize
    def test_method_onboard(self, client: Straddle) -> None:
        account = client.embed.accounts.onboard(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            terms_of_service={
                "accepted_date": parse_datetime("2019-12-27T18:11:19.117Z"),
                "agreement_type": "embedded",
                "agreement_url": "agreement_url",
            },
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    def test_method_onboard_with_all_params(self, client: Straddle) -> None:
        account = client.embed.accounts.onboard(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            terms_of_service={
                "accepted_date": parse_datetime("2019-12-27T18:11:19.117Z"),
                "agreement_type": "embedded",
                "agreement_url": "agreement_url",
                "accepted_ip": "accepted_ip",
                "accepted_user_agent": "accepted_user_agent",
            },
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    def test_raw_response_onboard(self, client: Straddle) -> None:
        response = client.embed.accounts.with_raw_response.onboard(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            terms_of_service={
                "accepted_date": parse_datetime("2019-12-27T18:11:19.117Z"),
                "agreement_type": "embedded",
                "agreement_url": "agreement_url",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    def test_streaming_response_onboard(self, client: Straddle) -> None:
        with client.embed.accounts.with_streaming_response.onboard(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            terms_of_service={
                "accepted_date": parse_datetime("2019-12-27T18:11:19.117Z"),
                "agreement_type": "embedded",
                "agreement_url": "agreement_url",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(AccountV1, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_onboard(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.embed.accounts.with_raw_response.onboard(
                account_id="",
                terms_of_service={
                    "accepted_date": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "agreement_type": "embedded",
                    "agreement_url": "agreement_url",
                },
            )

    @parametrize
    def test_method_simulate(self, client: Straddle) -> None:
        account = client.embed.accounts.simulate(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    def test_method_simulate_with_all_params(self, client: Straddle) -> None:
        account = client.embed.accounts.simulate(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            final_status="onboarding",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    def test_raw_response_simulate(self, client: Straddle) -> None:
        response = client.embed.accounts.with_raw_response.simulate(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    def test_streaming_response_simulate(self, client: Straddle) -> None:
        with client.embed.accounts.with_streaming_response.simulate(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(AccountV1, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_simulate(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.embed.accounts.with_raw_response.simulate(
                account_id="",
            )


class TestAsyncAccounts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncStraddle) -> None:
        account = await async_client.embed.accounts.create(
            access_level="standard",
            account_type="business",
            business_profile={
                "name": "name",
                "website": "https://example.com",
            },
            organization_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncStraddle) -> None:
        account = await async_client.embed.accounts.create(
            access_level="standard",
            account_type="business",
            business_profile={
                "name": "name",
                "website": "https://example.com",
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "state": "SE",
                    "zip": "zip",
                    "address2": "address2",
                    "country": "country",
                    "line1": "line1",
                    "line2": "line2",
                    "postal_code": "21029-1360",
                },
                "description": "description",
                "industry": {
                    "category": "category",
                    "mcc": "mcc",
                    "sector": "sector",
                },
                "legal_name": "legal_name",
                "phone": "+46991022",
                "support_channels": {
                    "email": "dev@stainless.com",
                    "phone": "+46991022",
                    "url": "https://example.com",
                },
                "tax_id": "210297980",
                "use_case": "use_case",
            },
            organization_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            external_id="external_id",
            metadata={"foo": "string"},
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncStraddle) -> None:
        response = await async_client.embed.accounts.with_raw_response.create(
            access_level="standard",
            account_type="business",
            business_profile={
                "name": "name",
                "website": "https://example.com",
            },
            organization_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncStraddle) -> None:
        async with async_client.embed.accounts.with_streaming_response.create(
            access_level="standard",
            account_type="business",
            business_profile={
                "name": "name",
                "website": "https://example.com",
            },
            organization_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(AccountV1, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_update(self, async_client: AsyncStraddle) -> None:
        account = await async_client.embed.accounts.update(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            business_profile={
                "name": "name",
                "website": "https://example.com",
            },
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncStraddle) -> None:
        account = await async_client.embed.accounts.update(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            business_profile={
                "name": "name",
                "website": "https://example.com",
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "state": "SE",
                    "zip": "zip",
                    "address2": "address2",
                    "country": "country",
                    "line1": "line1",
                    "line2": "line2",
                    "postal_code": "21029-1360",
                },
                "description": "description",
                "industry": {
                    "category": "category",
                    "mcc": "mcc",
                    "sector": "sector",
                },
                "legal_name": "legal_name",
                "phone": "+46991022",
                "support_channels": {
                    "email": "dev@stainless.com",
                    "phone": "+46991022",
                    "url": "https://example.com",
                },
                "tax_id": "210297980",
                "use_case": "use_case",
            },
            external_id="external_id",
            metadata={"foo": "string"},
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncStraddle) -> None:
        response = await async_client.embed.accounts.with_raw_response.update(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            business_profile={
                "name": "name",
                "website": "https://example.com",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncStraddle) -> None:
        async with async_client.embed.accounts.with_streaming_response.update(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            business_profile={
                "name": "name",
                "website": "https://example.com",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(AccountV1, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.embed.accounts.with_raw_response.update(
                account_id="",
                business_profile={
                    "name": "name",
                    "website": "https://example.com",
                },
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncStraddle) -> None:
        account = await async_client.embed.accounts.list()
        assert_matches_type(AsyncPageNumberSchema[Data], account, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncStraddle) -> None:
        account = await async_client.embed.accounts.list(
            page_number=0,
            page_size=0,
            search_text="search_text",
            sort_by="sort_by",
            sort_order="asc",
            status="created",
            type="business",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(AsyncPageNumberSchema[Data], account, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncStraddle) -> None:
        response = await async_client.embed.accounts.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(AsyncPageNumberSchema[Data], account, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncStraddle) -> None:
        async with async_client.embed.accounts.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(AsyncPageNumberSchema[Data], account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get(self, async_client: AsyncStraddle) -> None:
        account = await async_client.embed.accounts.get(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncStraddle) -> None:
        account = await async_client.embed.accounts.get(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncStraddle) -> None:
        response = await async_client.embed.accounts.with_raw_response.get(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncStraddle) -> None:
        async with async_client.embed.accounts.with_streaming_response.get(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(AccountV1, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_get(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.embed.accounts.with_raw_response.get(
                account_id="",
            )

    @parametrize
    async def test_method_onboard(self, async_client: AsyncStraddle) -> None:
        account = await async_client.embed.accounts.onboard(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            terms_of_service={
                "accepted_date": parse_datetime("2019-12-27T18:11:19.117Z"),
                "agreement_type": "embedded",
                "agreement_url": "agreement_url",
            },
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    async def test_method_onboard_with_all_params(self, async_client: AsyncStraddle) -> None:
        account = await async_client.embed.accounts.onboard(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            terms_of_service={
                "accepted_date": parse_datetime("2019-12-27T18:11:19.117Z"),
                "agreement_type": "embedded",
                "agreement_url": "agreement_url",
                "accepted_ip": "accepted_ip",
                "accepted_user_agent": "accepted_user_agent",
            },
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    async def test_raw_response_onboard(self, async_client: AsyncStraddle) -> None:
        response = await async_client.embed.accounts.with_raw_response.onboard(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            terms_of_service={
                "accepted_date": parse_datetime("2019-12-27T18:11:19.117Z"),
                "agreement_type": "embedded",
                "agreement_url": "agreement_url",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    async def test_streaming_response_onboard(self, async_client: AsyncStraddle) -> None:
        async with async_client.embed.accounts.with_streaming_response.onboard(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            terms_of_service={
                "accepted_date": parse_datetime("2019-12-27T18:11:19.117Z"),
                "agreement_type": "embedded",
                "agreement_url": "agreement_url",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(AccountV1, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_onboard(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.embed.accounts.with_raw_response.onboard(
                account_id="",
                terms_of_service={
                    "accepted_date": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "agreement_type": "embedded",
                    "agreement_url": "agreement_url",
                },
            )

    @parametrize
    async def test_method_simulate(self, async_client: AsyncStraddle) -> None:
        account = await async_client.embed.accounts.simulate(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    async def test_method_simulate_with_all_params(self, async_client: AsyncStraddle) -> None:
        account = await async_client.embed.accounts.simulate(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            final_status="onboarding",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    async def test_raw_response_simulate(self, async_client: AsyncStraddle) -> None:
        response = await async_client.embed.accounts.with_raw_response.simulate(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(AccountV1, account, path=["response"])

    @parametrize
    async def test_streaming_response_simulate(self, async_client: AsyncStraddle) -> None:
        async with async_client.embed.accounts.with_streaming_response.simulate(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(AccountV1, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_simulate(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.embed.accounts.with_raw_response.simulate(
                account_id="",
            )
