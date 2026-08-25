# Kalam CX — AI-Powered After-Call Automation Backend

A guarded after-call documentation backend built on the provided Kalam dataset. Runtime processing uses the real transcripts, customer records, and handbook. `answer_key.json` is **never used to generate records**; it is only used by the evaluation script.

## What is implemented
- Real transcript intake (`K-001` … `K-027`)
- Customer lookup and prior-ticket context
- Searchable parsed handbook clauses
- Structured documentation draft: summary, issue, root cause, resolution/pending action, sentiment, category/subcategory, priority, follow-ups, keywords/tags, disposition, escalation flag
- Code-level grounding, ambiguity, sensitive-topic and prompt-injection/caller-instruction checks
- Deterministic auto-save / review / escalation / non-interaction gate
- SQLite app record store
- Human review queue with approve/edit/override API
- Operational summary counts
- FastAPI endpoints ready for a frontend

## Run
```bash
python -m pip install -r requirements.txt
python -m uvicorn src.api:app --reload
```
Open API docs at `http://127.0.0.1:8000/docs`.

## Useful endpoints
- `GET /health`
- `GET /calls`
- `GET /calls/{call_id}`
- `POST /process/{call_id}`
- `POST /process-all`
- `GET /records`
- `GET /review-queue`
- `POST /review/{call_id}`
- `GET /summary`
- `DELETE /records`

## Tests and evaluation
```bash
python -m pytest tests/test_pipeline.py -v
python -m src.evaluate
```

## Frontend flow
1. Load calls with `GET /calls`.
2. Process one with `POST /process/K-001`.
3. Show the returned structured record and decision.
4. Load review cases from `GET /review-queue`.
5. Approve/edit through `POST /review/{call_id}`.
6. Show counts from `GET /summary`.

