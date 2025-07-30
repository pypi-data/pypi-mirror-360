# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deasy_client import Deasy, AsyncDeasy
from deasy_client.types import PrepareDataCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPrepareData:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Deasy) -> None:
        prepare_data = client.prepare_data.create(
            data_connector_name="data_connector_name",
        )
        assert_matches_type(PrepareDataCreateResponse, prepare_data, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Deasy) -> None:
        prepare_data = client.prepare_data.create(
            data_connector_name="data_connector_name",
            job_id="job_id",
            llm_profile_name="llm_profile_name",
            total_data_sets=0,
        )
        assert_matches_type(PrepareDataCreateResponse, prepare_data, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Deasy) -> None:
        response = client.prepare_data.with_raw_response.create(
            data_connector_name="data_connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prepare_data = response.parse()
        assert_matches_type(PrepareDataCreateResponse, prepare_data, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Deasy) -> None:
        with client.prepare_data.with_streaming_response.create(
            data_connector_name="data_connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prepare_data = response.parse()
            assert_matches_type(PrepareDataCreateResponse, prepare_data, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPrepareData:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncDeasy) -> None:
        prepare_data = await async_client.prepare_data.create(
            data_connector_name="data_connector_name",
        )
        assert_matches_type(PrepareDataCreateResponse, prepare_data, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncDeasy) -> None:
        prepare_data = await async_client.prepare_data.create(
            data_connector_name="data_connector_name",
            job_id="job_id",
            llm_profile_name="llm_profile_name",
            total_data_sets=0,
        )
        assert_matches_type(PrepareDataCreateResponse, prepare_data, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncDeasy) -> None:
        response = await async_client.prepare_data.with_raw_response.create(
            data_connector_name="data_connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prepare_data = await response.parse()
        assert_matches_type(PrepareDataCreateResponse, prepare_data, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncDeasy) -> None:
        async with async_client.prepare_data.with_streaming_response.create(
            data_connector_name="data_connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prepare_data = await response.parse()
            assert_matches_type(PrepareDataCreateResponse, prepare_data, path=["response"])

        assert cast(Any, response.is_closed) is True
