import httpx
import pytest
from unittest.mock import AsyncMock

from app.processing.fetching import fetch_page
from app.providers.errors import (
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)


@pytest.mark.asyncio
async def test_fetch_html_success():
    client = AsyncMock()

    client.get.return_value = httpx.Response(
        200,
        headers={"content-type": "text/html"},
        text="""
            <html>
                <head>
                    <script>ignore this</script>
                </head>
                <body>
                    <h1>Research Article</h1>
                    <p>Important evidence.</p>
                </body>
            </html>
        """,
    )

    result = await fetch_page(
        "https://example.com/article",
        client=client,
    )

    assert "Research Article" in result
    assert "Important evidence." in result
    assert "ignore this" not in result

    client.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_rejects_non_html():
    client = AsyncMock()

    client.get.return_value = httpx.Response(
        200,
        headers={"content-type": "application/pdf"},
        content=b"PDF content",
    )

    with pytest.raises(ProviderResponseError):
        await fetch_page(
            "https://example.com/file.pdf",
            client=client,
        )


@pytest.mark.asyncio
async def test_fetch_handles_timeout():
    client = AsyncMock()

    client.get.side_effect = httpx.TimeoutException(
        "timeout"
    )

    with pytest.raises(ProviderTimeoutError):
        await fetch_page(
            "https://example.com",
            client=client,
        )


@pytest.mark.asyncio
async def test_fetch_handles_server_error():
    client = AsyncMock()

    client.get.return_value = httpx.Response(503)

    with pytest.raises(ProviderUnavailableError):
        await fetch_page(
            "https://example.com",
            client=client,
        )


@pytest.mark.asyncio
async def test_fetch_handles_client_error():
    client = AsyncMock()

    client.get.return_value = httpx.Response(404)

    with pytest.raises(ProviderResponseError):
        await fetch_page(
            "https://example.com/missing",
            client=client,
        )


@pytest.mark.asyncio
async def test_empty_url_rejected():
    client = AsyncMock()

    with pytest.raises(ValueError):
        await fetch_page(
            "   ",
            client=client,
        )

    client.get.assert_not_awaited()


@pytest.mark.asyncio
async def test_empty_page_rejected():
    client = AsyncMock()

    client.get.return_value = httpx.Response(
        200,
        headers={"content-type": "text/html"},
        text="<html><body></body></html>",
    )

    with pytest.raises(ProviderResponseError):
        await fetch_page(
            "https://example.com",
            client=client,
        )