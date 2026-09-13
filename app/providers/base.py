from abc import ABC, abstractmethod

from app.schemas import SearchResult


class SearchProvider(ABC):
    """
    Contract that every search/retrieval provider must implement.

    Providers are responsible only for retrieving and normalizing
    search results. They must not perform LLM-based interpretation
    or synthesis.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique provider name."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[SearchResult]:
        """
        Search the provider and return normalized results.

        Args:
            query: Search query.
            limit: Maximum number of results requested.

        Returns:
            A list of normalized SearchResult objects.

        Raises:
            Provider-specific exceptions should be converted into
            controlled application-level errors by the provider layer.
        """
        pass