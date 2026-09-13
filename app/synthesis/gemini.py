import json
import os

from google import genai
from google.genai import types

from app.schemas import Claim, Evidence, SynthesisResult
from app.synthesis.base import SynthesisProvider
from app.synthesis.validation import validate_synthesis


class GeminiSynthesisProvider(SynthesisProvider):
    """Evidence-grounded synthesis using Google Gemini."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-3.6-flash",
        client=None,
    ) -> None:
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")

        if not self.api_key and client is None:
            raise ValueError("GOOGLE_API_KEY is required")

        self.model = model
        self._client = client or genai.Client(
            api_key=self.api_key
        )

    @property
    def name(self) -> str:
        return "gemini"

    async def synthesize(
        self,
        question: str,
        evidence: list[Evidence],
        conflicts: list[tuple[Evidence, Evidence]],
    ) -> tuple[str, list[Claim]]:

        if not evidence:
            raise ValueError(
                "Cannot synthesize without evidence"
            )

        evidence_text = self._format_evidence(evidence)
        conflict_text = self._format_conflicts(conflicts)

        prompt = f"""
You are an evidence-grounded research synthesizer.

Answer the user's research question using ONLY the supplied evidence.

USER QUESTION:
{question}

SUPPLIED EVIDENCE:
{evidence_text}

CONFLICTS:
{conflict_text}

Rules:
1. Do not use outside knowledge.
2. Do not invent facts.
3. Every factual claim must reference one or more supplied evidence IDs.
4. If evidence is insufficient, clearly state the limitation.
5. If sources conflict, do not silently choose one. Reflect the conflict.
6. Keep the answer concise and directly answer the question.
"""

        response = await self._client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema=SynthesisResult,
            ),
        )

        if not response.text:
            raise ValueError(
                "Gemini returned an empty response"
            )

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Gemini returned invalid JSON"
            ) from exc

        result = SynthesisResult.model_validate(data)

        result = validate_synthesis(
            result,
            evidence,
        )

        return result.answer, result.claims

    @staticmethod
    def _format_evidence(
        evidence: list[Evidence],
    ) -> str:
        return "\n\n".join(
            (
                f"[{item.evidence_id}]\n"
                f"{item.text}"
            )
            for item in evidence
        )

    @staticmethod
    def _format_conflicts(
        conflicts: list[tuple[Evidence, Evidence]],
    ) -> str:
        if not conflicts:
            return "No detected conflicts."

        return "\n\n".join(
            (
                f"- {first.evidence_id} conflicts with "
                f"{second.evidence_id}"
            )
            for first, second in conflicts
        )