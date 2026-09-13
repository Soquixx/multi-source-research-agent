from app.processing.normalization import normalize_url
from app.schemas import SearchResult, Source


def deduplicate_results(
    results: list[SearchResult],
) -> list[Source]:
    """
    Deduplicate search results using canonical URLs.

    When multiple providers discover the same source, their provider
    names are merged rather than creating duplicate Source objects.
    """

    sources_by_url: dict[str, Source] = {}

    for result in results:
        canonical_url = normalize_url(result.url)

        if not canonical_url:
            continue

        existing = sources_by_url.get(canonical_url)

        if existing is None:
            sources_by_url[canonical_url] = Source(
                source_id=_generate_source_id(canonical_url),
                title=result.title,
                url=result.url,
                providers=[result.provider],
                snippet=result.snippet,
                published_at=result.published_at,
            )
            continue

        if result.provider not in existing.providers:
            existing.providers.append(result.provider)

        # Prefer a non-empty snippet if the existing one is empty.
        if not existing.snippet and result.snippet:
            existing.snippet = result.snippet

        if existing.published_at is None and result.published_at is not None:
            existing.published_at = result.published_at

    return list(sources_by_url.values())


def _generate_source_id(canonical_url: str) -> str:
    """Generate a deterministic source ID from the canonical URL."""

    import hashlib

    digest = hashlib.sha256(
        canonical_url.encode("utf-8")
    ).hexdigest()[:12]

    return f"src_{digest}"