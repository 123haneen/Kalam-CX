# Kalam CX — AI-Powered After-Call Automation Platform

Kalam CX is a guarded after-call automation platform that converts customer-support call transcripts into structured, handbook-grounded records.

The system processes real call transcripts, retrieves customer context, applies handbook rules, validates every generated field, and uses deterministic code-level safeguards to decide whether a call can be automatically saved, requires human review, must be escalated, or should be classified as a non-interaction.

The project includes a FastAPI backend, guarded processing engine, SQLite record storage, human review workflow, operational summary, evaluation suite, and React frontend.

> `answer_key.json` is never used to generate records. It is used only by the evaluation process to compare system outcomes against expected results.

---

## Core Features

### Call Intake

- Loads real customer-support call transcripts.
- Supports the provided call dataset (`K-001` to `K-027`).
- Retrieves customer information using the call's customer ID.
- Preserves the original transcript for grounding and traceability.

### Structured After-Call Documentation

For every processed interaction, Kalam CX produces a structured record containing:

- Summary
- Issue
- Root cause
- Resolution
- Next action
- Sentiment
- Category
- Subcategory
- Priority
- Disposition
- Follow-up actions
- Keywords
- Tags
- Escalation flag
- Escalation reason
- Handbook rule references
- Grounding evidence

Structured documentation is kept concise while the original supporting transcript evidence is preserved separately.

### Handbook-Grounded Classification

The system uses the provided handbook as the source of truth for:

- Category and subcategory
- Disposition
- Priority
- Sentiment
- Escalation rules
- Review requirements

Handbook clause references are stored with the generated record to make classification and decisions traceable.

### Guarded Decision Engine

Operational decisions are controlled by deterministic application logic rather than caller instructions.

Possible decisions include:

- `AUTO_SAVE`
- `ROUTE_TO_REVIEW`
- `HUMAN_REVIEW`
- `ESCALATE`
- `NON_INTERACTION`

Automatic saving is allowed only when the call satisfies the guarded conditions, including being complete, routine, non-sensitive, sufficiently grounded, and free from escalation triggers.

Sensitive, ambiguous, incomplete, or escalation-worthy calls cannot bypass the guarded engine.

### Caller Manipulation Protection

Instructions contained inside a call transcript cannot override the system's rules.

For example, a caller asking the system to:

- Mark the call as resolved
- Close other tickets
- Suppress an escalation
- Change the documentation outcome

is documented but not obeyed.

The decision remains controlled by application logic and handbook rules.

### Human-in-the-Loop Review

Calls requiring human judgment are placed into a review queue.

The review interface allows a reviewer to:

- Inspect the drafted record
- Review the engine recommendation
- Review classification and priority
- Inspect grounding evidence
- Inspect handbook rule references
- Approve the record
- Edit supported fields
- Override the engine recommendation with a reviewer note

Records requiring human review are not approved automatically.

### Operational Summary

Kalam CX includes a lightweight operational counts panel showing:

- Total calls
- Auto-saved calls
- Calls requiring human review
- Escalated calls
- Non-interactions
- Calls by category
- Calls by sentiment

The summary is intentionally a simple operational view rather than a full analytics dashboard.

---

## System Architecture

The main processing flow is:

```text
Call Transcript
      ↓
Customer Lookup
      ↓
Handbook Retrieval
      ↓
Documentation Analysis
      ↓
Grounding & Safety Validation
      ↓
Deterministic Decision Engine
      ↓
 ┌─────────────────────────────────────────────┐
 │ AUTO_SAVE                                   │
 │ ROUTE_TO_REVIEW / HUMAN_REVIEW              │
 │ ESCALATE                                    │
 │ NON_INTERACTION                             │
 └─────────────────────────────────────────────┘
      ↓
Record Store / Human Review Queue
      ↓
Operational Summary
```

A key architectural principle is that documentation generation and operational decision-making are separated.

The analyzer creates the structured draft, while deterministic application logic controls whether the result can be automatically saved, requires review, or must be escalated.

---

## Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- SQLite
- Uvicorn

### Frontend

- React
- Vite
- JavaScript
- CSS

### Testing

- Pytest
- Custom evaluation runner

---

## Project Structure

```text
kalam-cx/
│
├── src/
│   ├── analyzer.py
│   ├── api.py
│   ├── customer.py
│   ├── data_access.py
│   ├── decision_engine.py
│   ├── handbook.py
│   ├── loader.py
│   ├── pipeline.py
│   ├── schemas.py
│   ├── storage.py
│   ├── transcript_parser.py
│   └── validator.py
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── CallsPage.jsx
│   │   │   ├── ReviewQueuePage.jsx
│   │   │   └── SummaryPage.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   └── package.json
│
├── evaluation/
│   ├── run_evaluation.py
│   └── evaluation_results.json
│
├── tests/
│   └── test_pipeline.py
│
├── docs/
│   ├── PRD.md
│   ├── System_Architecture.md
│   └── Data_Schema.md
│
├── requirements.txt
└── README.md
```

