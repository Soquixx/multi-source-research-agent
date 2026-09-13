import { useState } from "react";
import "./index.css";

const stages = [
  {
    id: "plan",
    label: "Plan",
    description: "Understand the question",
  },
  {
    id: "retrieve",
    label: "Retrieve",
    description: "Search multiple sources",
  },
  {
    id: "merge",
    label: "Merge",
    description: "Normalize & deduplicate",
  },
  {
    id: "rank",
    label: "Rank",
    description: "Score source quality",
  },
  {
    id: "verify",
    label: "Verify",
    description: "Extract supporting evidence",
  },
  {
    id: "synthesize",
    label: "Synthesize",
    description: "Generate grounded answer",
  },
];

function Icon({ children, size = 20 }) {
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        width: size,
        height: size,
      }}
    >
      {children}
    </span>
  );
}

function SearchIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <circle
        cx="11"
        cy="11"
        r="7"
        stroke="currentColor"
        strokeWidth="2"
      />
      <path
        d="M16.5 16.5L21 21"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function ArrowIcon() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none">
      <path
        d="M5 12H19M13 6L19 12L13 18"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
      <path
        d="M5 12.5L9.5 17L19 7"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function ExternalIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
      <path
        d="M14 5H19V10"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M19 5L12 12"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M19 14V18C19 19.1 18.1 20 17 20H6C4.9 20 4 19.1 4 18V7C4 5.9 4.9 5 6 5H10"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function App() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeStage, setActiveStage] = useState(-1);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const runResearch = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) return;

    setLoading(true);
    setResult(null);
    setError("");
    setActiveStage(0);

    // Visual progression only represents the pipeline stages.
    // The actual result still comes entirely from the backend.
    const timers = [
      setTimeout(() => setActiveStage(1), 500),
      setTimeout(() => setActiveStage(2), 1200),
      setTimeout(() => setActiveStage(3), 1900),
      setTimeout(() => setActiveStage(4), 2600),
      setTimeout(() => setActiveStage(5), 3400),
    ];

    try {
      const response = await fetch("/api/research", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: trimmedQuestion,
        }),
      });

      if (!response.ok) {
        let message = "Research request failed.";

        try {
          const data = await response.json();
          message = data.detail || message;
        } catch {
          // Keep default error.
        }

        throw new Error(message);
      }

      const data = await response.json();

      timers.forEach(clearTimeout);
      setActiveStage(5);
      setResult(data);
    } catch (err) {
      timers.forEach(clearTimeout);
      setError(err.message || "Unable to complete research.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      runResearch();
    }
  };

  return (
    <div className="app">
      <header className="navbar">
        <div className="nav-inner">
          <div className="brand">
            <div className="brand-mark">
              <SearchIcon />
            </div>

            <div>
              <div className="brand-name">RESEARCH</div>
              <div className="brand-subtitle">MULTI-SOURCE AGENT</div>
            </div>
          </div>

          <div className="system-status">
            <span className="status-dot" />
            SYSTEM ONLINE
          </div>
        </div>
      </header>

      {!result && !loading && (
        <main className="hero">
          <div className="hero-decoration hero-decoration-one" />
          <div className="hero-decoration hero-decoration-two" />

          <div className="hero-content">
            <div className="eyebrow">
              <span />
              EVIDENCE-GROUNDED RESEARCH
            </div>

            <h1>
              Research with
              <br />
              <span>evidence,</span> not assumptions.
            </h1>

            <p className="hero-description">
              Ask a question and let the agent search multiple sources,
              evaluate evidence, and synthesize a grounded answer.
            </p>

            <div className="search-box">
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="What would you like to research?"
                rows={1}
              />

              <button
                className="research-button"
                onClick={runResearch}
                disabled={!question.trim()}
              >
                Research
                <ArrowIcon />
              </button>
            </div>

            <div className="input-hint">
              Press <strong>Ctrl + Enter</strong> to research
            </div>

            <div className="hero-features">
              <div>
                <strong>02+</strong>
                <span>Independent sources</span>
              </div>

              <div>
                <strong>Evidence</strong>
                <span>Traceable claims</span>
              </div>

              <div>
                <strong>Resilient</strong>
                <span>Failure-aware pipeline</span>
              </div>
            </div>
          </div>
        </main>
      )}

      {loading && (
        <main className="researching">
          <div className="researching-header">
            <div className="eyebrow">
              <span />
              RESEARCH IN PROGRESS
            </div>

            <h2>Building your answer.</h2>

            <p>
              The agent is gathering and evaluating evidence across
              multiple sources.
            </p>
          </div>

          <div className="pipeline-card">
            {stages.map((stage, index) => {
              const completed = index < activeStage;
              const current = index === activeStage;

              return (
                <div className="pipeline-stage" key={stage.id}>
                  <div
                    className={`stage-icon ${
                      completed
                        ? "completed"
                        : current
                          ? "current"
                          : ""
                    }`}
                  >
                    {completed ? (
                      <CheckIcon />
                    ) : (
                      <span>{String(index + 1).padStart(2, "0")}</span>
                    )}
                  </div>

                  <div className="stage-info">
                    <strong>{stage.label}</strong>
                    <span>{stage.description}</span>
                  </div>

                  {index < stages.length - 1 && (
                    <div
                      className={`stage-line ${
                        completed ? "completed" : ""
                      }`}
                    />
                  )}
                </div>
              );
            })}
          </div>

          <div className="research-note">
            <span className="loading-dot" />
            Processing live research data...
          </div>
        </main>
      )}

      {error && (
        <div className="error-card">
          <strong>Research could not be completed.</strong>
          <span>{error}</span>

          <button
            onClick={() => {
              setError("");
              setResult(null);
              setActiveStage(-1);
            }}
          >
            Try again
          </button>
        </div>
      )}

      {result && !loading && (
        <main className="results-page">
          <div className="results-top">
            <div>
              <div className="eyebrow">
                <span />
                RESEARCH COMPLETE
              </div>

              <h1>Research result</h1>

              <p className="question-display">
                “{question}”
              </p>
            </div>

            <button
              className="new-research"
              onClick={() => {
                setResult(null);
                setQuestion("");
                setActiveStage(-1);
              }}
            >
              New research
              <ArrowIcon />
            </button>
          </div>

          <section className="answer-card">
            <div className="section-label">SYNTHESIZED ANSWER</div>

            <p className="answer-text">
              {result.answer}
            </p>
          </section>

          <div className="stats-row">
            <div className="stat-card">
              <span>CLAIMS</span>
              <strong>{result.claims?.length || 0}</strong>
            </div>

            <div className="stat-card">
              <span>SOURCES</span>
              <strong>{result.sources?.length || 0}</strong>
            </div>

            <div className="stat-card">
              <span>CONFLICTS</span>
              <strong>{result.conflicts?.length || 0}</strong>
            </div>

            <div className="stat-card">
              <span>UNCERTAINTIES</span>
              <strong>{result.uncertainties?.length || 0}</strong>
            </div>
          </div>

          <section className="result-section">
            <div className="section-heading">
              <div>
                <div className="section-label">EVIDENCE</div>
                <h2>Supporting claims</h2>
              </div>
            </div>

            <div className="claims-grid">
              {result.claims?.length ? (
                result.claims.map((claim, index) => (
                  <article className="claim-card" key={index}>
                    <div className="claim-number">
                      {String(index + 1).padStart(2, "0")}
                    </div>

                    <p>{claim.text}</p>

                    <div className="evidence-tags">
                      {claim.evidence_ids?.map((id) => (
                        <span key={id}>{id}</span>
                      ))}
                    </div>
                  </article>
                ))
              ) : (
                <div className="empty-state">
                  No supporting claims were returned.
                </div>
              )}
            </div>
          </section>

          <section className="result-section">
            <div className="section-heading">
              <div>
                <div className="section-label">RETRIEVED MATERIAL</div>
                <h2>Sources</h2>
              </div>
            </div>

            <div className="sources-list">
              {result.sources?.length ? (
                result.sources.map((source, index) => (
                  <article
                    className="source-card"
                    key={source.source_id || index}
                  >
                    <div className="source-index">
                      {String(index + 1).padStart(2, "0")}
                    </div>

                    <div className="source-main">
                      <div className="source-provider-row">
                        {source.providers?.map((provider) => (
                          <span
                            className="provider-tag"
                            key={provider}
                          >
                            {provider}
                          </span>
                        ))}

                        {source.fetch_success && (
                          <span className="verified-tag">
                            <CheckIcon />
                            fetched
                          </span>
                        )}
                      </div>

                      <h3>{source.title}</h3>

                      <p>
                        {source.snippet ||
                          "Source content was retrieved for evaluation."}
                      </p>

                      <a
                        href={source.url}
                        target="_blank"
                        rel="noreferrer"
                        className="source-link"
                      >
                        {source.url}
                        <ExternalIcon />
                      </a>
                    </div>

                    <div className="scores">
                      <div>
                        <span>RELEVANCE</span>
                        <strong>
                          {Math.round(
                            (source.relevance_score || 0) * 100
                          )}
                        </strong>
                      </div>

                      <div>
                        <span>QUALITY</span>
                        <strong>
                          {Math.round(
                            (source.quality_score || 0) * 100
                          )}
                        </strong>
                      </div>
                    </div>
                  </article>
                ))
              ) : (
                <div className="empty-state">
                  No sources were returned.
                </div>
              )}
            </div>
          </section>

          {(result.conflicts?.length > 0 ||
            result.uncertainties?.length > 0) && (
            <section className="analysis-grid">
              {result.conflicts?.length > 0 && (
                <div className="analysis-card conflict-card">
                  <div className="section-label">CONFLICTS</div>

                  <h2>Conflicting evidence</h2>

                  {result.conflicts.map((conflict, index) => (
                    <div className="analysis-item" key={index}>
                      <strong>{conflict.description}</strong>

                      {conflict.source_ids?.length > 0 && (
                        <div className="evidence-tags">
                          {conflict.source_ids.map((id) => (
                            <span key={id}>{id}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {result.uncertainties?.length > 0 && (
                <div className="analysis-card uncertainty-card">
                  <div className="section-label">UNCERTAINTY</div>

                  <h2>Research limitations</h2>

                  {result.uncertainties.map((uncertainty, index) => (
                    <div className="analysis-item" key={index}>
                      <span>{uncertainty}</span>
                    </div>
                  ))}
                </div>
              )}
            </section>
          )}
        </main>
      )}

      <footer className="footer">
        <span>Multi-Source Research Agent</span>
        <span>Evidence-aware · Resilient · Traceable</span>
      </footer>
    </div>
  );
}

export default App;