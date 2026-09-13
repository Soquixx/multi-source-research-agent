import asyncio

from ddgs import DDGS

from app.providers.base import SearchProvider
from app.providers.errors import (
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from app.schemas import SearchResult


class DuckDuckGoProvider(SearchProvider):
    """Search provider backed by DuckDuckGo."""

    def __init__(self, timeout: float = 10.0) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be greater than 0")

        self.timeout = timeout

    @property
    def name(self) -> str:
        return "duckduckgo"

    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[SearchResult]:

        if not query.strip():
            raise ValueError("Search query cannot be empty")

        if limit < 1:
            raise ValueError("limit must be at least 1")

        try:
            results = await asyncio.to_thread(
                lambda: list(
                    DDGS().text(
                        query,
                        max_results=limit,
                    )
                )
            )

        except TimeoutError as exc:
            raise ProviderTimeoutError(
                "DuckDuckGo request timed out"
            ) from exc

        except Exception as exc:
            raise ProviderUnavailableError(
                "DuckDuckGo request failed"
            ) from exc

        if not isinstance(results, list):
            raise ProviderResponseError(
                "DuckDuckGo returned an invalid response"
            )

        search_results: list[SearchResult] = []

        for item in results[:limit]:
            if not isinstance(item, dict):
                continue

            title = item.get("title")
            url = item.get("href")
            snippet = item.get("body", "")

            if not title or not url:
                continue

            search_results.append(
                SearchResult(
                    title=str(title),
                    url=str(url),
                    snippet=str(snippet),
                    provider=self.name,
                )
            )

        return search_results