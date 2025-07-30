# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deasy_client import Deasy, AsyncDeasy
from deasy_client.types import DocumentTextGetResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDocumentText:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get(self, client: Deasy) -> None:
        document_text = client.document_text.get(
            data_connector_name="data_connector_name",
            file_names=["string"],
        )
        assert_matches_type(DocumentTextGetResponse, document_text, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_with_all_params(self, client: Deasy) -> None:
        document_text = client.document_text.get(
            data_connector_name="data_connector_name",
            file_names=["string"],
            chunk_ids=["string"],
        )
        assert_matches_type(DocumentTextGetResponse, document_text, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get(self, client: Deasy) -> None:
        response = client.document_text.with_raw_response.get(
            data_connector_name="data_connector_name",
            file_names=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document_text = response.parse()
        assert_matches_type(DocumentTextGetResponse, document_text, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get(self, client: Deasy) -> None:
        with client.document_text.with_streaming_response.get(
            data_connector_name="data_connector_name",
            file_names=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document_text = response.parse()
            assert_matches_type(DocumentTextGetResponse, document_text, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDocumentText:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get(self, async_client: AsyncDeasy) -> None:
        document_text = await async_client.document_text.get(
            data_connector_name="data_connector_name",
            file_names=["string"],
        )
        assert_matches_type(DocumentTextGetResponse, document_text, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncDeasy) -> None:
        document_text = await async_client.document_text.get(
            data_connector_name="data_connector_name",
            file_names=["string"],
            chunk_ids=["string"],
        )
        assert_matches_type(DocumentTextGetResponse, document_text, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncDeasy) -> None:
        response = await async_client.document_text.with_raw_response.get(
            data_connector_name="data_connector_name",
            file_names=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document_text = await response.parse()
        assert_matches_type(DocumentTextGetResponse, document_text, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncDeasy) -> None:
        async with async_client.document_text.with_streaming_response.get(
            data_connector_name="data_connector_name",
            file_names=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document_text = await response.parse()
            assert_matches_type(DocumentTextGetResponse, document_text, path=["response"])

        assert cast(Any, response.is_closed) is True
