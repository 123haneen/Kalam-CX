"""File-backed access to the provided Kalam dataset and handbook."""
from pathlib import Path
import json
import re
from typing import List
from src.schemas import CallTranscript, HandbookRule

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def load_customers() -> list[dict]:
    with (DATA_DIR / "customers.json").open(encoding="utf-8") as f:
        data = json.load(f)
    return data["customers"] if isinstance(data, dict) and "customers" in data else data


def load_answer_key() -> dict:
    with (DATA_DIR / "answer_key.json").open(encoding="utf-8") as f:
        return json.load(f)


def _metadata_and_body(text: str) -> tuple[dict, str]:
    lines = text.splitlines()
    meta = {}
    body_start = 0
    for i, line in enumerate(lines):
        if not line.strip():
            body_start = i + 1
            break
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip().lower()] = value.strip()
    return meta, "\n".join(lines[body_start:]).strip()


def load_call(call_id: str) -> CallTranscript:
    path = DATA_DIR / "transcripts" / f"{call_id}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Unknown call_id: {call_id}")
    text = path.read_text(encoding="utf-8")
    meta, body = _metadata_and_body(text)
    cid = meta.get("customer id")
    if cid in {"None", "none", "null", "", "unknown", "Unknown"}:
        cid = None
    return CallTranscript(
        call_id=meta.get("call id", call_id),
        customer_id=cid,
        transcript=body,
        timestamp=meta.get("date", ""),
        channel=meta.get("channel", ""),
    )


def list_calls() -> List[CallTranscript]:
    return [load_call(p.stem) for p in sorted((DATA_DIR / "transcripts").glob("K-*.txt"))]


def load_handbook_rules() -> list[HandbookRule]:
    """Parse numbered clauses from the markdown handbook into searchable rules."""
    rules: list[HandbookRule] = []
    pattern = re.compile(r"\*\*Clause\s+(\d+\.\d+)\s+—\s+([^*]+)\*\*\s*(.*?)(?=\n\*\*Clause\s+\d+\.\d+\s+—|\Z)", re.S)
    for path in sorted((DATA_DIR / "handbook").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        section_match = re.search(r"Section\s+(\d+)\s+·\s+([^\n]+)", text)
        section = section_match.group(2).strip() if section_match else path.stem
        for rid, title, body in pattern.findall(text):
            rule_text = f"{title.strip()}. {re.sub(r'\s+', ' ', body).strip()}"
            rules.append(HandbookRule(rule_id=rid, section=section, rule_text=rule_text))
    return rules
