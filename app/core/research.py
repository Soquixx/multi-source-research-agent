from collections.abc import Sequence

from app.processing.deduplication import deduplicate_results
from app.processing.evidence import extract_evidence
from app.processing.fetching import fetch_page
from app.processing.ranking import rank_sources
from app.providers.base import SearchProvider
from app.schemas import Evidence, Source


DEFAULT_RESULTS_PER_PROVIDER = 10
DEFAULT_SOURCES_TO_FETCH = 5


class ResearchPipeline:
    """
    Coordinates retrieval and evidence preparation.
    """

    def __init__(
        self,
        providers: Sequence[SearchProvider],
        results_per_provider: int = DEFAULT_RESULTS_PER_PROVIDER,
        sources_to_fetch: int = DEFAULT_SOURCES_TO_FETCH,
    ) -> None:
        if not providers:
            raise ValueError("At least one search provider is required")

        if results_per_provider < 1:
            raise ValueError("results_per_provider must be at least 1")

        if sources_to_fetch < 1:
            raise ValueError("sources_to_fetch must be at least 1")

        self.providers = list(providers)
        self.results_per_provider = results_per_provider
        self.sources_to_fetch = sources_to_fetch

    async def retrieve(self, question: str) -> list[Source]:
        """
        Search all providers, isolate provider failures, then normalize,
        deduplicate, and rank the combined results.
        """
        results = []

        for provider in self.providers:
            try:
                provider_results = await provider.search(
                    question,
                    limit=self.results_per_provider,
                )
            except Exception:
                # A failed provider must not prevent other providers
                # from contributing evidence.
                continue

            results.extend(provider_results)

        if not results:
            return []

        sources = deduplicate_results(results)

        return rank_sources(
            sources,
            question,
        )

    async def collect_evidence(
        self,
        question: str,
    ) -> tuple[list[Source], list[Evidence]]:
        """
        Retrieve and fetch the highest-ranked sources.
        """

        sources = await self.retrieve(question)

        evidence: list[Evidence] = []

        for source in sources[: self.sources_to_fetch]:
            try:
                source.content = await fetch_page(source.url)
                source.fetch_success = True
            except Exception:
                source.fetch_success = False
                continue

            evidence.extend(
                extract_evidence(source)
            )

        return sources, evidence