# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from straddle import Straddle, AsyncStraddle
from tests.utils import assert_matches_type
from straddle._utils import parse_date
from straddle.pagination import SyncPageNumberSchema, AsyncPageNumberSchema
from straddle.types.embed import (
    Representative,
)
from straddle.types.embed.representative_paged import Data

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRepresentatives:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Straddle) -> None:
        representative = client.embed.representatives.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            dob=parse_date("1980-01-01"),
            email="ron.swanson@pawnee.com",
            first_name="first_name",
            last_name="last_name",
            mobile_number="+12128675309",
            relationship={
                "control": True,
                "owner": True,
                "primary": True,
            },
            ssn_last4="1234",
        )
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Straddle) -> None:
        representative = client.embed.representatives.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            dob=parse_date("1980-01-01"),
            email="ron.swanson@pawnee.com",
            first_name="first_name",
            last_name="last_name",
            mobile_number="+12128675309",
            relationship={
                "control": True,
                "owner": True,
                "primary": True,
                "percent_ownership": 0,
                "title": "title",
            },
            ssn_last4="1234",
            external_id="external_id",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Straddle) -> None:
        response = client.embed.representatives.with_raw_response.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            dob=parse_date("1980-01-01"),
            email="ron.swanson@pawnee.com",
            first_name="first_name",
            last_name="last_name",
            mobile_number="+12128675309",
            relationship={
                "control": True,
                "owner": True,
                "primary": True,
            },
            ssn_last4="1234",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        representative = response.parse()
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Straddle) -> None:
        with client.embed.representatives.with_streaming_response.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            dob=parse_date("1980-01-01"),
            email="ron.swanson@pawnee.com",
            first_name="first_name",
            last_name="last_name",
            mobile_number="+12128675309",
            relationship={
                "control": True,
                "owner": True,
                "primary": True,
            },
            ssn_last4="1234",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            representative = response.parse()
            assert_matches_type(Representative, representative, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_update(self, client: Straddle) -> None:
        representative = client.embed.representatives.update(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            dob=parse_date("1980-01-01"),
            email="ron.swanson@pawnee.com",
            first_name="Ron",
            last_name="Swanson",
            mobile_number="+12128675309",
            relationship={
                "control": True,
                "owner": True,
                "primary": True,
            },
            ssn_last4="1234",
        )
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Straddle) -> None:
        representative = client.embed.representatives.update(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            dob=parse_date("1980-01-01"),
            email="ron.swanson@pawnee.com",
            first_name="Ron",
            last_name="Swanson",
            mobile_number="+12128675309",
            relationship={
                "control": True,
                "owner": True,
                "primary": True,
                "percent_ownership": 0,
                "title": "title",
            },
            ssn_last4="1234",
            external_id="external_id",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Straddle) -> None:
        response = client.embed.representatives.with_raw_response.update(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            dob=parse_date("1980-01-01"),
            email="ron.swanson@pawnee.com",
            first_name="Ron",
            last_name="Swanson",
            mobile_number="+12128675309",
            relationship={
                "control": True,
                "owner": True,
                "primary": True,
            },
            ssn_last4="1234",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        representative = response.parse()
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Straddle) -> None:
        with client.embed.representatives.with_streaming_response.update(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            dob=parse_date("1980-01-01"),
            email="ron.swanson@pawnee.com",
            first_name="Ron",
            last_name="Swanson",
            mobile_number="+12128675309",
            relationship={
                "control": True,
                "owner": True,
                "primary": True,
            },
            ssn_last4="1234",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            representative = response.parse()
            assert_matches_type(Representative, representative, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `representative_id` but received ''"):
            client.embed.representatives.with_raw_response.update(
                representative_id="",
                dob=parse_date("1980-01-01"),
                email="ron.swanson@pawnee.com",
                first_name="Ron",
                last_name="Swanson",
                mobile_number="+12128675309",
                relationship={
                    "control": True,
                    "owner": True,
                    "primary": True,
                },
                ssn_last4="1234",
            )

    @parametrize
    def test_method_list(self, client: Straddle) -> None:
        representative = client.embed.representatives.list()
        assert_matches_type(SyncPageNumberSchema[Data], representative, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Straddle) -> None:
        representative = client.embed.representatives.list(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            level="account",
            organization_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            page_number=0,
            page_size=0,
            platform_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sort_by="sort_by",
            sort_order="asc",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(SyncPageNumberSchema[Data], representative, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Straddle) -> None:
        response = client.embed.representatives.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        representative = response.parse()
        assert_matches_type(SyncPageNumberSchema[Data], representative, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Straddle) -> None:
        with client.embed.representatives.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            representative = response.parse()
            assert_matches_type(SyncPageNumberSchema[Data], representative, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get(self, client: Straddle) -> None:
        representative = client.embed.representatives.get(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    def test_method_get_with_all_params(self, client: Straddle) -> None:
        representative = client.embed.representatives.get(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Straddle) -> None:
        response = client.embed.representatives.with_raw_response.get(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        representative = response.parse()
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Straddle) -> None:
        with client.embed.representatives.with_streaming_response.get(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            representative = response.parse()
            assert_matches_type(Representative, representative, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_get(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `representative_id` but received ''"):
            client.embed.representatives.with_raw_response.get(
                representative_id="",
            )

    @parametrize
    def test_method_unmask(self, client: Straddle) -> None:
        representative = client.embed.representatives.unmask(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    def test_method_unmask_with_all_params(self, client: Straddle) -> None:
        representative = client.embed.representatives.unmask(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    def test_raw_response_unmask(self, client: Straddle) -> None:
        response = client.embed.representatives.with_raw_response.unmask(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        representative = response.parse()
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    def test_streaming_response_unmask(self, client: Straddle) -> None:
        with client.embed.representatives.with_streaming_response.unmask(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            representative = response.parse()
            assert_matches_type(Representative, representative, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_unmask(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `representative_id` but received ''"):
            client.embed.representatives.with_raw_response.unmask(
                representative_id="",
            )


class TestAsyncRepresentatives:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncStraddle) -> None:
        representative = await async_client.embed.representatives.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            dob=parse_date("1980-01-01"),
            email="ron.swanson@pawnee.com",
            first_name="first_name",
            last_name="last_name",
            mobile_number="+12128675309",
            relationship={
                "control": True,
                "owner": True,
                "primary": True,
            },
            ssn_last4="1234",
        )
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncStraddle) -> None:
        representative = await async_client.embed.representatives.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            dob=parse_date("1980-01-01"),
            email="ron.swanson@pawnee.com",
            first_name="first_name",
            last_name="last_name",
            mobile_number="+12128675309",
            relationship={
                "control": True,
                "owner": True,
                "primary": True,
                "percent_ownership": 0,
                "title": "title",
            },
            ssn_last4="1234",
            external_id="external_id",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncStraddle) -> None:
        response = await async_client.embed.representatives.with_raw_response.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            dob=parse_date("1980-01-01"),
            email="ron.swanson@pawnee.com",
            first_name="first_name",
            last_name="last_name",
            mobile_number="+12128675309",
            relationship={
                "control": True,
                "owner": True,
                "primary": True,
            },
            ssn_last4="1234",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        representative = await response.parse()
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncStraddle) -> None:
        async with async_client.embed.representatives.with_streaming_response.create(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            dob=parse_date("1980-01-01"),
            email="ron.swanson@pawnee.com",
            first_name="first_name",
            last_name="last_name",
            mobile_number="+12128675309",
            relationship={
                "control": True,
                "owner": True,
                "primary": True,
            },
            ssn_last4="1234",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            representative = await response.parse()
            assert_matches_type(Representative, representative, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_update(self, async_client: AsyncStraddle) -> None:
        representative = await async_client.embed.representatives.update(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            dob=parse_date("1980-01-01"),
            email="ron.swanson@pawnee.com",
            first_name="Ron",
            last_name="Swanson",
            mobile_number="+12128675309",
            relationship={
                "control": True,
                "owner": True,
                "primary": True,
            },
            ssn_last4="1234",
        )
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncStraddle) -> None:
        representative = await async_client.embed.representatives.update(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            dob=parse_date("1980-01-01"),
            email="ron.swanson@pawnee.com",
            first_name="Ron",
            last_name="Swanson",
            mobile_number="+12128675309",
            relationship={
                "control": True,
                "owner": True,
                "primary": True,
                "percent_ownership": 0,
                "title": "title",
            },
            ssn_last4="1234",
            external_id="external_id",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncStraddle) -> None:
        response = await async_client.embed.representatives.with_raw_response.update(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            dob=parse_date("1980-01-01"),
            email="ron.swanson@pawnee.com",
            first_name="Ron",
            last_name="Swanson",
            mobile_number="+12128675309",
            relationship={
                "control": True,
                "owner": True,
                "primary": True,
            },
            ssn_last4="1234",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        representative = await response.parse()
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncStraddle) -> None:
        async with async_client.embed.representatives.with_streaming_response.update(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            dob=parse_date("1980-01-01"),
            email="ron.swanson@pawnee.com",
            first_name="Ron",
            last_name="Swanson",
            mobile_number="+12128675309",
            relationship={
                "control": True,
                "owner": True,
                "primary": True,
            },
            ssn_last4="1234",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            representative = await response.parse()
            assert_matches_type(Representative, representative, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `representative_id` but received ''"):
            await async_client.embed.representatives.with_raw_response.update(
                representative_id="",
                dob=parse_date("1980-01-01"),
                email="ron.swanson@pawnee.com",
                first_name="Ron",
                last_name="Swanson",
                mobile_number="+12128675309",
                relationship={
                    "control": True,
                    "owner": True,
                    "primary": True,
                },
                ssn_last4="1234",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncStraddle) -> None:
        representative = await async_client.embed.representatives.list()
        assert_matches_type(AsyncPageNumberSchema[Data], representative, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncStraddle) -> None:
        representative = await async_client.embed.representatives.list(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            level="account",
            organization_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            page_number=0,
            page_size=0,
            platform_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sort_by="sort_by",
            sort_order="asc",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(AsyncPageNumberSchema[Data], representative, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncStraddle) -> None:
        response = await async_client.embed.representatives.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        representative = await response.parse()
        assert_matches_type(AsyncPageNumberSchema[Data], representative, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncStraddle) -> None:
        async with async_client.embed.representatives.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            representative = await response.parse()
            assert_matches_type(AsyncPageNumberSchema[Data], representative, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get(self, async_client: AsyncStraddle) -> None:
        representative = await async_client.embed.representatives.get(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncStraddle) -> None:
        representative = await async_client.embed.representatives.get(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncStraddle) -> None:
        response = await async_client.embed.representatives.with_raw_response.get(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        representative = await response.parse()
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncStraddle) -> None:
        async with async_client.embed.representatives.with_streaming_response.get(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            representative = await response.parse()
            assert_matches_type(Representative, representative, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_get(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `representative_id` but received ''"):
            await async_client.embed.representatives.with_raw_response.get(
                representative_id="",
            )

    @parametrize
    async def test_method_unmask(self, async_client: AsyncStraddle) -> None:
        representative = await async_client.embed.representatives.unmask(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    async def test_method_unmask_with_all_params(self, async_client: AsyncStraddle) -> None:
        representative = await async_client.embed.representatives.unmask(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="correlation-id",
            request_id="request-id",
        )
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    async def test_raw_response_unmask(self, async_client: AsyncStraddle) -> None:
        response = await async_client.embed.representatives.with_raw_response.unmask(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        representative = await response.parse()
        assert_matches_type(Representative, representative, path=["response"])

    @parametrize
    async def test_streaming_response_unmask(self, async_client: AsyncStraddle) -> None:
        async with async_client.embed.representatives.with_streaming_response.unmask(
            representative_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            representative = await response.parse()
            assert_matches_type(Representative, representative, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_unmask(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `representative_id` but received ''"):
            await async_client.embed.representatives.with_raw_response.unmask(
                representative_id="",
            )
