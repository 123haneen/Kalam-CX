import json

import pytest

from src.analyzer import analyze_call
from src.customer import get_customer
from src.decision_engine import make_decision
from src.handbook import get_handbook_rules
from src.loader import load_json
from src.schemas import (
    AIDocumentationDraft,
    CustomerData,
    DecisionType,
    GroundingSafetyResult,
    HandbookRule,
)
from src.transcript_parser import parse_transcript
from src.validator import validate_draft


# ---------------------------------------------------------
# Test data
# ---------------------------------------------------------

CUSTOMERS = [
    {
        "customer_id": "CUS-001",
        "name": "Test Customer",
        "account_tier": "standard",
        "account_status": "active",
        "previous_tickets": [],
    }
]


RULES = [
    {
        "rule_id": "RULE-001",
        "category": "billing",
        "disposition": "billing_support",
        "priority": "medium",
        "sentiment": "neutral",
        "escalation_required": False,
        "rule_text": "Handle standard billing questions.",
    },
    {
        "rule_id": "RULE-002",
        "category": "fraud",
        "disposition": "fraud_escalation",
        "priority": "high",
        "sentiment": "negative",
        "escalation_required": True,
        "rule_text": "Escalate suspected fraud cases.",
    },
]


# ---------------------------------------------------------
# schemas.py
# ---------------------------------------------------------

def test_customer_model():
    customer = CustomerData(
        customer_id="CUS-001",
        name="Test Customer",
        account_tier="standard",
        account_status="active",
    )

    assert customer.customer_id == "CUS-001"
    assert customer.name == "Test Customer"


def test_decision_enum():
    assert DecisionType.AUTO_SAVE.value == "AUTO_SAVE"
    assert DecisionType.HUMAN_REVIEW.value == "HUMAN_REVIEW"
    assert DecisionType.ESCALATE.value == "ESCALATE"
    assert DecisionType.NON_INTERACTION.value == "NON_INTERACTION"


# ---------------------------------------------------------
# loader.py
# ---------------------------------------------------------

def test_load_json(tmp_path):
    file_path = tmp_path / "customers.json"

    file_path.write_text(
        json.dumps({"customers": CUSTOMERS}),
        encoding="utf-8",
    )

    data = load_json(str(file_path))

    assert data["customers"][0]["customer_id"] == "CUS-001"


def test_load_json_missing_file():
    with pytest.raises(FileNotFoundError):
        load_json("does_not_exist.json")


