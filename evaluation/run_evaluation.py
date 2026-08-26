import json
from pathlib import Path

from src.pipeline import process_call
from src.loader import load_json


PROJECT_ROOT = Path(__file__).resolve().parents[1]

ANSWER_KEY_FILE = PROJECT_ROOT / "data" / "answer_key.json"
OUTPUT_FILE = PROJECT_ROOT / "evaluation" / "evaluation_results.json"


EVALUATION_CALLS = [
    "K-001",
    "K-002",
    "K-004",
    "K-007",
    "K-009",
    "K-010",
    "K-011",
    "K-012",
    "K-013",
    "K-014",
    "K-016",
    "K-017",
    "K-018",
    "K-019",
    "K-020",
]


def evaluate_call(call_id, answer_key):
    expected = answer_key[call_id]

    record = process_call(
        call_id=call_id,
        persist=False,
    )

    actual = {
        "category": record.category,
        "subcategory": record.subcategory,
        "disposition": record.disposition,
        "sentiment": record.sentiment,
        "priority": record.priority,
        "escalate": record.escalation_flag,
        "decision": record.decision.value,
    }

    comparisons = {
        "category": actual["category"] == expected["category"],
        "subcategory": actual["subcategory"] == expected["subcategory"],
        "disposition": actual["disposition"] == expected["disposition"],
        "sentiment": actual["sentiment"] == expected["sentiment"],
        "priority": actual["priority"] == expected["priority"],
        "escalate": actual["escalate"] == expected["escalate"],
        "decision": actual["decision"] == expected["decision"],
    }

    passed = all(comparisons.values())

    mismatches = {}

    for field, matched in comparisons.items():
        if not matched:
            mismatches[field] = {
                "expected": expected[field],
                "actual": actual[field],
            }

    return {
        "call_id": call_id,
        "passed": passed,
        "expected": {
            "category": expected["category"],
            "subcategory": expected["subcategory"],
            "disposition": expected["disposition"],
            "sentiment": expected["sentiment"],
            "priority": expected["priority"],
            "escalate": expected["escalate"],
            "decision": expected["decision"],
        },
        "actual": actual,
        "comparisons": comparisons,
        "mismatches": mismatches,
        "grounding": record.grounding,
        "rule_references": record.rule_references,
        "decision_reason": record.decision_reason,
        "escalation_reason": record.escalation_reason,
    }


def main():
    answer_key = load_json(ANSWER_KEY_FILE)

    results = []

    print("\nKALAM CX EVALUATION")
    print("=" * 95)

    for call_id in EVALUATION_CALLS:
        result = evaluate_call(
            call_id=call_id,
            answer_key=answer_key,
        )

        results.append(result)

        status = "PASS" if result["passed"] else "FAIL"

        print(
            f"{call_id:<8}"
            f"{status:<7}"
            f"{result['actual']['category']:<30}"
            f"{result['actual']['decision']}"
        )

        if not result["passed"]:
            for field, mismatch in result["mismatches"].items():
                print(
                    f"   {field}: "
                    f"expected={mismatch['expected']!r} "
                    f"actual={mismatch['actual']!r}"
                )

    total = len(results)
    passed = sum(
        1
        for result in results
        if result["passed"]
    )
    failed = total - passed

    pass_rate = (
        (passed / total) * 100
        if total
        else 0
    )

    output = {
        "total_calls": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round(pass_rate, 1),
        "evaluation_calls": EVALUATION_CALLS,
        "results": results,
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("\n" + "=" * 95)
    print(f"Total Calls : {total}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")
    print(f"Pass Rate   : {pass_rate:.1f}%")
    print(f"\nSaved results to:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    main()