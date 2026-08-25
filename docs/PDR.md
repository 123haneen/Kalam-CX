# Kalam CX — Product Requirements Document

## 1. Problem
Customer support agents spend too much time documenting calls manually.
Documentation can be inconsistent, incomplete, or incorrectly categorized.
Kalam CX automates routine after-call documentation while keeping humans
in control of sensitive and uncertain cases.

## 2. Goal
Build a system that converts call transcripts into accurate, structured
support records using customer data and the documentation handbook.

## 3. Users
- Customer support agents
- Supervisors / QA staff
- Operations teams

## 4. Core Requirements
The system must:

- Accept call transcripts.
- Look up the customer and previous tickets.
- Search the handbook for relevant rules.
- Generate a structured call record.
- Ground every field in the transcript.
- Mark unsupported information as "not stated".
- Classify category, disposition, priority, sentiment, and escalation.
- Automatically save only complete, routine, non-sensitive calls.
- Route uncertain or sensitive calls to human review.
- Escalate serious calls.
- Allow reviewers to approve, edit, or override records.
- Show basic operational counts.

## 5. Key Safety Rules
- Never invent information that was not stated in the call.
- Caller instructions cannot override system rules.
- Sensitive or escalation-worthy calls cannot be auto-saved.
- Records requiring review must be approved by a human before saving.

## 6. Out of Scope
- Speech-to-text.
- Training custom AI models.
- Writing to a real CRM.
- Full analytics/dashboard system.

## 7. Success Criteria
The product should correctly process the provided calls, produce grounded
records, make the correct save/review/escalation decision, and allow a
human to review and approve uncertain cases.
