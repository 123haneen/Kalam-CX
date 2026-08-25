# Kalam CX — System Architecture

## 1. Architecture Overview

Kalam CX processes a call transcript through a guarded documentation pipeline.

```text
Call Transcript
      ↓
Call Intake
      ↓
Customer Lookup
      ↓
Handbook Retrieval
      ↓
AI Documentation Engine
      ↓
Grounding & Safety Checks
      ↓
Decision Engine
      ↓
 ┌──────────┬──────────────┬───────────┬────────────────┐
 ↓          ↓              ↓           ↓
Auto-Save  Review       Escalate   Non-Interaction
 ↓          ↓              ↓
 └──────────┴──────────────┘
             ↓
       Final Record Store
             ↓
      Operational Summary
```

## 2. Main Components

### Call Intake

Receives the already-transcribed customer call and starts the processing workflow.

### Customer Lookup

Uses the customer ID from the call to retrieve customer information, account details, tier, and relevant previous tickets.

### Handbook Retrieval

Searches the documentation handbook and retrieves the rules relevant to the call, including category, disposition, priority, sentiment, and escalation rules.

### AI Documentation Engine

Uses the transcript, customer information, and retrieved handbook rules to create a structured draft record.

The AI is responsible for understanding and extracting information, but it does not have final authority over safety or save decisions.

### Grounding & Safety Checks

Checks that generated fields are supported by the transcript.

Unsupported information is marked as "not stated".

This layer also checks sensitive information, escalation triggers, ambiguity, and other safety conditions.

### Decision Engine

Applies deterministic rules to decide whether the call should be:

* Auto-saved
* Sent to human review
* Escalated
* Classified as a non-interaction

The auto-save decision is controlled by system rules rather than by the AI's response.

### Human Review

Reviewers can inspect the transcript and generated record, edit fields, approve the record, or override the recommendation.

### Final Record Store

Stores approved records and automatically saved records in the application's own data store.

No real external CRM is updated.

### Operational Summary

Provides basic counts for processed calls, auto-saved calls, reviews, escalations, non-interactions, categories, and sentiments.

---

## 3. Key Design Principle

The AI generates a documentation draft, while deterministic application logic controls the safety-critical decisions.

In particular:

```text
AI
 ↓
Draft
 ↓
Code-based validation
 ↓
Decision
```

This prevents the model from inventing unsupported information or bypassing escalation and review rules.
