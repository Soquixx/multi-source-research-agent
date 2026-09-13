import httpx
import pytest
from unittest.mock import AsyncMock

from httpx import Response

from app.providers.errors import (
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from app.providers.searxng import SearXNGProvider
from app.schemas import SearchResult


@pytest.mark.asyncio
async def test_searxng_search_success():
    mock_client = AsyncMock()

    mock_client.get.return_value = Response(
        200,
        json={
            "results": [
                {
                    "title": "Test Title",
                    "url": "https://example.com",
                    "content": "Sample search result",
                }
            ]
        },
    )

    provider = SearXNGProvider(
        base_url="http://localhost:8080",
        client=mock_client,
    )

    results = await provider.search(
        "test query",
        limit=1,
    )

    assert len(results) == 1
    assert isinstance(results[0], SearchResult)

    assert results[0].title == "Test Title"
    assert results[0].url == "https://example.com"
    assert results[0].snippet == "Sample search result"
    assert results[0].provider == "searxng"

    mock_client.get.assert_awaited_once()

    _, kwargs = mock_client.get.call_args

    assert kwargs["params"]["q"] == "test query"
    assert kwargs["params"]["format"] == "json"
    assert kwargs["params"]["categories"] == "general"


@pytest.mark.asyncio
async def test_searxng_rate_limit_error():
    mock_client = AsyncMock()

    mock_client.get.return_value = Response(429)

    provider = SearXNGProvider(
        base_url="http://localhost:8080",
        client=mock_client,
    )

    with pytest.raises(ProviderRateLimitError):
        await provider.search("test query")


@pytest.mark.asyncio
async def test_searxng_server_error():
    mock_client = AsyncMock()

    mock_client.get.return_value = Response(503)

    provider = SearXNGProvider(
        base_url="http://localhost:8080",
        client=mock_client,
    )

    with pytest.raises(ProviderUnavailableError):
        await provider.search("test query")


@pytest.mark.asyncio
async def test_searxng_invalid_response():
    mock_client = AsyncMock()

    mock_client.get.return_value = Response(
        200,
        json={
            "results": "invalid",
        },
    )

    provider = SearXNGProvider(
        base_url="http://localhost:8080",
        client=mock_client,
    )

    with pytest.raises(ProviderResponseError):
        await provider.search("test query")


@pytest.mark.asyncio
async def test_searxng_empty_query_rejected():
    mock_client = AsyncMock()

    provider = SearXNGProvider(
        base_url="http://localhost:8080",
        client=mock_client,
    )

    with pytest.raises(ValueError):
        await provider.search("   ")

    mock_client.get.assert_not_awaited()


@pytest.mark.asyncio
async def test_searxng_timeout():
    mock_client = AsyncMock()

    mock_client.get.side_effect = httpx.TimeoutException(
        "timeout"
    )

    provider = SearXNGProvider(
        base_url="http://localhost:8080",
        client=mock_client,
    )

    with pytest.raises(ProviderTimeoutError):
        await provider.search("test query")