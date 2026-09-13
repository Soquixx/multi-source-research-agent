# Multi-Source Web Research Agent

A web research agent that uses multiple search providers and an LLM to answer research questions using retrieved source evidence.

## Demo

🎥 **Demo Video:** [Watch the demo](frontend/src/assets/demo.mp4)

The demo shows:
- Research question input
- Multi-source retrieval
- Evidence-based synthesis
- Supporting claims and sources
- Uncertainty handling

---

## Screenshots

### Research Input

![Research Input](frontend/src/assets/homepage.png)

### Research Result

![Research Result](frontend/src/assets/image.png)

---

## Workflow

The research pipeline follows these stages:

```mermaid
flowchart TD
    A[Research Question] --> B[Multiple Search Providers]
    B --> C[Merge Results]
    C --> D[Deduplicate]
    D --> E[Source Ranking]
    E --> F[Fetch Source Content]
    F --> G[Extract Evidence]
    G --> H[Verify Evidence]
    H --> I[Detect Conflicts]
    I --> J{Relevant Evidence?}
    J -- No --> K[Return Insufficient Evidence]
    J -- Yes --> L[LLM Synthesis]
    L --> M[Answer + Claims + Sources + Uncertainties]
````

The main pipeline is implemented in `app/core/pipeline.py`.

---

## Architecture

The project separates retrieval, processing, verification, and synthesis into independent modules.

```mermaid
flowchart LR
    UI[React Frontend] --> API[FastAPI API]
    API --> P[Research Pipeline]

    P --> SP[Search Providers]
    P --> DP[Deduplication]
    P --> R[Ranking]
    P --> F[Fetching]
    P --> E[Evidence Extraction]
    P --> V[Verification]
    P --> C[Conflict Detection]
    P --> S[LLM Synthesis]

    S --> API
    API --> UI
```

### Main Modules

| Module                        | Responsibility                                   |
| ----------------------------- | ------------------------------------------------ |
| `providers/`                  | Search provider implementations                  |
| `processing/deduplication.py` | Removes duplicate results                        |
| `processing/ranking.py`       | Ranks sources using relevance and quality        |
| `processing/fetching.py`      | Fetches and extracts readable webpage content    |
| `processing/evidence.py`      | Extracts evidence from source content            |
| `processing/verification.py`  | Checks evidence relevance and possible conflicts |
| `synthesis/`                  | Generates the final answer using the LLM         |
| `core/pipeline.py`            | Coordinates the complete research workflow       |

---

## Key Design Decisions

### Multiple Search Providers

The pipeline requires at least two search providers. Each provider is queried independently, so a failure in one provider does not stop the complete research process.

### Deduplication

Results from different providers can point to the same page. Results are normalized and deduplicated before the sources are selected for fetching.

### Source Ranking

Sources are ranked using two explicit factors:

* Relevance to the research question
* Source quality

The ranking uses deterministic rules so the selection process is predictable and reproducible.

### Evidence Before Synthesis

Source content is fetched and evidence is extracted before the LLM is called.

The evidence is then checked for meaningful overlap with the research question. If relevant evidence cannot be found, the synthesis step is skipped.

### Conflict Detection

The system checks for possible numerical conflicts between evidence from different sources.

Potential conflicts are reported instead of silently selecting one value.

### Failure Handling

Search and source-fetch operations use retry handling. If a provider or source cannot be reached, the failure is recorded and the pipeline continues with the available sources where possible.

---

## Technology Stack

| Layer           | Technology                |
| --------------- | ------------------------- |
| Backend         | Python, FastAPI           |
| Search          | Multiple search providers |
| HTTP / Fetching | httpx                     |
| HTML Parsing    | BeautifulSoup             |
| Data Validation | Pydantic                  |
| LLM             | Google Gemini             |
| Frontend        | React, Vite               |
| Testing         | Pytest                    |

---

## Setup

### Backend

Create a virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example` and add the required API keys.

Run the backend:

```bash
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Example

**Question**

```text
What are the main challenges preventing electric vehicles from becoming mainstream in India?
```

The application returns:

* Synthesized answer
* Supporting claims
* Retrieved sources
* Possible conflicts
* Uncertainties and unavailable evidence

---

## Reliability

The pipeline handles:

* Search provider failures
* Request timeouts
* Source fetch failures
* Retryable errors
* Empty search results
* Missing relevant evidence

Failures are recorded as uncertainties instead of being hidden from the user.

---

## Testing

Tests are included for the main processing and pipeline components.

Run:

```bash
pytest
```

---

## Limitations

* Evidence verification currently uses lexical matching rather than semantic verification.
* Conflict detection focuses on obvious numerical differences.
* Some websites may block automated requests or require JavaScript rendering.
* Source quality is based on explicit heuristics and is not a complete credibility assessment.
* Complex research questions are not currently decomposed into multiple sub-queries.

---

## Future Improvements

* Semantic evidence verification
* Better source credibility scoring
* Improved handling of JavaScript-rendered pages
* Stronger claim-to-evidence mapping
* More robust conflict detection
* Query decomposition for complex questions

---

## Implementation

I implemented the research pipeline, including multi-provider retrieval, result processing, source fetching, evidence extraction and verification, conflict detection, retry handling, and LLM synthesis.

The main design choice was to keep retrieval and evidence processing separate from the LLM. The LLM is called only after relevant evidence has been found.

---

## License

This project was developed as part of an AI/ML internship technical evaluation.