import pytest

from app.schemas import Evidence
from app.synthesis.base import SynthesisProvider
from app.synthesis.gemini import GeminiSynthesisProvider
from app.synthesis.guard import can_synthesize
from app.synthesis.validation import validate_synthesis
from app.schemas import SynthesisResult


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


class FakeResponse:

    def __init__(self, text: str):
        self.text = text


class FakeModels:

    def __init__(self, response: FakeResponse):
        self.response = response
        self.calls = 0

    async def generate_content(self, **kwargs):
        self.calls += 1
        return self.response


class FakeAio:

    def __init__(self, response: FakeResponse):
        self.models = FakeModels(response)


class FakeClient:

    def __init__(self, response: FakeResponse):
        self.aio = FakeAio(response)


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
    evidence = [make_evidence()]

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
    evidence = [make_evidence()]

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
    evidence = [make_evidence()]

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


@pytest.mark.asyncio
async def test_gemini_synthesis_success():
    response = FakeResponse(
        """
        {
            "answer": "Solar production increased by 25 percent.",
            "claims": [
                {
                    "text": "Solar production increased by 25 percent.",
                    "evidence_ids": ["ev1"]
                }
            ]
        }
        """
    )

    client = FakeClient(response)

    provider = GeminiSynthesisProvider(
        api_key="test-key",
        client=client,
    )

    answer, claims = await provider.synthesize(
        question="How much did solar production increase?",
        evidence=[
            Evidence(
                evidence_id="ev1",
                source_id="src1",
                text=(
                    "Solar production increased by "
                    "25 percent."
                ),
            )
        ],
        conflicts=[],
    )

    assert answer == (
        "Solar production increased by 25 percent."
    )

    assert len(claims) == 1
    assert claims[0].evidence_ids == ["ev1"]

    assert client.aio.models.calls == 1


@pytest.mark.asyncio
async def test_gemini_does_not_call_model_without_evidence():
    client = FakeClient(
        FakeResponse(
            '{"answer":"Should not happen","claims":[]}'
        )
    )

    provider = GeminiSynthesisProvider(
        api_key="test-key",
        client=client,
    )

    with pytest.raises(
        ValueError,
        match="without evidence",
    ):
        await provider.synthesize(
            question="What happened?",
            evidence=[],
            conflicts=[],
        )

    assert client.aio.models.calls == 0


@pytest.mark.asyncio
async def test_gemini_rejects_unknown_evidence_id():
    response = FakeResponse(
        """
        {
            "answer": "Unsupported answer.",
            "claims": [
                {
                    "text": "Unsupported claim.",
                    "evidence_ids": ["fake-id"]
                }
            ]
        }
        """
    )

    client = FakeClient(response)

    provider = GeminiSynthesisProvider(
        api_key="test-key",
        client=client,
    )

    with pytest.raises(
        ValueError,
        match="unknown evidence",
    ):
        await provider.synthesize(
            question="Test question",
            evidence=[make_evidence()],
            conflicts=[],
        )

    assert client.aio.models.calls == 1