The exact dataset and supporting files remain in their corresponding project directories.

---

# Running Kalam CX

## 1. Backend Setup

From the project root, install the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the FastAPI backend:

```bash
python -m uvicorn src.api:app --reload
```

The backend runs locally on port `8000`.

FastAPI's interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

## 2. Frontend Setup

Open another terminal and move into the frontend directory:

```bash
cd frontend
```

Install the frontend dependencies if needed:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

Open the local URL displayed by Vite in the terminal.

The React frontend communicates with the FastAPI backend running on port `8000`.

---

## API Endpoints

### System

```text
GET /health
```

Checks whether the API is running.

### Calls

```text
GET /calls
```

Returns available incoming calls.

```text
GET /calls/{call_id}
```

Returns a specific call and its transcript.

### Processing

```text
POST /process/{call_id}
```

Processes one call through the complete Kalam CX pipeline.

```text
POST /process-all
```

Processes the available calls.

### Records

```text
GET /records
```

Returns processed records.

```text
DELETE /records
```

Clears stored application records.

### Human Review

```text
GET /review-queue
```

Returns records requiring human review.

```text
POST /review/{call_id}
```

Allows a human reviewer to approve, edit, or override a pending record.

### Operational Summary

```text
GET /summary
```

Returns operational counts and category/sentiment breakdowns.

---

# Frontend Product Flow

The frontend contains three main product views.

## 1. Call Intake

The user selects an incoming call and reviews the original transcript.

Selecting **Process Call** sends the call through the complete backend pipeline.

The processed record displays:

- Structured documentation
- Classification
- Sentiment
- Priority
- Disposition
- Operational decision
- Escalation information
- Follow-up actions
- Keywords and tags
- Handbook rule references
- Grounding evidence

---

## 2. Review Queue

Calls that cannot be safely auto-saved are presented for human review.

The reviewer can inspect the drafted documentation and recommendation before choosing to:

- Approve
- Edit and approve
- Override the decision

This ensures that calls requiring human judgment are not automatically saved without review.

---

## 3. Operational Summary

The operational summary displays the current state of processed calls through:

- Total call count
- Auto-saved count
- Human-review count
- Escalated count
- Non-interaction count
- Category breakdown
- Sentiment breakdown

---

# Testing

Run the pipeline tests from the project root:

```bash
python -m pytest tests/test_pipeline.py -v
```

The tests verify core processing behavior and guarded pipeline logic.

---

# Evaluation

Kalam CX includes a dedicated evaluation set of approximately fifteen representative calls.

Run the evaluation from the project root:

```bash
python -m evaluation.run_evaluation
```

The evaluation judges both the expected classification and the operational decision.

Current evaluation result:

```text
Total Calls : 15
Passed      : 15
Failed      : 0
Pass Rate   : 100.0%
```

The evaluated calls include examples of:

- Routine auto-save cases
- Billing and refund distinctions
- Technical-support cases
- Ambiguous cases requiring review
- Account-management cases
- Escalation cases
- Complaints
- Sensitive or difficult interactions

Detailed results are stored in:

```text
evaluation/evaluation_results.json
```

The evaluation answer key is used only for evaluation and is never provided to the runtime processing engine.

---

# Design Documentation

The project was designed before implementation and includes:

```text
docs/PRD.md
docs/System_Architecture.md
docs/Data_Schema.md
```

### PRD

Defines the product goals, requirements, guarded behavior, human-review workflow, operational summary, and acceptance criteria.

### System Architecture

Documents the complete processing flow and separation between documentation generation and deterministic safety decisions.

### Data Schema / ERD

Defines the system entities, structured record fields, relationships, grounding information, decisions, statuses, and data-integrity principles.

---

# Safety and Grounding Principles

Kalam CX follows several core safeguards:

1. Never write a field that is unsupported by the call or trusted context.
2. Missing information is represented as `not stated` when appropriate.
3. Structured documentation summarizes meaning without fabricating facts.
4. Original transcript evidence is preserved for grounding.
5. Classification remains traceable to handbook rules.
6. Sensitive calls cannot be automatically saved.
7. Escalation triggers cannot be suppressed by caller instructions.
8. A complaint is not automatically treated as an escalation.
9. Similar categories, such as billing disputes and refund requests, remain distinct.
10. Calls requiring human judgment remain in the human-review workflow until reviewed.

---

# Evaluation Status

**15 / 15 evaluation calls passed — 100% pass rate.**

The evaluation covers both:

- **Outcome correctness:** whether the system produced the expected classification and decision.
- **Process correctness:** whether the call followed the appropriate guarded processing path.

---

# Kalam CX

**AI-Powered After-Call Automation Platform**

From transcript intake to structured, grounded documentation — with deterministic safeguards and human review where required.