from collections.abc import Sequence

from app.core.results import (FetchFailure, ProviderFailure, ResearchData)
from app.processing.deduplication import deduplicate_results
from app.processing.evidence import extract_evidence
from app.processing.fetching import fetch_page
from app.processing.ranking import rank_sources
from app.processing.verification import (detect_conflicts,verify_evidence,)
from app.providers.base import SearchProvider
from app.schemas import SearchResult



DEFAULT_RESULTS_PER_PROVIDER = 10
DEFAULT_SOURCES_TO_FETCH = 5


class ResearchPipeline:
    """Coordinates retrieval and evidence preparation."""

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

    async def retrieve(self, question: str) -> ResearchData:
        results: list[SearchResult] = []
        failures: list[ProviderFailure] = []

        for provider in self.providers:
            try:
                provider_results = await provider.search(
                    question,
                    limit=self.results_per_provider,
                )
                results.extend(provider_results)

            except Exception as exc:
                failures.append(
                    ProviderFailure(
                        provider=provider.name,
                        error_type=type(exc).__name__,
                        message=str(exc),
                    )
                )

        if not results:
            return ResearchData(
                provider_failures=failures,
            )

        sources = deduplicate_results(results)

        ranked_sources = rank_sources(
            sources,
            question,
        )

        return ResearchData(
            sources=ranked_sources,
            provider_failures=failures,
        )

    async def collect_evidence(
        self,
        question: str,
    ) -> ResearchData:
        data = await self.retrieve(question)

        evidence = []

        for source in data.sources[: self.sources_to_fetch]:
            try:
                source.content = await fetch_page(source.url)
                source.fetch_success = True

                evidence.extend(
                    extract_evidence(source)
                )

            except Exception as exc:
                source.fetch_success = False

                data.fetch_failures.append(
                    FetchFailure(
                        url=source.url,
                        error_type=type(exc).__name__,
                        message=str(exc),
                    )
                )

        data.evidence = evidence

        relevant_evidence , uncertainties = verify_evidence(
            question,
            evidence,
            data.sources
        )

        data.relevant_evidence = relevant_evidence
        data.uncertainties.extend(uncertainties)
        data.conflicts = detect_conflicts(relevant_evidence)

        return data