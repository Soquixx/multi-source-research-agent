import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

load_dotenv()

from app.core.pipeline import ResearchPipeline
from app.providers.duckduckgo import DuckDuckGoProvider
from app.providers.tavily import TavilyProvider
from app.schemas import ResearchRequest, ResearchResponse
from app.synthesis.gemini import GeminiSynthesisProvider

app = FastAPI(
    title="Multi-Source Research Agent",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://multi-source-research-agent-1.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_pipeline() -> ResearchPipeline:
    tavily_key = os.getenv("TAVILY_API_KEY")

    if not tavily_key:
        raise RuntimeError(
            "TAVILY_API_KEY is not configured"
        )

    return ResearchPipeline(
        providers=[
            TavilyProvider(api_key=tavily_key),
            DuckDuckGoProvider(),
        ],
        synthesis_provider=GeminiSynthesisProvider(),
    )

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/research",
    response_model=ResearchResponse,
)
async def research(
    request: ResearchRequest,
) -> ResearchResponse:

    try:
        pipeline = create_pipeline()

        return await pipeline.research(
            request.question
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc