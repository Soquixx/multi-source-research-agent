from datetime import datetime
from pydantic import BaseModel, Field

class ResearchRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        description="The research question to analyze",
    )


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str = ""
    provider: str
    published_at: datetime | None = None


class Source(BaseModel):
    source_id: str
    title: str
    url: str
    providers: list[str] = Field(default_factory=list)
    snippet: str = ""
    content: str | None = None
    published_at: datetime | None = None
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    fetch_success: bool = False


class Evidence(BaseModel):
    evidence_id: str
    source_id: str
    text: str
    location: str | None = None

class Claim(BaseModel):
    text: str
    evidence_ids: list[str] = Field(default_factory=list)

class Conflict(BaseModel):
    description: str
    source_ids: list[str] = Field(default_factory=list)

class SynthesisResult(BaseModel):
    answer: str
    claims: list[Claim] = Field(default_factory=list)    

class ResearchResponse(BaseModel):
    answer: str
    claims: list[Claim] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    conflicts: list[Conflict] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)