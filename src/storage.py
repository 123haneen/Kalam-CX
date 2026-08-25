"""Small SQLite record store for the demo backend."""
from pathlib import Path
import json, sqlite3
from datetime import datetime, timezone
from src.schemas import FinalRecord, OperationalSummary, RecordStatus, DecisionType
ROOT=Path(__file__).resolve().parents[1]
DB_PATH=ROOT/"data"/"runtime"/"kalam.db"

def _conn():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS records(call_id TEXT PRIMARY KEY, payload TEXT NOT NULL)""")
    c.commit(); return c

def upsert(record:FinalRecord)->FinalRecord:
    c=_conn(); c.execute("INSERT OR REPLACE INTO records(call_id,payload) VALUES(?,?)",(record.call_id,record.model_dump_json())); c.commit(); c.close(); return record

def get(call_id:str):
    c=_conn(); row=c.execute("SELECT payload FROM records WHERE call_id=?",(call_id,)).fetchone(); c.close()
    return FinalRecord.model_validate_json(row[0]) if row else None

def all_records()->list[FinalRecord]:
    c=_conn(); rows=c.execute("SELECT payload FROM records ORDER BY call_id").fetchall(); c.close(); return [FinalRecord.model_validate_json(r[0]) for r in rows]

def clear():
    c=_conn(); c.execute("DELETE FROM records"); c.commit(); c.close()

def summary()->OperationalSummary:
    rows=all_records(); cats={}; sents={}
    for r in rows:
        cats[r.category]=cats.get(r.category,0)+1; sents[r.sentiment]=sents.get(r.sentiment,0)+1
    return OperationalSummary(total_calls=len(rows), auto_saved=sum(r.status==RecordStatus.AUTO_SAVED for r in rows), human_review=sum(r.status==RecordStatus.PENDING_REVIEW for r in rows), escalated=sum(r.status==RecordStatus.ESCALATED for r in rows), non_interactions=sum(r.status==RecordStatus.NON_INTERACTION for r in rows), categories=cats, sentiments=sents)
