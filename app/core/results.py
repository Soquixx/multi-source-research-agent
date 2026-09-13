from dataclasses import dataclass, field

from app.schemas import Evidence, Source


@dataclass
class ProviderFailure:
    provider: str
    error_type: str
    message: str

@dataclass
class FetchFailure:
    url: str
    error_type: str
    message: str

@dataclass
class ResearchData:
    sources: list[Source] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    relevant_evidence: list[Evidence] = field(default_factory=list)
    conflicts: list[tuple[Evidence, Evidence]] = field(
        default_factory=list
    )
    uncertainties: list[str] = field(default_factory=list)
    provider_failures: list[ProviderFailure] = field(
        default_factory=list
    )
    fetch_failures: list[FetchFailure] = field(
        default_factory=list
    )