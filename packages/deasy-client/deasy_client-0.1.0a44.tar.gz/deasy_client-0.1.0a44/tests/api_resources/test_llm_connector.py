# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deasy_client import Deasy, AsyncDeasy
from deasy_client.types import (
    ConnectorResponse,
    LlmConnectorListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLlmConnector:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Deasy) -> None:
        llm_connector = client.llm_connector.create(
            connector_body={
                "api_key": "api_key",
                "rpm_completion": 0,
                "tpm_completion": 0,
            },
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Deasy) -> None:
        llm_connector = client.llm_connector.create(
            connector_body={
                "api_key": "api_key",
                "rpm_completion": 0,
                "tpm_completion": 0,
                "llm_type": "llmType",
                "rpm_embedding": 0,
                "temperature": 0,
                "tpm_embedding": 0,
            },
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Deasy) -> None:
        response = client.llm_connector.with_raw_response.create(
            connector_body={
                "api_key": "api_key",
                "rpm_completion": 0,
                "tpm_completion": 0,
            },
            connector_name="connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        llm_connector = response.parse()
        assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Deasy) -> None:
        with client.llm_connector.with_streaming_response.create(
            connector_body={
                "api_key": "api_key",
                "rpm_completion": 0,
                "tpm_completion": 0,
            },
            connector_name="connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            llm_connector = response.parse()
            assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Deasy) -> None:
        llm_connector = client.llm_connector.update(
            connector_body={
                "api_key": "api_key",
                "rpm_completion": 0,
                "tpm_completion": 0,
            },
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Deasy) -> None:
        llm_connector = client.llm_connector.update(
            connector_body={
                "api_key": "api_key",
                "rpm_completion": 0,
                "tpm_completion": 0,
                "llm_type": "llmType",
                "rpm_embedding": 0,
                "temperature": 0,
                "tpm_embedding": 0,
            },
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Deasy) -> None:
        response = client.llm_connector.with_raw_response.update(
            connector_body={
                "api_key": "api_key",
                "rpm_completion": 0,
                "tpm_completion": 0,
            },
            connector_name="connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        llm_connector = response.parse()
        assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Deasy) -> None:
        with client.llm_connector.with_streaming_response.update(
            connector_body={
                "api_key": "api_key",
                "rpm_completion": 0,
                "tpm_completion": 0,
            },
            connector_name="connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            llm_connector = response.parse()
            assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Deasy) -> None:
        llm_connector = client.llm_connector.list()
        assert_matches_type(LlmConnectorListResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Deasy) -> None:
        response = client.llm_connector.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        llm_connector = response.parse()
        assert_matches_type(LlmConnectorListResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Deasy) -> None:
        with client.llm_connector.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            llm_connector = response.parse()
            assert_matches_type(LlmConnectorListResponse, llm_connector, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Deasy) -> None:
        llm_connector = client.llm_connector.delete(
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Deasy) -> None:
        response = client.llm_connector.with_raw_response.delete(
            connector_name="connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        llm_connector = response.parse()
        assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Deasy) -> None:
        with client.llm_connector.with_streaming_response.delete(
            connector_name="connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            llm_connector = response.parse()
            assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncLlmConnector:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncDeasy) -> None:
        llm_connector = await async_client.llm_connector.create(
            connector_body={
                "api_key": "api_key",
                "rpm_completion": 0,
                "tpm_completion": 0,
            },
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncDeasy) -> None:
        llm_connector = await async_client.llm_connector.create(
            connector_body={
                "api_key": "api_key",
                "rpm_completion": 0,
                "tpm_completion": 0,
                "llm_type": "llmType",
                "rpm_embedding": 0,
                "temperature": 0,
                "tpm_embedding": 0,
            },
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncDeasy) -> None:
        response = await async_client.llm_connector.with_raw_response.create(
            connector_body={
                "api_key": "api_key",
                "rpm_completion": 0,
                "tpm_completion": 0,
            },
            connector_name="connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        llm_connector = await response.parse()
        assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncDeasy) -> None:
        async with async_client.llm_connector.with_streaming_response.create(
            connector_body={
                "api_key": "api_key",
                "rpm_completion": 0,
                "tpm_completion": 0,
            },
            connector_name="connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            llm_connector = await response.parse()
            assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncDeasy) -> None:
        llm_connector = await async_client.llm_connector.update(
            connector_body={
                "api_key": "api_key",
                "rpm_completion": 0,
                "tpm_completion": 0,
            },
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncDeasy) -> None:
        llm_connector = await async_client.llm_connector.update(
            connector_body={
                "api_key": "api_key",
                "rpm_completion": 0,
                "tpm_completion": 0,
                "llm_type": "llmType",
                "rpm_embedding": 0,
                "temperature": 0,
                "tpm_embedding": 0,
            },
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncDeasy) -> None:
        response = await async_client.llm_connector.with_raw_response.update(
            connector_body={
                "api_key": "api_key",
                "rpm_completion": 0,
                "tpm_completion": 0,
            },
            connector_name="connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        llm_connector = await response.parse()
        assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncDeasy) -> None:
        async with async_client.llm_connector.with_streaming_response.update(
            connector_body={
                "api_key": "api_key",
                "rpm_completion": 0,
                "tpm_completion": 0,
            },
            connector_name="connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            llm_connector = await response.parse()
            assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncDeasy) -> None:
        llm_connector = await async_client.llm_connector.list()
        assert_matches_type(LlmConnectorListResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncDeasy) -> None:
        response = await async_client.llm_connector.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        llm_connector = await response.parse()
        assert_matches_type(LlmConnectorListResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncDeasy) -> None:
        async with async_client.llm_connector.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            llm_connector = await response.parse()
            assert_matches_type(LlmConnectorListResponse, llm_connector, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncDeasy) -> None:
        llm_connector = await async_client.llm_connector.delete(
            connector_name="connector_name",
        )
        assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncDeasy) -> None:
        response = await async_client.llm_connector.with_raw_response.delete(
            connector_name="connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        llm_connector = await response.parse()
        assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncDeasy) -> None:
        async with async_client.llm_connector.with_streaming_response.delete(
            connector_name="connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            llm_connector = await response.parse()
            assert_matches_type(ConnectorResponse, llm_connector, path=["response"])

        assert cast(Any, response.is_closed) is True
