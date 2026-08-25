"""
Grounding and safety validation utilities for Kalam CX.

This module checks whether an AI-generated documentation draft is
supported by the available transcript and handbook rules.

It does not make the final save, review, or escalation decision.
"""

import re

from src.schemas import (
    AIDocumentationDraft,
    GroundingSafetyResult,
    HandbookRule,
)


def validate_draft(
    transcript: str,
    draft: AIDocumentationDraft,
    handbook_rules: list[HandbookRule],
) -> GroundingSafetyResult:
    """Validate an AI documentation draft against the available context.

    Args:
        transcript: The original/cleaned call transcript.
        draft: AI-generated documentation draft.
        handbook_rules: Relevant handbook rules.

    Returns:
        A GroundingSafetyResult containing validation findings.
    """
    if not isinstance(transcript, str):
        raise TypeError("transcript must be a string")

    if not transcript.strip():
        raise ValueError("transcript must not be empty or whitespace-only")

    unsupported_fields: list[str] = []
    validation_errors: list[str] = []

    transcript_lower = transcript.lower()

    # Check whether important generated text is supported by the transcript.
    fields_to_check = {
        "summary": draft.summary,
        "resolution": draft.resolution,
        "next_action": draft.next_action,
    }

    for field_name, value in fields_to_check.items():
        if value == "not stated":
            continue

        if value.strip().lower() not in transcript_lower:
            unsupported_fields.append(field_name)

    # Check for ambiguity.
    ambiguity_detected = any(
        phrase in transcript_lower
        for phrase in [
            "not sure",
            "unclear",
            "i don't know",
            "i do not know",
            "maybe",
        ]
    )

    # Check whether any handbook rule requires escalation.
    escalation_triggered = any(
        rule.escalation_required for rule in handbook_rules
    )

    # Basic sensitive-data detection.
    sensitive_patterns = [
        r"\b\d{16}\b",          # Possible card number
        r"\b\d{3}-\d{2}-\d{4}\b",  # Possible SSN-style value
    ]

    sensitive_data_detected = any(
        re.search(pattern, transcript) is not None
        for pattern in sensitive_patterns
    )

    if unsupported_fields:
        validation_errors.append(
            "Some generated fields are not directly supported by the transcript."
        )

    if ambiguity_detected:
        validation_errors.append(
            "The transcript contains potentially ambiguous language."
        )

    if sensitive_data_detected:
        validation_errors.append(
            "Potential sensitive information was detected in the transcript."
        )

    grounded = len(unsupported_fields) == 0

    return GroundingSafetyResult(
        grounded=grounded,
        unsupported_fields=unsupported_fields,
        sensitive_data_detected=sensitive_data_detected,
        ambiguity_detected=ambiguity_detected,
        escalation_triggered=escalation_triggered,
        validation_errors=validation_errors,
    )