import pytest

from app.core.research import ResearchPipeline
from app.providers.base import SearchProvider
from app.providers.errors import ProviderTimeoutError
from app.schemas import SearchResult
from unittest.mock import AsyncMock, patch
from app.schemas import Evidence

class MockProvider(SearchProvider):
    def __init__(
        self,
        provider_name: str,
        results: list[SearchResult] | None = None,
        error: Exception | None = None,
    ):
        self.provider_name = provider_name
        self.results = results or []
        self.error = error

    @property
    def name(self) -> str:
        return self.provider_name

    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[SearchResult]:
        if self.error:
            raise self.error

        return self.results[:limit]


def result(
    title: str,
    url: str,
    provider: str,
) -> SearchResult:
    return SearchResult(
        title=title,
        url=url,
        snippet=f"Relevant information about {title}",
        provider=provider,
    )


@pytest.mark.asyncio
async def test_retrieve_combines_multiple_providers():
    tavily = MockProvider(
        "tavily",
        [
            result(
                "Climate Report",
                "https://example.com/climate",
                "tavily",
            )
        ],
    )

    searxng = MockProvider(
        "searxng",
        [
            result(
                "Agriculture Report",
                "https://example.org/agriculture",
                "searxng",
            )
        ],
    )

    pipeline = ResearchPipeline(
        [tavily, searxng],
    )

    data = await pipeline.retrieve(
        "climate agriculture",
    )

    assert len(data.sources) == 2
    assert data.provider_failures == []


@pytest.mark.asyncio
async def test_duplicate_results_are_merged():
    first = MockProvider(
        "tavily",
        [
            result(
                "Same Article",
                "https://example.com/article",
                "tavily",
            )
        ],
    )

    second = MockProvider(
        "searxng",
        [
            result(
                "Same Article",
                "https://example.com/article?utm_source=test",
                "searxng",
            )
        ],
    )

    pipeline = ResearchPipeline(
        [first, second],
    )

    data = await pipeline.retrieve(
        "same article",
    )

    assert len(data.sources) == 1
    assert data.sources[0].providers == [
        "tavily",
        "searxng",
    ]


@pytest.mark.asyncio
async def test_provider_failure_does_not_stop_pipeline():
    failing_provider = MockProvider(
        "tavily",
        error=ProviderTimeoutError(),
    )

    working_provider = MockProvider(
        "searxng",
        [
            result(
                "Working Result",
                "https://example.com/result",
                "searxng",
            )
        ],
    )

    pipeline = ResearchPipeline(
        [failing_provider, working_provider],
    )

    data = await pipeline.retrieve(
        "test query",
    )

    assert len(data.sources) == 1
    assert data.sources[0].providers == ["searxng"]

    assert len(data.provider_failures) == 1
    assert data.provider_failures[0].provider == "tavily"

@pytest.mark.asyncio
async def test_all_provider_failures_return_empty_results():
    pipeline = ResearchPipeline(
        [
            MockProvider(
                "tavily",
                error=ProviderTimeoutError(),
            ),
            MockProvider(
                "searxng",
                error=ProviderTimeoutError(),
            ),
        ],
    )

    data = await pipeline.retrieve(
        "test query",
    )

    assert data.sources == []
    assert len(data.provider_failures) == 2


@pytest.mark.asyncio
async def test_result_limit_is_passed_to_providers():
    provider = MockProvider(
        "tavily",
        [
            result(
                f"Result {i}",
                f"https://example.com/{i}",
                "tavily",
            )
            for i in range(5)
        ],
    )

    pipeline = ResearchPipeline(
        [provider],
        results_per_provider=2,
    )

    data = await pipeline.retrieve(
        "test query",
    )

    assert len(data.sources) == 2

@pytest.mark.asyncio
async def test_collect_evidence_verifies_retrieved_content():
    provider = MockProvider(
        "tavily",
        [
            result(
                "Solar Energy Report",
                "https://example.com/solar",
                "tavily",
            )
        ],
    )

    pipeline = ResearchPipeline(
        [provider],
        sources_to_fetch=1,
    )

    content = (
        "Solar energy production increased by 25 percent "
        "during the study period."
    )

    with patch(
        "app.core.research.fetch_page",
        new=AsyncMock(return_value=content),
    ):
        data = await pipeline.collect_evidence(
            "How much did solar energy production increase?"
        )

    assert len(data.evidence) == 1
    assert len(data.relevant_evidence) == 1
    assert data.relevant_evidence[0].source_id == (
        data.sources[0].source_id
    )
    assert data.fetch_failures == []

@pytest.mark.asyncio
async def test_collect_evidence_does_not_synthesize_without_evidence():
    provider = MockProvider(
        "tavily",
        [
            result(
                "Unrelated Article",
                "https://example.com/unrelated",
                "tavily",
            )
        ],
    )

    pipeline = ResearchPipeline(
        [provider],
        sources_to_fetch=1,
    )

    with patch(
        "app.core.research.fetch_page",
        new=AsyncMock(
            return_value=(
                "The football match ended in a draw "
                "after ninety minutes."
            )
        ),
    ):
        data = await pipeline.collect_evidence(
            "What caused inflation?"
        )

    assert data.evidence
    assert data.relevant_evidence == []
    assert data.uncertainties    