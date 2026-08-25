"""
Deterministic decision engine for Kalam CX.

This module makes the final processing decision based on validation
results and handbook rules.

The AI does not control these decisions.
"""


from src.schemas import (
    AIDocumentationDraft,
    DecisionResult,
    DecisionType,
    GroundingSafetyResult,
    HandbookRule,
)


def make_decision(
    draft: AIDocumentationDraft,
    validation: GroundingSafetyResult,
    handbook_rules: list[HandbookRule],
) -> DecisionResult:
    """Make a deterministic decision for a documentation draft.

    Decision priority:

    1. Non-interaction
    2. Escalation
    3. Human review
    4. Auto-save

    Args:
        draft: The AI-generated documentation draft.
        validation: Grounding and safety validation result.
        handbook_rules: Relevant handbook rules.

    Returns:
        A deterministic DecisionResult.
    """

    # 1. Non-interaction
    if draft.category.lower() == "non-interaction":
        return DecisionResult(
            decision=DecisionType.NON_INTERACTION,
            reason="The call was classified as a non-interaction.",
            review_required=False,
            escalation_required=False,
        )

    # 2. Escalation
    if validation.escalation_triggered:
        return DecisionResult(
            decision=DecisionType.ESCALATE,
            reason="An escalation condition was triggered by the handbook.",
            review_required=False,
            escalation_required=True,
        )

    # 3. Human review
    if (
        not validation.grounded
        or validation.sensitive_data_detected
        or validation.ambiguity_detected
    ):
        return DecisionResult(
            decision=DecisionType.HUMAN_REVIEW,
            reason="The draft requires human review due to validation or safety concerns.",
            review_required=True,
            escalation_required=False,
        )

    # 4. Auto-save
    return DecisionResult(
        decision=DecisionType.AUTO_SAVE,
        reason="The draft passed the required deterministic checks.",
        review_required=False,
        escalation_required=False,
    )