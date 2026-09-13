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