from app.processing.verification import (
    detect_conflicts,
    verify_evidence,
)
from app.schemas import Evidence, Source


def make_source(
    source_id: str,
    provider: str = "tavily",
) -> Source:
    return Source(
        source_id=source_id,
        title=f"Source {source_id}",
        url=f"https://example.com/{source_id}",
        providers=[provider],
    )


def make_evidence(
    evidence_id: str,
    source_id: str,
    text: str,
) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        source_id=source_id,
        text=text,
    )


def test_relevant_evidence_is_selected():
    sources = [
        make_source("src1"),
        make_source("src2", "duckduckgo"),
    ]

    evidence = [
        make_evidence(
            "ev1",
            "src1",
            "Solar energy production increased by 25 percent.",
        ),
        make_evidence(
            "ev2",
            "src2",
            "The weather was unusually cold yesterday.",
        ),
    ]

    relevant, uncertainties = verify_evidence(
        "How much did solar energy production increase?",
        evidence,
        sources,
    )

    assert len(relevant) == 1
    assert relevant[0].evidence_id == "ev1"
    assert uncertainties == [
        "The relevant evidence comes from only one source."
    ]


def test_multiple_sources_reduce_single_source_uncertainty():
    sources = [
        make_source("src1"),
        make_source("src2", "duckduckgo"),
    ]

    evidence = [
        make_evidence(
            "ev1",
            "src1",
            "Solar energy production increased significantly.",
        ),
        make_evidence(
            "ev2",
            "src2",
            "Solar energy production increased during the year.",
        ),
    ]

    relevant, uncertainties = verify_evidence(
        "What happened to solar energy production?",
        evidence,
        sources,
    )

    assert len(relevant) == 2
    assert uncertainties == []


def test_no_evidence_creates_uncertainty():
    relevant, uncertainties = verify_evidence(
        "What happened to the economy?",
        [],
        [],
    )

    assert relevant == []
    assert uncertainties == ["No evidence was retrieved."]


def test_irrelevant_evidence_is_rejected():
    sources = [make_source("src1")]

    evidence = [
        make_evidence(
            "ev1",
            "src1",
            "The football match ended in a draw.",
        )
    ]

    relevant, uncertainties = verify_evidence(
        "What caused inflation?",
        evidence,
        sources,
    )

    assert relevant == []
    assert len(uncertainties) == 1


def test_empty_question_is_rejected():
    try:
        verify_evidence("", [], [])
    except ValueError as exc:
        assert str(exc) == "Question cannot be empty"
    else:
        raise AssertionError("Expected ValueError")


def test_numeric_conflict_is_detected():
    evidence = [
        make_evidence(
            "ev1",
            "src1",
            "The population was 10 million people.",
        ),
        make_evidence(
            "ev2",
            "src2",
            "The population was 12 million people.",
        ),
    ]

    conflicts = detect_conflicts(evidence)

    assert len(conflicts) == 1
    assert conflicts[0][0].evidence_id == "ev1"
    assert conflicts[0][1].evidence_id == "ev2"


def test_different_topics_are_not_marked_as_conflict():
    evidence = [
        make_evidence(
            "ev1",
            "src1",
            "The study lasted 10 years.",
        ),
        make_evidence(
            "ev2",
            "src2",
            "The population was 12 million people.",
        ),
    ]

    conflicts = detect_conflicts(evidence)

    assert conflicts == []


def test_same_source_is_not_conflict_checked():
    evidence = [
        make_evidence(
            "ev1",
            "src1",
            "The population was 10 million people.",
        ),
        make_evidence(
            "ev2",
            "src1",
            "The population was 12 million people.",
        ),
    ]

    assert detect_conflicts(evidence) == []