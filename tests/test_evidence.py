from app.processing.evidence import extract_evidence
from app.schemas import Source

def make_source(content: str | None) -> Source:
    return Source(
        source_id="src_123",
        title="Test Source",
        url="https://example.com/article",
        providers=["tavily"],
        content=content,
    )


def test_extracts_evidence_from_content():
    source = make_source(
        "Climate change affects agricultural production. "
        "Changes in temperature and rainfall can reduce crop yields. "
        "Farmers may need to adapt their practices."
    )

    evidence = extract_evidence(
        source,
        min_length=20,
    )

    assert len(evidence) == 3
    assert evidence[0].source_id == "src_123"
    assert "Climate change affects" in evidence[0].text


def test_no_content_returns_empty_list():
    source = make_source(None)

    assert extract_evidence(source) == []


def test_empty_content_returns_empty_list():
    source = make_source("")

    assert extract_evidence(source) == []


def test_short_text_is_filtered():
    source = make_source(
        "Too short. "
        "This is sufficiently long evidence that should remain."
    )

    evidence = extract_evidence(
        source,
        min_length=20,
    )

    assert len(evidence) == 1
    assert "sufficiently long" in evidence[0].text


def test_max_evidence_is_respected():
    source = make_source(
        "This is the first sufficiently long evidence sentence. "
        "This is the second sufficiently long evidence sentence. "
        "This is the third sufficiently long evidence sentence."
    )

    evidence = extract_evidence(
        source,
        max_evidence=2,
        min_length=20,
    )

    assert len(evidence) == 2


def test_evidence_ids_are_deterministic():
    source = make_source(
        "This is sufficiently long evidence text for testing."
    )

    first = extract_evidence(
        source,
        min_length=20,
    )

    second = extract_evidence(
        source,
        min_length=20,
    )

    assert first[0].evidence_id == second[0].evidence_id


def test_evidence_preserves_source_text():
    original = (
        "According to the report, agricultural production "
        "increased by 25 percent during the study period."
    )

    source = make_source(original)

    evidence = extract_evidence(
        source,
        min_length=20,
    )

    assert evidence[0].text == original