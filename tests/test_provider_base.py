import pytest
from app.providers.base import SearchProvider
from app.schemas import SearchResult


class DummyProvider(SearchProvider):

    @property
    def name(self) -> str:
        return "dummy"

    async def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        return [
            SearchResult(
                title="Test Entry",
                url="https://example.com",
                snippet="Sample text",
                provider=self.name,
            )
        ]


def test_provider_name_contract():
    provider = DummyProvider()
    assert provider.name == "dummy"


@pytest.mark.asyncio
async def test_provider_search_contract():
    provider = DummyProvider()
    results = await provider.search(query="test request", limit=5)

    assert len(results) == 1
    assert isinstance(results[0], SearchResult)
    assert results[0].provider == "dummy"
    assert results[0].url == "https://example.com"