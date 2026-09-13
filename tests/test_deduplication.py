from app.processing.deduplication import deduplicate_results
from app.schemas import SearchResult

def test_duplicate_urls_are_merged():
    results = [
        SearchResult(
            title="Example Article",
            url="https://example.com/article",
            snippet="First result",
            provider="tavily",
        ),
        SearchResult(
            title="Example Article",
            url="https://example.com/article?utm_source=google",
            snippet="Second result",
            provider="searxng",
        ),
    ]

    sources = deduplicate_results(results)

    assert len(sources) == 1

    source = sources[0]

    assert source.providers == ["tavily", "searxng"]
    assert source.url == "https://example.com/article"


def test_different_urls_are_not_merged():
    results = [
        SearchResult(
            title="Article One",
            url="https://example.com/article?id=1",
            provider="tavily",
        ),
        SearchResult(
            title="Article Two",
            url="https://example.com/article?id=2",
            provider="searxng",
        ),
    ]

    sources = deduplicate_results(results)

    assert len(sources) == 2


def test_empty_urls_are_ignored():
    results = [
        SearchResult(
            title="Invalid",
            url="",
            provider="tavily",
        ),
    ]

    sources = deduplicate_results(results)
    
    assert sources == []


def test_source_ids_are_deterministic():
    results = [
        SearchResult(
            title="Example",
            url="https://example.com/article",
            provider="tavily",
        ),
    ]

    first = deduplicate_results(results)
    second = deduplicate_results(results)

    assert first[0].source_id == second[0].source_id


def test_non_empty_snippet_is_preserved():
    results = [
        SearchResult(
            title="Example",
            url="https://example.com/article",
            snippet="",
            provider="tavily",
        ),
        SearchResult(
            title="Example",
            url="https://example.com/article",
            snippet="Useful content",
            provider="searxng",
        ),
    ]

    sources = deduplicate_results(results)

    assert sources[0].snippet == "Useful content"