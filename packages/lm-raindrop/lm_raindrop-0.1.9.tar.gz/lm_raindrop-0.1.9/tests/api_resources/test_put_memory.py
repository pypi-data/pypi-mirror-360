# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from raindrop import Raindrop, AsyncRaindrop
from tests.utils import assert_matches_type
from raindrop.types import PutMemoryCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPutMemory:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Raindrop) -> None:
        put_memory = client.put_memory.create(
            agent_memory_location={"agent_memory": {"name": "memory-name"}},
            content="User prefers dark theme for the interface",
            session_id="01jxanr45haeswhay4n0q8340y",
        )
        assert_matches_type(PutMemoryCreateResponse, put_memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Raindrop) -> None:
        put_memory = client.put_memory.create(
            agent_memory_location={
                "agent_memory": {
                    "name": "memory-name",
                    "application_name": "my-app",
                    "version": "1234",
                }
            },
            content="User prefers dark theme for the interface",
            session_id="01jxanr45haeswhay4n0q8340y",
            agent="assistant-v1",
            key="user-preference-theme",
            timeline="user-conversation-2024",
        )
        assert_matches_type(PutMemoryCreateResponse, put_memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Raindrop) -> None:
        response = client.put_memory.with_raw_response.create(
            agent_memory_location={"agent_memory": {"name": "memory-name"}},
            content="User prefers dark theme for the interface",
            session_id="01jxanr45haeswhay4n0q8340y",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        put_memory = response.parse()
        assert_matches_type(PutMemoryCreateResponse, put_memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Raindrop) -> None:
        with client.put_memory.with_streaming_response.create(
            agent_memory_location={"agent_memory": {"name": "memory-name"}},
            content="User prefers dark theme for the interface",
            session_id="01jxanr45haeswhay4n0q8340y",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            put_memory = response.parse()
            assert_matches_type(PutMemoryCreateResponse, put_memory, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPutMemory:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncRaindrop) -> None:
        put_memory = await async_client.put_memory.create(
            agent_memory_location={"agent_memory": {"name": "memory-name"}},
            content="User prefers dark theme for the interface",
            session_id="01jxanr45haeswhay4n0q8340y",
        )
        assert_matches_type(PutMemoryCreateResponse, put_memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncRaindrop) -> None:
        put_memory = await async_client.put_memory.create(
            agent_memory_location={
                "agent_memory": {
                    "name": "memory-name",
                    "application_name": "my-app",
                    "version": "1234",
                }
            },
            content="User prefers dark theme for the interface",
            session_id="01jxanr45haeswhay4n0q8340y",
            agent="assistant-v1",
            key="user-preference-theme",
            timeline="user-conversation-2024",
        )
        assert_matches_type(PutMemoryCreateResponse, put_memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncRaindrop) -> None:
        response = await async_client.put_memory.with_raw_response.create(
            agent_memory_location={"agent_memory": {"name": "memory-name"}},
            content="User prefers dark theme for the interface",
            session_id="01jxanr45haeswhay4n0q8340y",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        put_memory = await response.parse()
        assert_matches_type(PutMemoryCreateResponse, put_memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncRaindrop) -> None:
        async with async_client.put_memory.with_streaming_response.create(
            agent_memory_location={"agent_memory": {"name": "memory-name"}},
            content="User prefers dark theme for the interface",
            session_id="01jxanr45haeswhay4n0q8340y",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            put_memory = await response.parse()
            assert_matches_type(PutMemoryCreateResponse, put_memory, path=["response"])

        assert cast(Any, response.is_closed) is True
