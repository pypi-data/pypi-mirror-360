# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deasy_client import Deasy, AsyncDeasy
from deasy_client.types import TaskStatusTaskStatusResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTaskStatus:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_task_status(self, client: Deasy) -> None:
        task_status = client.task_status.task_status(
            job_id="job_id",
        )
        assert_matches_type(TaskStatusTaskStatusResponse, task_status, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_task_status(self, client: Deasy) -> None:
        response = client.task_status.with_raw_response.task_status(
            job_id="job_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task_status = response.parse()
        assert_matches_type(TaskStatusTaskStatusResponse, task_status, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_task_status(self, client: Deasy) -> None:
        with client.task_status.with_streaming_response.task_status(
            job_id="job_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task_status = response.parse()
            assert_matches_type(TaskStatusTaskStatusResponse, task_status, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTaskStatus:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_task_status(self, async_client: AsyncDeasy) -> None:
        task_status = await async_client.task_status.task_status(
            job_id="job_id",
        )
        assert_matches_type(TaskStatusTaskStatusResponse, task_status, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_task_status(self, async_client: AsyncDeasy) -> None:
        response = await async_client.task_status.with_raw_response.task_status(
            job_id="job_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task_status = await response.parse()
        assert_matches_type(TaskStatusTaskStatusResponse, task_status, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_task_status(self, async_client: AsyncDeasy) -> None:
        async with async_client.task_status.with_streaming_response.task_status(
            job_id="job_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task_status = await response.parse()
            assert_matches_type(TaskStatusTaskStatusResponse, task_status, path=["response"])

        assert cast(Any, response.is_closed) is True
