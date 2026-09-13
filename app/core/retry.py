import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

from app.providers.errors import (
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)

T = TypeVar("T")

RETRYABLE_ERRORS = (
    ProviderTimeoutError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)


async def retry_async(
    operation: Callable[[], Awaitable[T]],
    max_attempts: int = 3,
    base_delay: float = 0.5,
) -> T:
    """
    Execute an async operation with exponential backoff and randomized jitter.

    Only explicitly retryable provider errors are retried.
    Non-retryable errors propagate immediately.
    """

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    for attempt in range(max_attempts):
        try:
            return await operation()

        except RETRYABLE_ERRORS:
            if attempt == max_attempts - 1:
                raise

            exponential_delay = base_delay * (2**attempt)

            # Full jitter spreads retries over the calculated delay window.
            jittered_delay = random.uniform(0, exponential_delay)

            await asyncio.sleep(jittered_delay)

    raise RuntimeError("Retry operation exited unexpectedly")