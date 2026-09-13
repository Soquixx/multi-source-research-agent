from app.processing.ranking import rank_sources
from app.schemas import Source


def make_source(
    source_id: str,
    title: str,
    url: str,
    snippet: str = "",
) -> Source:
    return Source(
        source_id=source_id,
        title=title,
        url=url,
        snippet=snippet,
    )

def test_relevant_source_ranks_higher():
    sources = [
        make_source(
            "1",
            "Random Technology News",
            "https://example.com/news",
        ),
        make_source(
            "2",
            "Climate Change Effects on Agriculture",
            "https://example.com/climate",
            "Climate change affects agricultural production.",
        ),
    ]

    ranked = rank_sources(
        sources,
        "climate change agriculture",
    )

    assert ranked[0].source_id == "2"


def test_https_gets_higher_quality_than_http():
    sources = [
        make_source(
            "1",
            "Climate Change",
            "http://example.com/article",
        ),
        make_source(
            "2",
            "Climate Change",
            "https://example.com/article",
        ),
    ]

    ranked = rank_sources(
        sources,
        "climate change",
    )

    assert ranked[0].source_id == "2"


def test_government_source_gets_high_quality_score():
    sources = [
        make_source(
            "1",
            "Climate Change Report",
            "https://example.gov/report",
        ),
    ]

    ranked = rank_sources(
        sources,
        "climate change",
    )

    assert ranked[0].quality_score == 1.0


def test_scores_are_bounded():
    sources = [
        make_source(
            "1",
            "Climate Change Agriculture",
            "https://example.com/article",
            "Climate change affects agriculture.",
        ),
    ]

    ranked = rank_sources(
        sources,
        "climate change agriculture",
    )

    source = ranked[0]

    assert 0.0 <= source.relevance_score <= 1.0
    assert 0.0 <= source.quality_score <= 1.0


def test_empty_sources():
    assert rank_sources([], "some query") == []