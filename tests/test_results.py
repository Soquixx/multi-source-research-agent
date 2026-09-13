from app.core.results import ProviderFailure, ResearchData


def test_provider_failure():
    failure = ProviderFailure(
        provider="tavily",
        error_type="ProviderTimeoutError",
        message="request timed out",
    )

    assert failure.provider == "tavily"
    assert failure.error_type == "ProviderTimeoutError"


def test_research_data_defaults():
    data = ResearchData()

    assert data.sources == []
    assert data.evidence == []
    assert data.provider_failures == []

def test_fetch_failure():
    from app.core.results import FetchFailure

    failure = FetchFailure(
        url="https://example.com/article",
        error_type="ProviderTimeoutError",
        message="request timed out",
    )

    assert failure.url == "https://example.com/article"
    assert failure.error_type == "ProviderTimeoutError"

def test_research_data_tracks_fetch_failures():
    from app.core.results import FetchFailure

    data = ResearchData(
        fetch_failures=[
            FetchFailure(
                url="https://example.com",
                error_type="ProviderResponseError",
                message="404",
            )
        ]
    )

    assert len(data.fetch_failures) == 1        