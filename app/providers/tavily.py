import httpx

from app.providers.base import SearchProvider
from app.providers.errors import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from app.schemas import SearchResult


class TavilyProvider(SearchProvider):
    """Search provider backed by the Tavily Search API."""

    API_URL = "https://api.tavily.com/search"

    def __init__(
        self,
        api_key: str,
        timeout: float = 10.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("Tavily API key is required")

        if timeout <= 0:
            raise ValueError("timeout must be greater than 0")

        self.api_key = api_key
        self.timeout = timeout
        self._client = client

    @property
    def name(self) -> str:
        return "tavily"

    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[SearchResult]:
        if not query.strip():
            raise ValueError("Search query cannot be empty")

        if limit < 1:
            raise ValueError("limit must be at least 1")

        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": limit,
            "search_depth": "basic",
            "include_answer": False,
            "include_raw_content": False,
            "include_images": False,
        }

        client = self._client or httpx.AsyncClient(
            timeout=self.timeout
        )
        should_close = self._client is None

        try:
            try:
                response = await client.post(
                    self.API_URL,
                    json=payload,
                )

            except httpx.TimeoutException as exc:
                raise ProviderTimeoutError(
                    "Tavily request timed out"
                ) from exc

            except httpx.RequestError as exc:
                raise ProviderUnavailableError(
                    "Tavily request failed"
                ) from exc

        finally:
            if should_close:
                await client.aclose()

        if response.status_code in (401, 403):
            raise ProviderAuthenticationError(
                "Tavily authentication or access failed"
            )

        if response.status_code == 429:
            raise ProviderRateLimitError(
                "Tavily rate limit reached"
            )

        if response.status_code >= 500:
            raise ProviderUnavailableError(
                f"Tavily server error: {response.status_code}"
            )

        if response.status_code >= 400:
            raise ProviderResponseError(
                f"Tavily request failed: {response.status_code}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise ProviderResponseError(
                "Tavily returned invalid JSON"
            ) from exc

        raw_results = data.get("results")

        if not isinstance(raw_results, list):
            raise ProviderResponseError(
                "Tavily response does not contain a valid results list"
            )

        results: list[SearchResult] = []

        for item in raw_results[:limit]:
            if not isinstance(item, dict):
                continue

            title = item.get("title")
            url = item.get("url")

            if not title or not url:
                continue

            results.append(
                SearchResult(
                    title=str(title),
                    url=str(url),
                    snippet=str(item.get("content", "")),
                    provider=self.name,
                )
            )

        return results