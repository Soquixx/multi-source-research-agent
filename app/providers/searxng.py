import httpx

from app.providers.base import SearchProvider
from app.providers.errors import (
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from app.schemas import SearchResult


class SearXNGProvider(SearchProvider):
    """Search provider backed by a SearXNG instance."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if not base_url:
            raise ValueError("SearXNG base URL is required")

        if timeout <= 0:
            raise ValueError("timeout must be greater than 0")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = client

    @property
    def name(self) -> str:
        return "searxng"

    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[SearchResult]:
        if not query.strip():
            raise ValueError("Search query cannot be empty")

        if limit < 1:
            raise ValueError("limit must be at least 1")

        params = {
            "q": query,
            "format": "json",
            "categories": "general",
        }

        client = self._client or httpx.AsyncClient(
            timeout=self.timeout
        )
        should_close = self._client is None

        try:
            try:
                response = await client.get(
                    f"{self.base_url}/search",
                    params=params,
                )

            except httpx.TimeoutException as exc:
                raise ProviderTimeoutError(
                    "SearXNG request timed out"
                ) from exc

            except httpx.RequestError as exc:
                raise ProviderUnavailableError(
                    "SearXNG request failed"
                ) from exc

        finally:
            if should_close:
                await client.aclose()

        if response.status_code == 429:
            raise ProviderRateLimitError(
                "SearXNG rate limit reached"
            )

        if response.status_code >= 500:
            raise ProviderUnavailableError(
                f"SearXNG server error: {response.status_code}"
            )

        if response.status_code >= 400:
            raise ProviderResponseError(
                f"SearXNG request failed: {response.status_code}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise ProviderResponseError(
                "SearXNG returned invalid JSON"
            ) from exc

        raw_results = data.get("results")

        if not isinstance(raw_results, list):
            raise ProviderResponseError(
                "SearXNG response does not contain a valid results list"
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