def test_load_json_invalid_json(tmp_path):
    file_path = tmp_path / "invalid.json"

    file_path.write_text(
        "{invalid json}",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_json(str(file_path))


# ---------------------------------------------------------
# transcript_parser.py
# ---------------------------------------------------------

def test_parse_transcript():
    raw = "  Hello customer.  \n\n\n\n I need help.   "

    result = parse_transcript(raw)

    assert result == "Hello customer.\n\n I need help."


def test_parse_empty_transcript():
    with pytest.raises(ValueError):
        parse_transcript("   ")


def test_parse_invalid_transcript_type():
    with pytest.raises(TypeError):
        parse_transcript(123)


# ---------------------------------------------------------
# customer.py
# ---------------------------------------------------------

def test_customer_lookup():
    customer = get_customer("CUS-001", CUSTOMERS)

    assert isinstance(customer, CustomerData)
    assert customer.customer_id == "CUS-001"


def test_customer_not_found():
    with pytest.raises(LookupError):
        get_customer("CUS-999", CUSTOMERS)


def test_customer_invalid_id():
    with pytest.raises(ValueError):
        get_customer("   ", CUSTOMERS)


# ---------------------------------------------------------
# handbook.py
# ---------------------------------------------------------

def test_handbook_lookup():
    rules = get_handbook_rules("billing", RULES)

    assert len(rules) == 1
    assert isinstance(rules[0], HandbookRule)
    assert rules[0].rule_id == "RULE-001"


def test_handbook_not_found():
    with pytest.raises(LookupError):
        get_handbook_rules("unknown", RULES)


def test_handbook_invalid_category():
    with pytest.raises(ValueError):
        get_handbook_rules("   ", RULES)


# ---------------------------------------------------------
# analyzer.py
# ---------------------------------------------------------

def test_analyzer_creates_draft():
    customer = get_customer("CUS-001", CUSTOMERS)
    rules = get_handbook_rules("billing", RULES)

    transcript = "Customer asked about a billing issue."

    draft = analyze_call(
        transcript,
        customer,
        rules,
    )

    assert isinstance(draft, AIDocumentationDraft)
    assert draft.category == "billing"
    assert draft.disposition == "billing_support"


# ---------------------------------------------------------
# validator.py
# ---------------------------------------------------------

def test_validator_grounded():
    rules = get_handbook_rules("billing", RULES)

    draft = AIDocumentationDraft(
        category="billing",
        disposition="billing_support",
        priority="medium",
        sentiment="neutral",
        summary="Customer asked about a billing issue.",
        resolution="not stated",
        next_action="not stated",
    )

    transcript = "Customer asked about a billing issue."

    result = validate_draft(
        transcript,
        draft,
        rules,
    )

    assert isinstance(result, GroundingSafetyResult)
    assert result.grounded is True
    assert result.escalation_triggered is False


def test_validator_detects_unsupported_field():
    rules = get_handbook_rules("billing", RULES)

    draft = AIDocumentationDraft(
        category="billing",
        disposition="billing_support",
        priority="medium",
        sentiment="neutral",
        summary="Customer asked about a billing issue.",
        resolution="Refund was issued.",
        next_action="not stated",
    )

    transcript = "Customer asked about a billing issue."

    result = validate_draft(
        transcript,
        draft,
        rules,
    )

    assert result.grounded is False
    assert "resolution" in result.unsupported_fields


# ---------------------------------------------------------
# decision_engine.py
# ---------------------------------------------------------

def test_decision_auto_save():
    draft = AIDocumentationDraft(
        category="billing",
        disposition="billing_support",
        priority="medium",
        sentiment="neutral",
        summary="Customer asked about a billing issue.",
        resolution="not stated",
        next_action="not stated",
    )

    validation = GroundingSafetyResult(
        grounded=True,
        sensitive_data_detected=False,
        ambiguity_detected=False,
        escalation_triggered=False,
    )

    result = make_decision(
        draft,
        validation,
        [],
    )

    assert result.decision == DecisionType.AUTO_SAVE


def test_decision_human_review():
    draft = AIDocumentationDraft(
        category="billing",
        disposition="billing_support",
        priority="medium",
        sentiment="neutral",
        summary="Unsupported summary.",
        resolution="not stated",
        next_action="not stated",
    )

    validation = GroundingSafetyResult(
        grounded=False,
        unsupported_fields=["summary"],
        sensitive_data_detected=False,
        ambiguity_detected=False,
        escalation_triggered=False,
    )

    result = make_decision(
        draft,
        validation,
        [],
    )

    assert result.decision == DecisionType.HUMAN_REVIEW


def test_decision_escalate():
    draft = AIDocumentationDraft(
        category="fraud",
        disposition="fraud_escalation",
        priority="high",
        sentiment="negative",
        summary="Customer reported suspicious activity.",
        resolution="not stated",
        next_action="not stated",
    )

    validation = GroundingSafetyResult(
        grounded=True,
        sensitive_data_detected=False,
        ambiguity_detected=False,
        escalation_triggered=True,
    )

    result = make_decision(
        draft,
        validation,
        [],
    )

    assert result.decision == DecisionType.ESCALATE


def test_decision_non_interaction():
    draft = AIDocumentationDraft(
        category="non-interaction",
        disposition="not stated",
        priority="not stated",
        sentiment="not stated",
        summary="No meaningful interaction occurred.",
        resolution="not stated",
        next_action="not stated",
    )

    validation = GroundingSafetyResult(
        grounded=True,
        sensitive_data_detected=False,
        ambiguity_detected=False,
        escalation_triggered=False,
    )

    result = make_decision(
        draft,
        validation,
        [],
    )

    assert result.decision == DecisionType.NON_INTERACTION