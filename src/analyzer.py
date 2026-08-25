"""
AI documentation engine for Kalam CX.

This module creates a structured documentation draft from:
- the cleaned call transcript
- customer information
- relevant handbook rules

This is currently a deterministic/local implementation.
A real AI provider can be integrated later.

The analyzer does NOT make final safety or save decisions.
"""

from src.schemas import (
    AIDocumentationDraft,
    CustomerData,
    HandbookRule,
)


def analyze_call(
    transcript: str,
    customer: CustomerData,
    handbook_rules: list[HandbookRule],
) -> AIDocumentationDraft:
    """Generate a structured documentation draft from call information.

    The current implementation uses available structured information
    without calling an external AI service.

    Args:
        transcript: Cleaned call transcript.
        customer: Customer information.
        handbook_rules: Relevant handbook rules.

    Returns:
        An AIDocumentationDraft containing the generated documentation.
    """
    if not isinstance(transcript, str):
        raise TypeError("transcript must be a string")

    if not transcript.strip():
        raise ValueError("transcript must not be empty or whitespace-only")

    if not handbook_rules:
        raise ValueError("at least one handbook rule is required")

    # Use the first applicable handbook rule as the primary rule.
    rule = handbook_rules[0]

    return AIDocumentationDraft(
        category=rule.category,
        disposition=rule.disposition,
        priority=rule.priority,
        sentiment=rule.sentiment,
        summary=transcript[:500],
        resolution="not stated",
        next_action="not stated",
        escalation_reason=(
            "Escalation required by handbook rule."
            if rule.escalation_required
            else None
        ),
    )