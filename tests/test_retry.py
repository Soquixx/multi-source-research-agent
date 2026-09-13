import pytest

from app.core.retry import retry_async
from app.providers.errors import (
    ProviderAuthenticationError,
    ProviderTimeoutError,
)

@pytest.mark.asyncio
async def test_retry_succeeds_after_temporary_failure():
    attempts = 0

    async def operation():
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            raise ProviderTimeoutError("Temporary timeout")

        return "success"

    result = await retry_async(
        operation,
        max_attempts=3,
        base_delay=0,
    )

    assert result == "success"
    assert attempts == 3


@pytest.mark.asyncio
async def test_non_retryable_error_fails_immediately():
    attempts = 0

    async def operation():
        nonlocal attempts
        attempts += 1
        raise ProviderAuthenticationError("Invalid API key")

    with pytest.raises(ProviderAuthenticationError):
        await retry_async(
            operation,
            max_attempts=3,
            base_delay=0,
        )

    assert attempts == 1


@pytest.mark.asyncio
async def test_retryable_error_is_raised_after_max_attempts():
    attempts = 0

    async def operation():
        nonlocal attempts
        attempts += 1
        raise ProviderTimeoutError("Persistent timeout")

    with pytest.raises(ProviderTimeoutError):
        await retry_async(
            operation,
            max_attempts=3,
            base_delay=0,
        )

    assert attempts == 3