"""End-to-end orchestration for processing one real call."""
from datetime import datetime, timezone
from src.data_access import load_call, load_customers, load_handbook_rules
from src.customer import get_customer
from src.transcript_parser import parse_transcript
from src.analyzer import analyze_call
from src.validator import validate_draft
from src.decision_engine import make_decision
from src.schemas import FinalRecord, RecordStatus, DecisionType
from src.storage import upsert


def process_call(call_id:str, persist:bool=True)->FinalRecord:
    call=load_call(call_id); transcript=parse_transcript(call.transcript)
    customer=get_customer(call.customer_id,load_customers()) if call.customer_id else None
    rules=load_handbook_rules(); draft=analyze_call(transcript,customer,rules); validation=validate_draft(transcript,draft,rules); decision=make_decision(draft,validation,rules)
    status={DecisionType.AUTO_SAVE:RecordStatus.AUTO_SAVED,DecisionType.ROUTE_TO_REVIEW:RecordStatus.PENDING_REVIEW,DecisionType.HUMAN_REVIEW:RecordStatus.PENDING_REVIEW,DecisionType.ESCALATE:RecordStatus.ESCALATED,DecisionType.NON_INTERACTION:RecordStatus.NON_INTERACTION}[decision.decision]
    now=datetime.now(timezone.utc).isoformat()
    record=FinalRecord(record_id=f"R-{call.call_id}",call_id=call.call_id,customer_id=call.customer_id,customer_name=customer.name if customer else "",client=customer.client if customer else "",tier=(customer.tier or customer.account_tier) if customer else "",category=draft.category,subcategory=draft.subcategory,disposition=draft.disposition,priority=draft.priority,sentiment=draft.sentiment,summary=draft.summary,issue=draft.issue,root_cause=draft.root_cause,resolution=draft.resolution,next_action=draft.next_action,follow_up_actions=draft.follow_up_actions,keywords=draft.keywords,tags=draft.tags,status=status,decision=decision.decision,escalation_flag=draft.escalation_flag,escalation_reason=draft.escalation_reason,rule_references=draft.rule_references,grounding=validation.field_evidence,decision_reason=decision.reason,created_at=now,updated_at=now)
    return upsert(record) if persist else record
