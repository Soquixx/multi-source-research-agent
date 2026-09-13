import re
from urllib.parse import urlsplit

from app.schemas import Source

# Domains with generally strong primary/authoritative information.
TRUSTED_DOMAINS = {
    "who.int",
    "un.org",
    "worldbank.org",
    "imf.org",
    "nasa.gov",
    "nih.gov",
    "ncbi.nlm.nih.gov",
    "gov",
    "edu",
}

def _query_terms(query: str) -> set[str]:
    return {
        word.lower()
        for word in re.findall(r"[a-zA-Z0-9]+", query)
        if len(word) > 2
    }

def _relevance_score(source: Source, terms: set[str]) -> float:
    if not terms:
        return 0.0

    title = source.title.lower()
    snippet = source.snippet.lower()

    title_matches = sum(term in title for term in terms)
    snippet_matches = sum(term in snippet for term in terms)

    # Title matches are stronger evidence of relevance.
    score = (
        0.7 * (title_matches / len(terms))
        + 0.3 * (snippet_matches / len(terms))
    )

    return min(score, 1.0)

def _quality_score(source: Source) -> float:
    parsed = urlsplit(source.url)
    hostname = (parsed.hostname or "").lower()

    if parsed.scheme != "https":
        score = 0.5
    else:
        score = 0.7

    # Handle government/education domains and trusted organizations.
    if hostname.endswith(".gov") or hostname.endswith(".edu"):
        score = 1.0
    elif any(
        hostname == domain or hostname.endswith(f".{domain}")
        for domain in TRUSTED_DOMAINS
    ):
        score = 1.0

    return score


def rank_sources(
    sources: list[Source],
    query: str,
) -> list[Source]:
    """
    Score and rank sources deterministically.

    Relevance has slightly more weight than source quality because
    a highly authoritative source is still less useful if it doesn't
    address the research question.
    """

    terms = _query_terms(query)

    for source in sources:
        source.relevance_score = _relevance_score(source, terms)
        source.quality_score = _quality_score(source)

    return sorted(
        sources,
        key=lambda source: (
            0.6 * source.relevance_score
            + 0.4 * source.quality_score
        ),
        reverse=True,
    )