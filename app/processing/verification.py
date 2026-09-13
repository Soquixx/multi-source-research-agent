from collections import defaultdict
import re

from app.schemas import Evidence, Source

_STOP_WORDS = {
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "how",
    "does",
    "did",
    "is",
    "are",
    "was",
    "were",
    "the",
    "a",
    "an",
    "of",
    "to",
    "in",
    "on",
    "for",
    "and",
    "or",
    "with",
    "from",
    "about",
}

def verify_evidence(
    question: str,
    evidence: list[Evidence],
    sources: list[Source],
) -> tuple[list[Evidence], list[str]]:
    """
    Perform deterministic evidence sufficiency checks.

    Returns:
        relevant_evidence:
            Evidence with meaningful lexical overlap with the question.

        uncertainties:
            Explicit reasons why the available evidence may be insufficient.
    """

    if not question.strip():
        raise ValueError("Question cannot be empty")

    if not evidence:
        return [], ["No evidence was retrieved."]

    source_map = {
        source.source_id: source
        for source in sources
    }

    question_terms = _keywords(question)

    relevant: list[Evidence] = []

    for item in evidence:
        evidence_terms = _keywords(item.text)

        if not question_terms:
            continue

        overlap = question_terms & evidence_terms

        if overlap:
            relevant.append(item)

    uncertainties: list[str] = []

    if not relevant:
        uncertainties.append(
            "Retrieved evidence does not contain meaningful "
            "lexical overlap with the research question."
        )
        return [], uncertainties

    source_ids = {
        item.source_id
        for item in relevant
        if item.source_id in source_map
    }

    if len(source_ids) == 1:
        uncertainties.append(
            "The relevant evidence comes from only one source."
        )

    return relevant, uncertainties

def detect_conflicts(
    evidence: list[Evidence],
) -> list[tuple[Evidence, Evidence]]:
    """
    Detect obvious numerical or polarity conflicts.

    This is intentionally conservative. It does not claim to perform
    semantic fact checking.
    """

    conflicts: list[tuple[Evidence, Evidence]] = []

    for index, first in enumerate(evidence):
        for second in evidence[index + 1:]:
            if first.source_id == second.source_id:
                continue

            if _has_numeric_conflict(first.text, second.text):
                conflicts.append((first, second))

    return conflicts

def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())

    return {
        word
        for word in words
        if len(word) > 2 and word not in _STOP_WORDS
    }

def _has_numeric_conflict(
    first: str,
    second: str,
) -> bool:
    first_numbers = set(
        re.findall(r"\b\d+(?:\.\d+)?%?\b", first)
    )

    second_numbers = set(
        re.findall(r"\b\d+(?:\.\d+)?%?\b", second)
    )

    if not first_numbers or not second_numbers:
        return False

    first_terms = _keywords(first)
    second_terms = _keywords(second)

    shared_terms = first_terms & second_terms

    return bool(shared_terms) and first_numbers != second_numbers