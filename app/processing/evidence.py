import hashlib

from app.schemas import Evidence, Source


def extract_evidence(
    source: Source,
    max_evidence: int = 5,
    min_length: int = 40,
) -> list[Evidence]:
    """
    Extract deterministic evidence chunks from fetched source content.
    Text is preserved from the source rather than
    rewritten, so downstream claims can be traced back to source text.
    """

    if not source.content:
        return []

    if max_evidence < 1:
        raise ValueError("max_evidence must be at least 1")

    paragraphs = [
        " ".join(paragraph.split())
        for paragraph in source.content.split("\n")
        if paragraph.strip()
    ]

    # If fetching produced one continuous block, split it into sentences.
    if len(paragraphs) == 1:
        paragraphs = _split_sentences(paragraphs[0])

    evidence: list[Evidence] = []

    for text in paragraphs:
        if len(text) < min_length:
            continue

        evidence_id = _generate_evidence_id(
            source.source_id,
            text,
        )

        evidence.append(
            Evidence(
                evidence_id=evidence_id,
                source_id=source.source_id,
                text=text,
            )
        )

        if len(evidence) >= max_evidence:
            break

    return evidence

def _split_sentences(text: str) -> list[str]:
    """Split text into sentences while preserving source text."""
    import re

    return [
        match.group().strip()
        for match in re.finditer(
            r"[^.!?]+[.!?]|[^.!?]+$",
            text,
        )
        if match.group().strip()
    ]


def _generate_evidence_id(
    source_id: str,
    text: str,
) -> str:
    digest = hashlib.sha256(
        f"{source_id}:{text}".encode("utf-8")
    ).hexdigest()[:12]

    return f"ev_{digest}"