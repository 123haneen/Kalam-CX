"""Evaluate the backend against the supplied answer key (not used by runtime processing)."""
from src.data_access import load_answer_key
from src.pipeline import process_call

def main():
    key=load_answer_key(); fields=["category","subcategory","disposition","sentiment","priority","decision"]
    total=0; passed=0
    for cid,exp in key.items():
        r=process_call(cid,persist=False); actual={"category":r.category,"subcategory":r.subcategory,"disposition":r.disposition,"sentiment":r.sentiment,"priority":r.priority,"decision":r.decision.value}
        ok=all(actual[f]==exp[f] for f in fields)
        total+=1; passed+=ok
        print(f"{cid}: {'PASS' if ok else 'FAIL'}")
        if not ok:
            for f in fields:
                if actual[f]!=exp[f]: print(f"  {f}: got={actual[f]!r} expected={exp[f]!r}")
    print(f"\nExact records: {passed}/{total} ({passed/total:.1%})")
if __name__=="__main__": main()
