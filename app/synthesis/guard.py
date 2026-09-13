from app.schemas import Evidence

def can_synthesize(evidence: list[Evidence]) -> bool:
    """Return True only when usable evidence exists."""
    return bool(evidence)