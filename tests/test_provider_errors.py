from app.providers.errors import (
    ProviderError,
    ProviderTimeoutError,
    ProviderRateLimitError,
    ProviderAuthenticationError,
    ProviderResponseError,
    ProviderUnavailableError,
)


def test_provider_errors_inherit_from_base_error():
    errors = [
        ProviderTimeoutError(),
        ProviderRateLimitError(),
        ProviderAuthenticationError(),
        ProviderResponseError(),
        ProviderUnavailableError(),
    ]

    for error in errors:
        assert isinstance(error, ProviderError)
        assert isinstance(error, Exception)