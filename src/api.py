"""FastAPI application consumed by the frontend."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from src.data_access import list_calls, load_call
from src.pipeline import process_call
from src.storage import all_records, get, summary, upsert, clear
from src.schemas import ReviewUpdate, RecordStatus, DecisionType

app=FastAPI(title="Kalam CX Backend",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

@app.get("/health")
def health(): return {"status":"ok","service":"Kalam CX Backend"}

@app.get("/calls")
def calls():
    return [{"call_id":c.call_id,"customer_id":c.customer_id,"channel":c.channel,"date":c.timestamp,"preview":c.transcript[:140]} for c in list_calls()]

@app.get("/calls/{call_id}")
def call(call_id:str):
    try: return load_call(call_id)
    except FileNotFoundError as e: raise HTTPException(404,str(e))

@app.post("/process/{call_id}")
def process(call_id:str):
    try: return process_call(call_id)
    except FileNotFoundError as e: raise HTTPException(404,str(e))

@app.post("/process-all")
def process_all(): return [process_call(c.call_id) for c in list_calls()]

@app.get("/records")
def records(): return all_records()

@app.get("/records/{call_id}")
def record(call_id:str):
    r=get(call_id)
    if not r: raise HTTPException(404,"Record not found")
    return r

@app.get("/review-queue")
def review_queue(): return [r for r in all_records() if r.status in {RecordStatus.PENDING_REVIEW,RecordStatus.ESCALATED}]

@app.post("/review/{call_id}")
def review(call_id:str, update:ReviewUpdate):
    r=get(call_id)
    if not r: raise HTTPException(404,"Process the call before reviewing it")
    allowed=set(r.model_fields)
    for k,v in update.edits.items():
        if k in allowed and k not in {"record_id","call_id","customer_id","created_at"}: setattr(r,k,v)
    if update.override_decision is not None: r.decision=update.override_decision
    if update.approved:
        r.status=RecordStatus.APPROVED
    r.updated_at=datetime.now(timezone.utc).isoformat(); return upsert(r)

@app.get("/summary")
def operational_summary(): return summary()

@app.delete("/records")
def reset_records(): clear(); return {"status":"cleared"}
