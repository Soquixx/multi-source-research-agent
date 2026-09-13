import pytest

from app.core.pipeline import ResearchPipeline
from app.providers.base import SearchProvider
from app.schemas import SearchResult


class FakeSearchProvider(SearchProvider):

    def __init__(self, provider_name, results):
        self._name = provider_name
        self._results = results

    @property
    def name(self) -> str:
        return self._name

    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[SearchResult]:
        return self._results[:limit]


class FakeSynthesisProvider:

    def __init__(self):
        self.calls = 0

    @property
    def name(self) -> str:
        return "fake"

    async def synthesize(
        self,
        question,
        evidence,
        conflicts,
    ):
        self.calls += 1
        return "Grounded answer.", []


def make_result(
    title,
    url,
    provider,
    snippet,
):
    return SearchResult(
        title=title,
        url=url,
        provider=provider,
        snippet=snippet,
    )


def test_pipeline_requires_two_providers():
    with pytest.raises(
        ValueError,
        match="At least two search providers",
    ):
        ResearchPipeline(
            providers=[
                FakeSearchProvider("tavily", [])
            ],
            synthesis_provider=FakeSynthesisProvider(),
        )


@pytest.mark.asyncio
async def test_pipeline_does_not_call_llm_without_relevant_evidence():

    provider1 = FakeSearchProvider(
        "tavily",
        [
            make_result(
                "Football",
                "https://example.com/football",
                "tavily",
                "The football match ended in a draw.",
            )
        ],
    )

    provider2 = FakeSearchProvider(
        "duckduckgo",
        [],
    )

    synthesis = FakeSynthesisProvider()

    pipeline = ResearchPipeline(
        providers=[
            provider1,
            provider2,
        ],
        synthesis_provider=synthesis,
    )

    response = await pipeline.research(
        "What caused inflation?"
    )

    assert synthesis.calls == 0

    assert (
        "Insufficient"
        in response.answer
    )