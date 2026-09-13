from app.schemas import Evidence, SynthesisResult

def validate_synthesis(
    result: SynthesisResult,
    evidence: list[Evidence],
) -> SynthesisResult:
    """
    Validate that every generated claim is grounded in supplied evidence.
    """
    valid_evidence_ids = {
        item.evidence_id
        for item in evidence
    }

    for claim in result.claims:
        if not claim.evidence_ids:
            raise ValueError(
                "Generated claim has no evidence references"
            )

        unknown_ids = set(claim.evidence_ids) - valid_evidence_ids

        if unknown_ids:
            raise ValueError(
                f"Claim references unknown evidence: {unknown_ids}"
            )

    return result