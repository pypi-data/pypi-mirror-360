# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deasy_client import Deasy, AsyncDeasy
from deasy_client.types import (
    ListVdbConnector,
    ConnectorResponse,
    VdbConnectorGetDeleteStatsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestVdbConnector:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Deasy) -> None:
        vdb_connector = client.vdb_connector.create(
            connector_body={
                "collection_name": "collection_name",
                "database_name": "database_name",
                "db_user": "db_user",
                "name": "name",
                "password": "password",
                "port": "port",
                "url": "url",
            },
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Deasy) -> None:
        vdb_connector = client.vdb_connector.create(
            connector_body={
                "collection_name": "collection_name",
                "database_name": "database_name",
                "db_user": "db_user",
                "name": "name",
                "password": "password",
                "port": "port",
                "url": "url",
                "filename_key": "filename_key",
                "index_info": {
                    "found_indexes": ["string"],
                    "total_indexes_found": 0,
                },
                "text_key": "text_key",
                "type": "PSQLVectorDBManager",
            },
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Deasy) -> None:
        response = client.vdb_connector.with_raw_response.create(
            connector_body={
                "collection_name": "collection_name",
                "database_name": "database_name",
                "db_user": "db_user",
                "name": "name",
                "password": "password",
                "port": "port",
                "url": "url",
            },
            connector_name="connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vdb_connector = response.parse()
        assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Deasy) -> None:
        with client.vdb_connector.with_streaming_response.create(
            connector_body={
                "collection_name": "collection_name",
                "database_name": "database_name",
                "db_user": "db_user",
                "name": "name",
                "password": "password",
                "port": "port",
                "url": "url",
            },
            connector_name="connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vdb_connector = response.parse()
            assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Deasy) -> None:
        vdb_connector = client.vdb_connector.update(
            connector_body={
                "collection_name": "collection_name",
                "database_name": "database_name",
                "db_user": "db_user",
                "name": "name",
                "password": "password",
                "port": "port",
                "url": "url",
            },
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Deasy) -> None:
        vdb_connector = client.vdb_connector.update(
            connector_body={
                "collection_name": "collection_name",
                "database_name": "database_name",
                "db_user": "db_user",
                "name": "name",
                "password": "password",
                "port": "port",
                "url": "url",
                "filename_key": "filename_key",
                "index_info": {
                    "found_indexes": ["string"],
                    "total_indexes_found": 0,
                },
                "text_key": "text_key",
                "type": "PSQLVectorDBManager",
            },
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Deasy) -> None:
        response = client.vdb_connector.with_raw_response.update(
            connector_body={
                "collection_name": "collection_name",
                "database_name": "database_name",
                "db_user": "db_user",
                "name": "name",
                "password": "password",
                "port": "port",
                "url": "url",
            },
            connector_name="connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vdb_connector = response.parse()
        assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Deasy) -> None:
        with client.vdb_connector.with_streaming_response.update(
            connector_body={
                "collection_name": "collection_name",
                "database_name": "database_name",
                "db_user": "db_user",
                "name": "name",
                "password": "password",
                "port": "port",
                "url": "url",
            },
            connector_name="connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vdb_connector = response.parse()
            assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Deasy) -> None:
        vdb_connector = client.vdb_connector.list()
        assert_matches_type(ListVdbConnector, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Deasy) -> None:
        response = client.vdb_connector.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vdb_connector = response.parse()
        assert_matches_type(ListVdbConnector, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Deasy) -> None:
        with client.vdb_connector.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vdb_connector = response.parse()
            assert_matches_type(ListVdbConnector, vdb_connector, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Deasy) -> None:
        vdb_connector = client.vdb_connector.delete(
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Deasy) -> None:
        response = client.vdb_connector.with_raw_response.delete(
            connector_name="connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vdb_connector = response.parse()
        assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Deasy) -> None:
        with client.vdb_connector.with_streaming_response.delete(
            connector_name="connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vdb_connector = response.parse()
            assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get_delete_stats(self, client: Deasy) -> None:
        vdb_connector = client.vdb_connector.get_delete_stats(
            connector_name="connector_name",
        )
        assert_matches_type(VdbConnectorGetDeleteStatsResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_delete_stats(self, client: Deasy) -> None:
        response = client.vdb_connector.with_raw_response.get_delete_stats(
            connector_name="connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vdb_connector = response.parse()
        assert_matches_type(VdbConnectorGetDeleteStatsResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_delete_stats(self, client: Deasy) -> None:
        with client.vdb_connector.with_streaming_response.get_delete_stats(
            connector_name="connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vdb_connector = response.parse()
            assert_matches_type(VdbConnectorGetDeleteStatsResponse, vdb_connector, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncVdbConnector:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncDeasy) -> None:
        vdb_connector = await async_client.vdb_connector.create(
            connector_body={
                "collection_name": "collection_name",
                "database_name": "database_name",
                "db_user": "db_user",
                "name": "name",
                "password": "password",
                "port": "port",
                "url": "url",
            },
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncDeasy) -> None:
        vdb_connector = await async_client.vdb_connector.create(
            connector_body={
                "collection_name": "collection_name",
                "database_name": "database_name",
                "db_user": "db_user",
                "name": "name",
                "password": "password",
                "port": "port",
                "url": "url",
                "filename_key": "filename_key",
                "index_info": {
                    "found_indexes": ["string"],
                    "total_indexes_found": 0,
                },
                "text_key": "text_key",
                "type": "PSQLVectorDBManager",
            },
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncDeasy) -> None:
        response = await async_client.vdb_connector.with_raw_response.create(
            connector_body={
                "collection_name": "collection_name",
                "database_name": "database_name",
                "db_user": "db_user",
                "name": "name",
                "password": "password",
                "port": "port",
                "url": "url",
            },
            connector_name="connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vdb_connector = await response.parse()
        assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncDeasy) -> None:
        async with async_client.vdb_connector.with_streaming_response.create(
            connector_body={
                "collection_name": "collection_name",
                "database_name": "database_name",
                "db_user": "db_user",
                "name": "name",
                "password": "password",
                "port": "port",
                "url": "url",
            },
            connector_name="connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vdb_connector = await response.parse()
            assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncDeasy) -> None:
        vdb_connector = await async_client.vdb_connector.update(
            connector_body={
                "collection_name": "collection_name",
                "database_name": "database_name",
                "db_user": "db_user",
                "name": "name",
                "password": "password",
                "port": "port",
                "url": "url",
            },
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncDeasy) -> None:
        vdb_connector = await async_client.vdb_connector.update(
            connector_body={
                "collection_name": "collection_name",
                "database_name": "database_name",
                "db_user": "db_user",
                "name": "name",
                "password": "password",
                "port": "port",
                "url": "url",
                "filename_key": "filename_key",
                "index_info": {
                    "found_indexes": ["string"],
                    "total_indexes_found": 0,
                },
                "text_key": "text_key",
                "type": "PSQLVectorDBManager",
            },
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncDeasy) -> None:
        response = await async_client.vdb_connector.with_raw_response.update(
            connector_body={
                "collection_name": "collection_name",
                "database_name": "database_name",
                "db_user": "db_user",
                "name": "name",
                "password": "password",
                "port": "port",
                "url": "url",
            },
            connector_name="connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vdb_connector = await response.parse()
        assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncDeasy) -> None:
        async with async_client.vdb_connector.with_streaming_response.update(
            connector_body={
                "collection_name": "collection_name",
                "database_name": "database_name",
                "db_user": "db_user",
                "name": "name",
                "password": "password",
                "port": "port",
                "url": "url",
            },
            connector_name="connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vdb_connector = await response.parse()
            assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncDeasy) -> None:
        vdb_connector = await async_client.vdb_connector.list()
        assert_matches_type(ListVdbConnector, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncDeasy) -> None:
        response = await async_client.vdb_connector.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vdb_connector = await response.parse()
        assert_matches_type(ListVdbConnector, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncDeasy) -> None:
        async with async_client.vdb_connector.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vdb_connector = await response.parse()
            assert_matches_type(ListVdbConnector, vdb_connector, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncDeasy) -> None:
        vdb_connector = await async_client.vdb_connector.delete(
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncDeasy) -> None:
        response = await async_client.vdb_connector.with_raw_response.delete(
            connector_name="connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vdb_connector = await response.parse()
        assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncDeasy) -> None:
        async with async_client.vdb_connector.with_streaming_response.delete(
            connector_name="connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vdb_connector = await response.parse()
            assert_matches_type(ConnectorResponse, vdb_connector, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_delete_stats(self, async_client: AsyncDeasy) -> None:
        vdb_connector = await async_client.vdb_connector.get_delete_stats(
            connector_name="connector_name",
        )
        assert_matches_type(VdbConnectorGetDeleteStatsResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_delete_stats(self, async_client: AsyncDeasy) -> None:
        response = await async_client.vdb_connector.with_raw_response.get_delete_stats(
            connector_name="connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vdb_connector = await response.parse()
        assert_matches_type(VdbConnectorGetDeleteStatsResponse, vdb_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_delete_stats(self, async_client: AsyncDeasy) -> None:
        async with async_client.vdb_connector.with_streaming_response.get_delete_stats(
            connector_name="connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vdb_connector = await response.parse()
            assert_matches_type(VdbConnectorGetDeleteStatsResponse, vdb_connector, path=["response"])

        assert cast(Any, response.is_closed) is True
