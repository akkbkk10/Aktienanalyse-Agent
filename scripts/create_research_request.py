from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import validate_sources


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MARKDOWN_QUEUE_PATH = REPO_ROOT / "research_queue.md"
DEFAULT_JSON_QUEUE_PATH = REPO_ROOT / "research_queue.json"
REQUIRED_EVIDENCE = ["source_url", "source_date", "unit", "period", "confidence"]


def build_request_entry(
    company: str,
    ticker: str,
    question: str,
    source: str = "manual",
    context: dict[str, Any] | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    entry = {
        "id": _entry_id(company=company, ticker=ticker, question=question, source=source, context=context),
        "company": company,
        "ticker": ticker.upper(),
        "question": question,
        "status": "open",
        "source": source,
        "created_at": created_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "required_evidence": REQUIRED_EVIDENCE,
    }
    if context:
        entry["context"] = context
    return entry


def format_markdown_entry(entry: dict[str, Any]) -> str:
    lines = [
        f"\n## {entry['company']} ({entry['ticker']})\n",
        f"- ID: {entry['id']}",
        f"- Created: {entry['created_at']}",
        f"- Question: {entry['question']}",
        f"- Status: {entry['status']}",
        f"- Source: {entry['source']}",
        f"- Required evidence: {', '.join(entry['required_evidence'])}",
    ]

    context = entry.get("context")
    if context:
        lines.append(f"- Context: {json.dumps(context, sort_keys=True)}")

    return "\n".join(lines) + "\n"


def append_request(
    company: str,
    ticker: str,
    question: str,
    markdown_queue_path: Path = DEFAULT_MARKDOWN_QUEUE_PATH,
    json_queue_path: Path = DEFAULT_JSON_QUEUE_PATH,
    source: str = "manual",
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    entry = build_request_entry(company=company, ticker=ticker, question=question, source=source, context=context)
    queue = load_json_queue(json_queue_path)

    if _has_duplicate(queue["items"], entry["id"]):
        return {"created": False, "entry": entry}

    queue["items"].append(entry)
    save_json_queue(queue, json_queue_path)
    append_markdown_entry(entry, markdown_queue_path)
    return {"created": True, "entry": entry}


def append_requests_from_validation_errors(
    input_path: Path,
    markdown_queue_path: Path = DEFAULT_MARKDOWN_QUEUE_PATH,
    json_queue_path: Path = DEFAULT_JSON_QUEUE_PATH,
) -> dict[str, Any]:
    payload = validate_sources.load_json(input_path)
    records = validate_sources.normalize_records(payload)
    errors = validate_sources.validate_file(input_path)
    results = []

    for error in errors:
        record = records[error.index] if error.index < len(records) else {}
        company = str(record.get("company") or "Unknown company")
        ticker = str(record.get("ticker") or "UNKNOWN")
        metric_name = str(record.get("metric_name") or "unknown metric")
        question = f"Resolve validation error for {metric_name}: {error.field} - {error.message}"
        context = {
            "record_index": error.index,
            "field": error.field,
            "message": error.message,
            "metric_name": metric_name,
            "input_path": str(input_path),
        }
        results.append(
            append_request(
                company=company,
                ticker=ticker,
                question=question,
                markdown_queue_path=markdown_queue_path,
                json_queue_path=json_queue_path,
                source="validation_error",
                context=context,
            )
        )

    return {
        "validation_error_count": len(errors),
        "created_count": sum(1 for result in results if result["created"]),
        "duplicate_count": sum(1 for result in results if not result["created"]),
        "items": results,
    }


def load_json_queue(json_queue_path: Path = DEFAULT_JSON_QUEUE_PATH) -> dict[str, list[dict[str, Any]]]:
    if not json_queue_path.exists():
        return {"items": []}

    with json_queue_path.open("r", encoding="utf-8") as handle:
        queue = json.load(handle)

    if isinstance(queue, list):
        return {"items": queue}
    if isinstance(queue, dict) and isinstance(queue.get("items"), list):
        return queue
    raise ValueError("Research queue JSON must be an object with an items list.")


def save_json_queue(queue: dict[str, list[dict[str, Any]]], json_queue_path: Path = DEFAULT_JSON_QUEUE_PATH) -> None:
    json_queue_path.parent.mkdir(parents=True, exist_ok=True)
    with json_queue_path.open("w", encoding="utf-8") as handle:
        json.dump(queue, handle, indent=2)
        handle.write("\n")


def append_markdown_entry(entry: dict[str, Any], markdown_queue_path: Path = DEFAULT_MARKDOWN_QUEUE_PATH) -> None:
    markdown_queue_path.parent.mkdir(parents=True, exist_ok=True)
    with markdown_queue_path.open("a", encoding="utf-8") as handle:
        handle.write(format_markdown_entry(entry))


def _entry_id(
    company: str,
    ticker: str,
    question: str,
    source: str,
    context: dict[str, Any] | None,
) -> str:
    duplicate_key = {
        "company": company.strip().lower(),
        "ticker": ticker.strip().upper(),
        "question": question.strip().lower(),
        "source": source,
        "context": _duplicate_context(context),
    }
    digest = sha256(json.dumps(duplicate_key, sort_keys=True).encode("utf-8")).hexdigest()
    return digest[:16]


def _duplicate_context(context: dict[str, Any] | None) -> dict[str, Any]:
    if not context:
        return {}

    return {key: value for key, value in context.items() if key != "input_path"}


def _has_duplicate(items: list[dict[str, Any]], entry_id: str) -> bool:
    return any(item.get("id") == entry_id for item in items)


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a stock research request to the queue.")
    parser.add_argument("--company")
    parser.add_argument("--ticker")
    parser.add_argument("--question")
    parser.add_argument("--from-validation-errors", type=Path)
    parser.add_argument("--markdown-queue-path", type=Path, default=DEFAULT_MARKDOWN_QUEUE_PATH)
    parser.add_argument("--json-queue-path", type=Path, default=DEFAULT_JSON_QUEUE_PATH)
    args = parser.parse_args()

    if args.from_validation_errors:
        result = append_requests_from_validation_errors(
            input_path=args.from_validation_errors,
            markdown_queue_path=args.markdown_queue_path,
            json_queue_path=args.json_queue_path,
        )
        print(json.dumps(result, indent=2))
        return 0

    if not args.company or not args.ticker or not args.question:
        parser.error("--company, --ticker, and --question are required unless --from-validation-errors is used.")

    result = append_request(
        company=args.company,
        ticker=args.ticker,
        question=args.question,
        markdown_queue_path=args.markdown_queue_path,
        json_queue_path=args.json_queue_path,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
