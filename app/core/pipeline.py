import asyncio
import logging

from app.core.retry import retry_async
from app.processing.deduplication import deduplicate_results
from app.processing.evidence import extract_evidence
from app.processing.fetching import fetch_page
from app.processing.ranking import rank_sources
from app.processing.verification import detect_conflicts, verify_evidence
from app.providers.base import SearchProvider
from app.schemas import Conflict, ResearchResponse, SearchResult, Source
from app.synthesis.base import SynthesisProvider
from app.synthesis.guard import can_synthesize

logger = logging.getLogger(__name__)


class ResearchPipeline:
    """Orchestrates multi-source research from retrieval to synthesis."""

    def __init__(
        self,
        providers: list[SearchProvider],
        synthesis_provider: SynthesisProvider,
        search_limit: int = 10,
        max_sources: int = 8,
        max_evidence: int = 12,
    ) -> None:
        if len(providers) < 2:
            raise ValueError(
                "At least two search providers are required"
            )

        self.providers = providers
        self.synthesis_provider = synthesis_provider
        self.search_limit = search_limit
        self.max_sources = max_sources
        self.max_evidence = max_evidence

    async def research(self, question: str) -> ResearchResponse:
        uncertainties: list[str] = []

        # 1. Retrieve from all providers concurrently.
        results = await self._search_all(
            question,
            uncertainties,
        )

        if not results:
            return self._insufficient_response(
                [],
                uncertainties,
                "No search results were retrieved.",
            )

        # 2. Deduplicate using canonical URLs.
        sources = deduplicate_results(results)

        # 3. Deterministic relevance + quality ranking.
        sources = rank_sources(
            sources,
            question,
        )

        sources = sources[: self.max_sources]

        # 4. Fetch source content concurrently.
        await self._fetch_sources(sources, uncertainties)

        # 5. Extract deterministic evidence.
        evidence = []

        for source in sources:
            if not source.fetch_success:
                continue

            evidence.extend(
                extract_evidence(
                    source,
                    max_evidence=self.max_evidence,
                )
            )

        evidence = evidence[: self.max_evidence]

        # 6. Deterministic evidence verification.
        relevant_evidence, verification_uncertainties = (
            verify_evidence(
                question,
                evidence,
                sources,
            )
        )

        uncertainties.extend(
            verification_uncertainties
        )

        # 7. HARD GUARD:
        # No evidence = no LLM call.
        if not can_synthesize(relevant_evidence):
            return self._insufficient_response(
                sources,
                uncertainties,
                "No sufficiently relevant evidence was found.",
            )

        # 8. Detect conservative conflicts.
        conflicts = detect_conflicts(
            relevant_evidence
        )

        # 9. Exactly ONE LLM synthesis call.
        answer, claims = (
            await self.synthesis_provider.synthesize(
                question=question,
                evidence=relevant_evidence,
                conflicts=conflicts,
            )
        )

        conflict_models = [
            Conflict(
                description=(
                    f"Evidence {first.evidence_id} "
                    f"and {second.evidence_id} "
                    "may conflict."
                ),
                source_ids=[
                    first.source_id,
                    second.source_id,
                ],
            )
            for first, second in conflicts
        ]

        return ResearchResponse(
            answer=answer,
            claims=claims,
            sources=sources,
            conflicts=conflict_models,
            uncertainties=uncertainties,
        )

    async def _search_all(
        self,
        question: str,
        uncertainties: list[str],
    ) -> list[SearchResult]:

        async def search_provider(
            provider: SearchProvider,
        ) -> list[SearchResult]:

            try:
                return await retry_async(
                    lambda: provider.search(
                        question,
                        limit=self.search_limit,
                    )
                )

            except Exception as exc:
                logger.warning("Provider %s search failed: %s", provider.name, exc)
                uncertainties.append(
                    f"Search provider '{provider.name}' was temporarily unavailable."
                )
                return []

        provider_results = await asyncio.gather(
            *(
                search_provider(provider)
                for provider in self.providers
            )
        )

        return [
            result
            for results in provider_results
            for result in results
        ]

    async def _fetch_sources(
        self,
        sources: list[Source],
        uncertainties: list[str],
    ) -> None:

        async def fetch_source(
            source: Source,
        ) -> None:

            try:
                source.content = await retry_async(
                    lambda: fetch_page(source.url)
                )
                source.fetch_success = True

            except Exception as exc:
                source.fetch_success = False
                logger.info("Failed to fetch full page content for %s: %s", source.url, exc)

        await asyncio.gather(
            *(
                fetch_source(source)
                for source in sources
            )
        )

        # Summarize fetch failures instead of exposing raw exception strings
        failed_count = sum(1 for s in sources if not s.fetch_success)
        if failed_count > 0:
            uncertainties.append(
                f"Full page content could not be retrieved for {failed_count} source(s); analysis relied on available search snippets."
            )

    @staticmethod
    def _insufficient_response(
        sources: list[Source],
        uncertainties: list[str],
        reason: str,
    ) -> ResearchResponse:

        return ResearchResponse(
            answer=(
                "Insufficient reliable evidence was "
                "retrieved to answer this question."
            ),
            sources=sources,
            uncertainties=[
                *uncertainties,
                reason,
            ],
        )