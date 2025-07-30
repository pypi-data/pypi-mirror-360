# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deasy_client import Deasy, AsyncDeasy
from deasy_client.types import (
    TagResponse,
    TagListResponse,
    TagCreateResponse,
    TagUpsertResponse,
    TagGetDeleteStatsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTags:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Deasy) -> None:
        tag = client.tags.create(
            tag_data={
                "name": "name",
                "output_type": "output_type",
            },
        )
        assert_matches_type(TagCreateResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Deasy) -> None:
        tag = client.tags.create(
            tag_data={
                "name": "name",
                "output_type": "output_type",
                "available_values": ["string"],
                "date_format": "date_format",
                "description": "description",
                "enhance_file_metadata": True,
                "examples": ["string"],
                "max_values": 0,
                "tag_id": "tag_id",
                "tuned": 0,
            },
        )
        assert_matches_type(TagCreateResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Deasy) -> None:
        response = client.tags.with_raw_response.create(
            tag_data={
                "name": "name",
                "output_type": "output_type",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tag = response.parse()
        assert_matches_type(TagCreateResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Deasy) -> None:
        with client.tags.with_streaming_response.create(
            tag_data={
                "name": "name",
                "output_type": "output_type",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tag = response.parse()
            assert_matches_type(TagCreateResponse, tag, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Deasy) -> None:
        tag = client.tags.update(
            tag_data={
                "name": "name",
                "output_type": "output_type",
            },
        )
        assert_matches_type(TagResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Deasy) -> None:
        tag = client.tags.update(
            tag_data={
                "name": "name",
                "output_type": "output_type",
                "available_values": ["string"],
                "date_format": "date_format",
                "description": "description",
                "enhance_file_metadata": True,
                "examples": ["string"],
                "max_values": 0,
                "tag_id": "tag_id",
                "tuned": 0,
            },
        )
        assert_matches_type(TagResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Deasy) -> None:
        response = client.tags.with_raw_response.update(
            tag_data={
                "name": "name",
                "output_type": "output_type",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tag = response.parse()
        assert_matches_type(TagResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Deasy) -> None:
        with client.tags.with_streaming_response.update(
            tag_data={
                "name": "name",
                "output_type": "output_type",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tag = response.parse()
            assert_matches_type(TagResponse, tag, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Deasy) -> None:
        tag = client.tags.list()
        assert_matches_type(TagListResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Deasy) -> None:
        response = client.tags.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tag = response.parse()
        assert_matches_type(TagListResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Deasy) -> None:
        with client.tags.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tag = response.parse()
            assert_matches_type(TagListResponse, tag, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Deasy) -> None:
        tag = client.tags.delete(
            tag_name="tag_name",
        )
        assert_matches_type(TagResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Deasy) -> None:
        response = client.tags.with_raw_response.delete(
            tag_name="tag_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tag = response.parse()
        assert_matches_type(TagResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Deasy) -> None:
        with client.tags.with_streaming_response.delete(
            tag_name="tag_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tag = response.parse()
            assert_matches_type(TagResponse, tag, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get_delete_stats(self, client: Deasy) -> None:
        tag = client.tags.get_delete_stats(
            tag_name="tag_name",
        )
        assert_matches_type(TagGetDeleteStatsResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_delete_stats(self, client: Deasy) -> None:
        response = client.tags.with_raw_response.get_delete_stats(
            tag_name="tag_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tag = response.parse()
        assert_matches_type(TagGetDeleteStatsResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_delete_stats(self, client: Deasy) -> None:
        with client.tags.with_streaming_response.get_delete_stats(
            tag_name="tag_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tag = response.parse()
            assert_matches_type(TagGetDeleteStatsResponse, tag, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_upsert(self, client: Deasy) -> None:
        tag = client.tags.upsert(
            tag_data={
                "name": "name",
                "output_type": "output_type",
            },
        )
        assert_matches_type(TagUpsertResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_upsert_with_all_params(self, client: Deasy) -> None:
        tag = client.tags.upsert(
            tag_data={
                "name": "name",
                "output_type": "output_type",
                "available_values": ["string"],
                "date_format": "date_format",
                "description": "description",
                "enhance_file_metadata": True,
                "examples": ["string"],
                "max_values": 0,
                "tag_id": "tag_id",
                "tuned": 0,
            },
        )
        assert_matches_type(TagUpsertResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_upsert(self, client: Deasy) -> None:
        response = client.tags.with_raw_response.upsert(
            tag_data={
                "name": "name",
                "output_type": "output_type",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tag = response.parse()
        assert_matches_type(TagUpsertResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_upsert(self, client: Deasy) -> None:
        with client.tags.with_streaming_response.upsert(
            tag_data={
                "name": "name",
                "output_type": "output_type",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tag = response.parse()
            assert_matches_type(TagUpsertResponse, tag, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTags:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncDeasy) -> None:
        tag = await async_client.tags.create(
            tag_data={
                "name": "name",
                "output_type": "output_type",
            },
        )
        assert_matches_type(TagCreateResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncDeasy) -> None:
        tag = await async_client.tags.create(
            tag_data={
                "name": "name",
                "output_type": "output_type",
                "available_values": ["string"],
                "date_format": "date_format",
                "description": "description",
                "enhance_file_metadata": True,
                "examples": ["string"],
                "max_values": 0,
                "tag_id": "tag_id",
                "tuned": 0,
            },
        )
        assert_matches_type(TagCreateResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncDeasy) -> None:
        response = await async_client.tags.with_raw_response.create(
            tag_data={
                "name": "name",
                "output_type": "output_type",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tag = await response.parse()
        assert_matches_type(TagCreateResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncDeasy) -> None:
        async with async_client.tags.with_streaming_response.create(
            tag_data={
                "name": "name",
                "output_type": "output_type",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tag = await response.parse()
            assert_matches_type(TagCreateResponse, tag, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncDeasy) -> None:
        tag = await async_client.tags.update(
            tag_data={
                "name": "name",
                "output_type": "output_type",
            },
        )
        assert_matches_type(TagResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncDeasy) -> None:
        tag = await async_client.tags.update(
            tag_data={
                "name": "name",
                "output_type": "output_type",
                "available_values": ["string"],
                "date_format": "date_format",
                "description": "description",
                "enhance_file_metadata": True,
                "examples": ["string"],
                "max_values": 0,
                "tag_id": "tag_id",
                "tuned": 0,
            },
        )
        assert_matches_type(TagResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncDeasy) -> None:
        response = await async_client.tags.with_raw_response.update(
            tag_data={
                "name": "name",
                "output_type": "output_type",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tag = await response.parse()
        assert_matches_type(TagResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncDeasy) -> None:
        async with async_client.tags.with_streaming_response.update(
            tag_data={
                "name": "name",
                "output_type": "output_type",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tag = await response.parse()
            assert_matches_type(TagResponse, tag, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncDeasy) -> None:
        tag = await async_client.tags.list()
        assert_matches_type(TagListResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncDeasy) -> None:
        response = await async_client.tags.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tag = await response.parse()
        assert_matches_type(TagListResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncDeasy) -> None:
        async with async_client.tags.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tag = await response.parse()
            assert_matches_type(TagListResponse, tag, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncDeasy) -> None:
        tag = await async_client.tags.delete(
            tag_name="tag_name",
        )
        assert_matches_type(TagResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncDeasy) -> None:
        response = await async_client.tags.with_raw_response.delete(
            tag_name="tag_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tag = await response.parse()
        assert_matches_type(TagResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncDeasy) -> None:
        async with async_client.tags.with_streaming_response.delete(
            tag_name="tag_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tag = await response.parse()
            assert_matches_type(TagResponse, tag, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_delete_stats(self, async_client: AsyncDeasy) -> None:
        tag = await async_client.tags.get_delete_stats(
            tag_name="tag_name",
        )
        assert_matches_type(TagGetDeleteStatsResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_delete_stats(self, async_client: AsyncDeasy) -> None:
        response = await async_client.tags.with_raw_response.get_delete_stats(
            tag_name="tag_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tag = await response.parse()
        assert_matches_type(TagGetDeleteStatsResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_delete_stats(self, async_client: AsyncDeasy) -> None:
        async with async_client.tags.with_streaming_response.get_delete_stats(
            tag_name="tag_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tag = await response.parse()
            assert_matches_type(TagGetDeleteStatsResponse, tag, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_upsert(self, async_client: AsyncDeasy) -> None:
        tag = await async_client.tags.upsert(
            tag_data={
                "name": "name",
                "output_type": "output_type",
            },
        )
        assert_matches_type(TagUpsertResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_upsert_with_all_params(self, async_client: AsyncDeasy) -> None:
        tag = await async_client.tags.upsert(
            tag_data={
                "name": "name",
                "output_type": "output_type",
                "available_values": ["string"],
                "date_format": "date_format",
                "description": "description",
                "enhance_file_metadata": True,
                "examples": ["string"],
                "max_values": 0,
                "tag_id": "tag_id",
                "tuned": 0,
            },
        )
        assert_matches_type(TagUpsertResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_upsert(self, async_client: AsyncDeasy) -> None:
        response = await async_client.tags.with_raw_response.upsert(
            tag_data={
                "name": "name",
                "output_type": "output_type",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tag = await response.parse()
        assert_matches_type(TagUpsertResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_upsert(self, async_client: AsyncDeasy) -> None:
        async with async_client.tags.with_streaming_response.upsert(
            tag_data={
                "name": "name",
                "output_type": "output_type",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tag = await response.parse()
            assert_matches_type(TagUpsertResponse, tag, path=["response"])

        assert cast(Any, response.is_closed) is True
