import pytest

from app.providers.duckduckgo import DuckDuckGoProvider


def test_duckduckgo_provider_name():
    provider = DuckDuckGoProvider()

    assert provider.name == "duckduckgo"


@pytest.mark.asyncio
async def test_duckduckgo_empty_query_rejected():
    provider = DuckDuckGoProvider()

    with pytest.raises(ValueError):
        await provider.search("")


@pytest.mark.asyncio
async def test_duckduckgo_whitespace_query_rejected():
    provider = DuckDuckGoProvider()

    with pytest.raises(ValueError):
        await provider.search("   ")


@pytest.mark.asyncio
async def test_duckduckgo_invalid_limit_rejected():
    provider = DuckDuckGoProvider()

    with pytest.raises(ValueError):
        await provider.search("nuclear energy", limit=0)