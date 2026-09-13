import pytest

from app.schemas import Evidence, SynthesisResult
from app.synthesis.base import SynthesisProvider
from app.synthesis.guard import can_synthesize
from app.synthesis.validation import validate_synthesis

class DummySynthesisProvider(SynthesisProvider):

    @property
    def name(self) -> str:
        return "dummy"

    async def synthesize(
        self,
        question: str,
        evidence: list[Evidence],
        conflicts: list[tuple[Evidence, Evidence]],
    ) -> tuple[str, list]:
        return "Test answer", []

def make_evidence() -> Evidence:
    return Evidence(
        evidence_id="ev1",
        source_id="src1",
        text="Test evidence",
    )

def test_synthesis_provider_name_contract():
    provider = DummySynthesisProvider()

    assert provider.name == "dummy"

@pytest.mark.asyncio
async def test_synthesis_provider_contract():
    provider = DummySynthesisProvider()

    answer, claims = await provider.synthesize(
        question="Test question",
        evidence=[make_evidence()],
        conflicts=[],
    )

    assert answer == "Test answer"
    assert claims == []

def test_synthesis_allowed_with_evidence():
    assert can_synthesize([make_evidence()]) is True

def test_synthesis_blocked_without_evidence():
    assert can_synthesize([]) is False

def test_synthesis_claim_requires_valid_evidence():
    evidence = [
        make_evidence(),
    ]

    result = SynthesisResult(
        answer="Test answer",
        claims=[
            {
                "text": "Supported claim",
                "evidence_ids": ["ev1"],
            }
        ],
    )

    validated = validate_synthesis(
        result,
        evidence,
    )

    assert validated.claims[0].evidence_ids == ["ev1"]

def test_synthesis_rejects_unknown_evidence():
    evidence = [
        make_evidence(),
    ]

    result = SynthesisResult(
        answer="Test answer",
        claims=[
            {
                "text": "Unsupported claim",
                "evidence_ids": ["ev999"],
            }
        ],
    )

    with pytest.raises(ValueError, match="unknown evidence"):
        validate_synthesis(
            result,
            evidence,
        )

def test_synthesis_rejects_claim_without_evidence():
    evidence = [
        make_evidence(),
    ]

    result = SynthesisResult(
        answer="Test answer",
        claims=[
            {
                "text": "Unsupported claim",
                "evidence_ids": [],
            }
        ],
    )

    with pytest.raises(
        ValueError,
        match="no evidence references",
    ):
        validate_synthesis(
            result,
            evidence,
        )                