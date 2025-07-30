# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deasy_client import Deasy, AsyncDeasy
from deasy_client.types import ClassifyClassifyFilesResponse
from deasy_client._utils import parse_datetime

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClassify:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_classify_files(self, client: Deasy) -> None:
        classify = client.classify.classify_files(
            data_connector_name="data_connector_name",
        )
        assert_matches_type(ClassifyClassifyFilesResponse, classify, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_classify_files_with_all_params(self, client: Deasy) -> None:
        classify = client.classify.classify_files(
            data_connector_name="data_connector_name",
            dataslice_id="dataslice_id",
            file_names=["string"],
            hierarchy_data={"foo": "bar"},
            hierarchy_name="hierarchy_name",
            job_id="job_id",
            llm_profile_name="llm_profile_name",
            overwrite=True,
            soft_run=True,
            tag_datas={
                "foo": {
                    "description": "description",
                    "name": "name",
                    "available_values": ["string"],
                    "created_at": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "date_format": "date_format",
                    "enhance_file_metadata": True,
                    "examples": ["string"],
                    "max_values": 0,
                    "neg_examples": ["string"],
                    "output_type": "output_type",
                    "retry_feedback": {"foo": "bar"},
                    "strategy": "strategy",
                    "tag_id": "tag_id",
                    "truncated_available_values": True,
                    "tuned": 0,
                    "updated_at": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "username": "username",
                }
            },
            tag_names=["string"],
        )
        assert_matches_type(ClassifyClassifyFilesResponse, classify, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_classify_files(self, client: Deasy) -> None:
        response = client.classify.with_raw_response.classify_files(
            data_connector_name="data_connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        classify = response.parse()
        assert_matches_type(ClassifyClassifyFilesResponse, classify, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_classify_files(self, client: Deasy) -> None:
        with client.classify.with_streaming_response.classify_files(
            data_connector_name="data_connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            classify = response.parse()
            assert_matches_type(ClassifyClassifyFilesResponse, classify, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncClassify:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_classify_files(self, async_client: AsyncDeasy) -> None:
        classify = await async_client.classify.classify_files(
            data_connector_name="data_connector_name",
        )
        assert_matches_type(ClassifyClassifyFilesResponse, classify, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_classify_files_with_all_params(self, async_client: AsyncDeasy) -> None:
        classify = await async_client.classify.classify_files(
            data_connector_name="data_connector_name",
            dataslice_id="dataslice_id",
            file_names=["string"],
            hierarchy_data={"foo": "bar"},
            hierarchy_name="hierarchy_name",
            job_id="job_id",
            llm_profile_name="llm_profile_name",
            overwrite=True,
            soft_run=True,
            tag_datas={
                "foo": {
                    "description": "description",
                    "name": "name",
                    "available_values": ["string"],
                    "created_at": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "date_format": "date_format",
                    "enhance_file_metadata": True,
                    "examples": ["string"],
                    "max_values": 0,
                    "neg_examples": ["string"],
                    "output_type": "output_type",
                    "retry_feedback": {"foo": "bar"},
                    "strategy": "strategy",
                    "tag_id": "tag_id",
                    "truncated_available_values": True,
                    "tuned": 0,
                    "updated_at": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "username": "username",
                }
            },
            tag_names=["string"],
        )
        assert_matches_type(ClassifyClassifyFilesResponse, classify, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_classify_files(self, async_client: AsyncDeasy) -> None:
        response = await async_client.classify.with_raw_response.classify_files(
            data_connector_name="data_connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        classify = await response.parse()
        assert_matches_type(ClassifyClassifyFilesResponse, classify, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_classify_files(self, async_client: AsyncDeasy) -> None:
        async with async_client.classify.with_streaming_response.classify_files(
            data_connector_name="data_connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            classify = await response.parse()
            assert_matches_type(ClassifyClassifyFilesResponse, classify, path=["response"])

        assert cast(Any, response.is_closed) is True
