# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deasy_client import Deasy, AsyncDeasy
from deasy_client.types import (
    DatasliceListResponse,
    DatasliceCreateResponse,
    DatasliceDeleteResponse,
    DatasliceGetFilesResponse,
    DatasliceGetMetricsResponse,
    DatasliceGetFileCountResponse,
    DatasliceGetTagVdbDistributionResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDataslice:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Deasy) -> None:
        dataslice = client.dataslice.create(
            data_connector_name="data_connector_name",
            dataslice_name="dataslice_name",
            graph_id="graph_id",
            latest_graph={"foo": "bar"},
        )
        assert_matches_type(DatasliceCreateResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Deasy) -> None:
        dataslice = client.dataslice.create(
            data_connector_name="data_connector_name",
            dataslice_name="dataslice_name",
            graph_id="graph_id",
            latest_graph={"foo": "bar"},
            condition={
                "children": [],
                "condition": "AND",
                "tag": {
                    "name": "name",
                    "values": ["string"],
                    "operator": "operator",
                },
            },
            data_points=0,
            description="description",
            parent_dataslice_id="parent_dataslice_id",
            status="status",
        )
        assert_matches_type(DatasliceCreateResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Deasy) -> None:
        response = client.dataslice.with_raw_response.create(
            data_connector_name="data_connector_name",
            dataslice_name="dataslice_name",
            graph_id="graph_id",
            latest_graph={"foo": "bar"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataslice = response.parse()
        assert_matches_type(DatasliceCreateResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Deasy) -> None:
        with client.dataslice.with_streaming_response.create(
            data_connector_name="data_connector_name",
            dataslice_name="dataslice_name",
            graph_id="graph_id",
            latest_graph={"foo": "bar"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataslice = response.parse()
            assert_matches_type(DatasliceCreateResponse, dataslice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Deasy) -> None:
        dataslice = client.dataslice.list()
        assert_matches_type(DatasliceListResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Deasy) -> None:
        response = client.dataslice.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataslice = response.parse()
        assert_matches_type(DatasliceListResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Deasy) -> None:
        with client.dataslice.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataslice = response.parse()
            assert_matches_type(DatasliceListResponse, dataslice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Deasy) -> None:
        dataslice = client.dataslice.delete(
            dataslice_id="dataslice_id",
        )
        assert_matches_type(DatasliceDeleteResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Deasy) -> None:
        response = client.dataslice.with_raw_response.delete(
            dataslice_id="dataslice_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataslice = response.parse()
        assert_matches_type(DatasliceDeleteResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Deasy) -> None:
        with client.dataslice.with_streaming_response.delete(
            dataslice_id="dataslice_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataslice = response.parse()
            assert_matches_type(DatasliceDeleteResponse, dataslice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get_file_count(self, client: Deasy) -> None:
        dataslice = client.dataslice.get_file_count(
            data_connector_name="data_connector_name",
        )
        assert_matches_type(DatasliceGetFileCountResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_file_count_with_all_params(self, client: Deasy) -> None:
        dataslice = client.dataslice.get_file_count(
            data_connector_name="data_connector_name",
            condition={
                "children": [],
                "condition": "AND",
                "tag": {
                    "name": "name",
                    "values": ["string"],
                    "operator": "operator",
                },
            },
            dataslice_id="dataslice_id",
        )
        assert_matches_type(DatasliceGetFileCountResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_file_count(self, client: Deasy) -> None:
        response = client.dataslice.with_raw_response.get_file_count(
            data_connector_name="data_connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataslice = response.parse()
        assert_matches_type(DatasliceGetFileCountResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_file_count(self, client: Deasy) -> None:
        with client.dataslice.with_streaming_response.get_file_count(
            data_connector_name="data_connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataslice = response.parse()
            assert_matches_type(DatasliceGetFileCountResponse, dataslice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get_files(self, client: Deasy) -> None:
        dataslice = client.dataslice.get_files(
            dataslice_id="dataslice_id",
        )
        assert_matches_type(DatasliceGetFilesResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_files(self, client: Deasy) -> None:
        response = client.dataslice.with_raw_response.get_files(
            dataslice_id="dataslice_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataslice = response.parse()
        assert_matches_type(DatasliceGetFilesResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_files(self, client: Deasy) -> None:
        with client.dataslice.with_streaming_response.get_files(
            dataslice_id="dataslice_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataslice = response.parse()
            assert_matches_type(DatasliceGetFilesResponse, dataslice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get_metrics(self, client: Deasy) -> None:
        dataslice = client.dataslice.get_metrics()
        assert_matches_type(DatasliceGetMetricsResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_metrics_with_all_params(self, client: Deasy) -> None:
        dataslice = client.dataslice.get_metrics(
            data_connector_name="data_connector_name",
            dataslice_id="dataslice_id",
            file_names=["string"],
            node_ids=["string"],
            tags=["string"],
        )
        assert_matches_type(DatasliceGetMetricsResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_metrics(self, client: Deasy) -> None:
        response = client.dataslice.with_raw_response.get_metrics()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataslice = response.parse()
        assert_matches_type(DatasliceGetMetricsResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_metrics(self, client: Deasy) -> None:
        with client.dataslice.with_streaming_response.get_metrics() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataslice = response.parse()
            assert_matches_type(DatasliceGetMetricsResponse, dataslice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get_tag_vdb_distribution(self, client: Deasy) -> None:
        dataslice = client.dataslice.get_tag_vdb_distribution()
        assert_matches_type(DatasliceGetTagVdbDistributionResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_tag_vdb_distribution_with_all_params(self, client: Deasy) -> None:
        dataslice = client.dataslice.get_tag_vdb_distribution(
            data_connector_name="data_connector_name",
            dataslice_id="dataslice_id",
        )
        assert_matches_type(DatasliceGetTagVdbDistributionResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_tag_vdb_distribution(self, client: Deasy) -> None:
        response = client.dataslice.with_raw_response.get_tag_vdb_distribution()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataslice = response.parse()
        assert_matches_type(DatasliceGetTagVdbDistributionResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_tag_vdb_distribution(self, client: Deasy) -> None:
        with client.dataslice.with_streaming_response.get_tag_vdb_distribution() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataslice = response.parse()
            assert_matches_type(DatasliceGetTagVdbDistributionResponse, dataslice, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDataslice:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncDeasy) -> None:
        dataslice = await async_client.dataslice.create(
            data_connector_name="data_connector_name",
            dataslice_name="dataslice_name",
            graph_id="graph_id",
            latest_graph={"foo": "bar"},
        )
        assert_matches_type(DatasliceCreateResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncDeasy) -> None:
        dataslice = await async_client.dataslice.create(
            data_connector_name="data_connector_name",
            dataslice_name="dataslice_name",
            graph_id="graph_id",
            latest_graph={"foo": "bar"},
            condition={
                "children": [],
                "condition": "AND",
                "tag": {
                    "name": "name",
                    "values": ["string"],
                    "operator": "operator",
                },
            },
            data_points=0,
            description="description",
            parent_dataslice_id="parent_dataslice_id",
            status="status",
        )
        assert_matches_type(DatasliceCreateResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncDeasy) -> None:
        response = await async_client.dataslice.with_raw_response.create(
            data_connector_name="data_connector_name",
            dataslice_name="dataslice_name",
            graph_id="graph_id",
            latest_graph={"foo": "bar"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataslice = await response.parse()
        assert_matches_type(DatasliceCreateResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncDeasy) -> None:
        async with async_client.dataslice.with_streaming_response.create(
            data_connector_name="data_connector_name",
            dataslice_name="dataslice_name",
            graph_id="graph_id",
            latest_graph={"foo": "bar"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataslice = await response.parse()
            assert_matches_type(DatasliceCreateResponse, dataslice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncDeasy) -> None:
        dataslice = await async_client.dataslice.list()
        assert_matches_type(DatasliceListResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncDeasy) -> None:
        response = await async_client.dataslice.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataslice = await response.parse()
        assert_matches_type(DatasliceListResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncDeasy) -> None:
        async with async_client.dataslice.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataslice = await response.parse()
            assert_matches_type(DatasliceListResponse, dataslice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncDeasy) -> None:
        dataslice = await async_client.dataslice.delete(
            dataslice_id="dataslice_id",
        )
        assert_matches_type(DatasliceDeleteResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncDeasy) -> None:
        response = await async_client.dataslice.with_raw_response.delete(
            dataslice_id="dataslice_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataslice = await response.parse()
        assert_matches_type(DatasliceDeleteResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncDeasy) -> None:
        async with async_client.dataslice.with_streaming_response.delete(
            dataslice_id="dataslice_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataslice = await response.parse()
            assert_matches_type(DatasliceDeleteResponse, dataslice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_file_count(self, async_client: AsyncDeasy) -> None:
        dataslice = await async_client.dataslice.get_file_count(
            data_connector_name="data_connector_name",
        )
        assert_matches_type(DatasliceGetFileCountResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_file_count_with_all_params(self, async_client: AsyncDeasy) -> None:
        dataslice = await async_client.dataslice.get_file_count(
            data_connector_name="data_connector_name",
            condition={
                "children": [],
                "condition": "AND",
                "tag": {
                    "name": "name",
                    "values": ["string"],
                    "operator": "operator",
                },
            },
            dataslice_id="dataslice_id",
        )
        assert_matches_type(DatasliceGetFileCountResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_file_count(self, async_client: AsyncDeasy) -> None:
        response = await async_client.dataslice.with_raw_response.get_file_count(
            data_connector_name="data_connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataslice = await response.parse()
        assert_matches_type(DatasliceGetFileCountResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_file_count(self, async_client: AsyncDeasy) -> None:
        async with async_client.dataslice.with_streaming_response.get_file_count(
            data_connector_name="data_connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataslice = await response.parse()
            assert_matches_type(DatasliceGetFileCountResponse, dataslice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_files(self, async_client: AsyncDeasy) -> None:
        dataslice = await async_client.dataslice.get_files(
            dataslice_id="dataslice_id",
        )
        assert_matches_type(DatasliceGetFilesResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_files(self, async_client: AsyncDeasy) -> None:
        response = await async_client.dataslice.with_raw_response.get_files(
            dataslice_id="dataslice_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataslice = await response.parse()
        assert_matches_type(DatasliceGetFilesResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_files(self, async_client: AsyncDeasy) -> None:
        async with async_client.dataslice.with_streaming_response.get_files(
            dataslice_id="dataslice_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataslice = await response.parse()
            assert_matches_type(DatasliceGetFilesResponse, dataslice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_metrics(self, async_client: AsyncDeasy) -> None:
        dataslice = await async_client.dataslice.get_metrics()
        assert_matches_type(DatasliceGetMetricsResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_metrics_with_all_params(self, async_client: AsyncDeasy) -> None:
        dataslice = await async_client.dataslice.get_metrics(
            data_connector_name="data_connector_name",
            dataslice_id="dataslice_id",
            file_names=["string"],
            node_ids=["string"],
            tags=["string"],
        )
        assert_matches_type(DatasliceGetMetricsResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_metrics(self, async_client: AsyncDeasy) -> None:
        response = await async_client.dataslice.with_raw_response.get_metrics()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataslice = await response.parse()
        assert_matches_type(DatasliceGetMetricsResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_metrics(self, async_client: AsyncDeasy) -> None:
        async with async_client.dataslice.with_streaming_response.get_metrics() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataslice = await response.parse()
            assert_matches_type(DatasliceGetMetricsResponse, dataslice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_tag_vdb_distribution(self, async_client: AsyncDeasy) -> None:
        dataslice = await async_client.dataslice.get_tag_vdb_distribution()
        assert_matches_type(DatasliceGetTagVdbDistributionResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_tag_vdb_distribution_with_all_params(self, async_client: AsyncDeasy) -> None:
        dataslice = await async_client.dataslice.get_tag_vdb_distribution(
            data_connector_name="data_connector_name",
            dataslice_id="dataslice_id",
        )
        assert_matches_type(DatasliceGetTagVdbDistributionResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_tag_vdb_distribution(self, async_client: AsyncDeasy) -> None:
        response = await async_client.dataslice.with_raw_response.get_tag_vdb_distribution()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataslice = await response.parse()
        assert_matches_type(DatasliceGetTagVdbDistributionResponse, dataslice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_tag_vdb_distribution(self, async_client: AsyncDeasy) -> None:
        async with async_client.dataslice.with_streaming_response.get_tag_vdb_distribution() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataslice = await response.parse()
            assert_matches_type(DatasliceGetTagVdbDistributionResponse, dataslice, path=["response"])

        assert cast(Any, response.is_closed) is True
