from urllib.parse import (
    parse_qsl,
    urlencode,
    urlsplit,
    urlunsplit,
)

TRACKING_PARAMETERS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
}

def normalize_url(url: str) -> str:
    """
    Convert a URL into a stable canonical form for comparison.

    The original URL should still be retained separately for fetching.
    """

    url = url.strip()

    if not url:
        return ""

    parsed = urlsplit(url)

    scheme = parsed.scheme.lower()
    hostname = (parsed.hostname or "").lower()

    # Preserve non-default ports.
    netloc = hostname

    if parsed.port is not None:
        is_default_port = (
            (scheme == "http" and parsed.port == 80)
            or (scheme == "https" and parsed.port == 443)
        )

        if not is_default_port:
            netloc = f"{hostname}:{parsed.port}"

    query_params = parse_qsl(
        parsed.query,
        keep_blank_values=True,
    )

    filtered_params = [
        (key, value)
        for key, value in query_params
        if key.lower() not in TRACKING_PARAMETERS
    ]

    normalized_query = urlencode(
        sorted(filtered_params)
    )

    # Treat /article/ and /article as the same path.
    path = parsed.path or "/"

    if path != "/":
        path = path.rstrip("/")

    return urlunsplit(
        (
            scheme,
            netloc,
            path,
            normalized_query,
            "",
        )
    )