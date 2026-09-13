from abc import ABC, abstractmethod

from app.schemas import Claim, Evidence

class SynthesisProvider(ABC):
    """Contract for LLM-based evidence synthesis."""

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def synthesize(
        self,
        question: str,
        evidence: list[Evidence],
        conflicts: list[tuple[Evidence, Evidence]],
    ) -> tuple[str, list[Claim]]:
        """
        Synthesize an answer strictly from supplied evidence.
        Implementations must not perform additional retrieval.
        """
        raise NotImplementedError