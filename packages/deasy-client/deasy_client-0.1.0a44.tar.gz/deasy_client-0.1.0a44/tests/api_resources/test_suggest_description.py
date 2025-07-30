# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deasy_client import Deasy, AsyncDeasy
from deasy_client.types import SuggestDescriptionCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSuggestDescription:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Deasy) -> None:
        suggest_description = client.suggest_description.create(
            data_connector_name="data_connector_name",
            tag_name="tag_name",
        )
        assert_matches_type(SuggestDescriptionCreateResponse, suggest_description, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Deasy) -> None:
        suggest_description = client.suggest_description.create(
            data_connector_name="data_connector_name",
            tag_name="tag_name",
            available_values=["string"],
            context="context",
            current_description="current_description",
            dataslice_id="dataslice_id",
            llm_profile_name="llm_profile_name",
        )
        assert_matches_type(SuggestDescriptionCreateResponse, suggest_description, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Deasy) -> None:
        response = client.suggest_description.with_raw_response.create(
            data_connector_name="data_connector_name",
            tag_name="tag_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        suggest_description = response.parse()
        assert_matches_type(SuggestDescriptionCreateResponse, suggest_description, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Deasy) -> None:
        with client.suggest_description.with_streaming_response.create(
            data_connector_name="data_connector_name",
            tag_name="tag_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            suggest_description = response.parse()
            assert_matches_type(SuggestDescriptionCreateResponse, suggest_description, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSuggestDescription:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncDeasy) -> None:
        suggest_description = await async_client.suggest_description.create(
            data_connector_name="data_connector_name",
            tag_name="tag_name",
        )
        assert_matches_type(SuggestDescriptionCreateResponse, suggest_description, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncDeasy) -> None:
        suggest_description = await async_client.suggest_description.create(
            data_connector_name="data_connector_name",
            tag_name="tag_name",
            available_values=["string"],
            context="context",
            current_description="current_description",
            dataslice_id="dataslice_id",
            llm_profile_name="llm_profile_name",
        )
        assert_matches_type(SuggestDescriptionCreateResponse, suggest_description, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncDeasy) -> None:
        response = await async_client.suggest_description.with_raw_response.create(
            data_connector_name="data_connector_name",
            tag_name="tag_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        suggest_description = await response.parse()
        assert_matches_type(SuggestDescriptionCreateResponse, suggest_description, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncDeasy) -> None:
        async with async_client.suggest_description.with_streaming_response.create(
            data_connector_name="data_connector_name",
            tag_name="tag_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            suggest_description = await response.parse()
            assert_matches_type(SuggestDescriptionCreateResponse, suggest_description, path=["response"])

        assert cast(Any, response.is_closed) is True
