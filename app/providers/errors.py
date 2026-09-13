class ProviderError(Exception):
    """Base exception for search provider failures."""


class ProviderTimeoutError(ProviderError):
    """Raised when a provider request times out."""


class ProviderRateLimitError(ProviderError):
    """Raised when a provider rate-limits the request."""


class ProviderAuthenticationError(ProviderError):
    """Raised when provider credentials are invalid."""


class ProviderResponseError(ProviderError):
    """Raised when a provider returns an unexpected response."""


class ProviderUnavailableError(ProviderError):
    """Raised when a provider is temporarily unavailable."""