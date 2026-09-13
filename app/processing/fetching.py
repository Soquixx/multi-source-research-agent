import httpx
from bs4 import BeautifulSoup

from app.providers.errors import (
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)

DEFAULT_TIMEOUT = 10.0
MAX_CONTENT_LENGTH = 2_000_000


async def fetch_page(
    url: str,
    timeout: float = DEFAULT_TIMEOUT,
    client: httpx.AsyncClient | None = None,
) -> str:
    """
    Fetch an HTML page and return readable text.

    The function deliberately does not use an LLM.
    """

    if not url.strip():
        raise ValueError("URL cannot be empty")

    http_client = client or httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        headers={
            "User-Agent": (
                "MultiSourceResearchAgent/1.0 "
                "(research-purpose)"
            )
        },
    )

    should_close = client is None

    try:
        try:
            response = await http_client.get(url)

        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError(
                "Source fetch timed out"
            ) from exc

        except httpx.RequestError as exc:
            raise ProviderUnavailableError(
                "Source fetch failed"
            ) from exc

    finally:
        if should_close:
            await http_client.aclose()

    if response.status_code >= 500:
        raise ProviderUnavailableError(
            f"Source server error: {response.status_code}"
        )

    if response.status_code >= 400:
        raise ProviderResponseError(
            f"Source returned HTTP {response.status_code}"
        )

    content_type = response.headers.get(
        "content-type",
        "",
    ).lower()

    if "text/html" not in content_type:
        raise ProviderResponseError(
            "Source is not an HTML page"
        )

    if len(response.content) > MAX_CONTENT_LENGTH:
        raise ProviderResponseError(
            "Source content exceeds maximum allowed size"
        )

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    for element in soup(
        ["script", "style", "noscript", "nav", "footer"]
    ):
        element.decompose()

    text = soup.get_text(
        separator=" ",
        strip=True,
    )

    if not text:
        raise ProviderResponseError(
            "Source page contains no readable text"
        )

    return text