import pytest
from unittest.mock import AsyncMock

from httpx import Response
from app.providers.errors import (
    ProviderAuthenticationError,
    ProviderResponseError,
)
from app.providers.tavily import TavilyProvider
from app.schemas import SearchResult


@pytest.mark.asyncio
async def test_tavily_search_success():
    mock_client = AsyncMock()

    mock_client.post.return_value = Response(
        200,
        json={
            "results": [
                {
                    "title": "Test Title",
                    "url": "https://example.com",
                    "content": "Sample text",
                }
            ]
        },
    )

    provider = TavilyProvider(
        api_key="test_key",
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
    assert results[0].snippet == "Sample text"
    assert results[0].provider == "tavily"

    mock_client.post.assert_awaited_once()

    _, kwargs = mock_client.post.call_args

    assert kwargs["json"]["query"] == "test query"
    assert kwargs["json"]["max_results"] == 1
    assert kwargs["json"]["include_answer"] is False
    assert kwargs["json"]["include_raw_content"] is False
    assert kwargs["json"]["include_images"] is False


@pytest.mark.asyncio
async def test_tavily_auth_error():
    mock_client = AsyncMock()

    mock_client.post.return_value = Response(401)

    provider = TavilyProvider(
        api_key="bad_key",
        client=mock_client,
    )

    with pytest.raises(ProviderAuthenticationError):
        await provider.search("test query")


@pytest.mark.asyncio
async def test_tavily_empty_query_rejected():
    mock_client = AsyncMock()

    provider = TavilyProvider(
        api_key="test_key",
        client=mock_client,
    )

    with pytest.raises(ValueError):
        await provider.search("   ")

    mock_client.post.assert_not_awaited()


@pytest.mark.asyncio
async def test_tavily_invalid_response_rejected():
    mock_client = AsyncMock()

    mock_client.post.return_value = Response(
        200,
        json={
            "results": "not-a-list"
        },
    )

    provider = TavilyProvider(
        api_key="test_key",
        client=mock_client,
    )

    from app.providers.errors import ProviderResponseError

    with pytest.raises(ProviderResponseError):
        await provider.search("test query")