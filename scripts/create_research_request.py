from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE_PATH = REPO_ROOT / "research_queue.md"


def build_request(company: str, ticker: str, question: str) -> str:
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        f"\n## {company} ({ticker})\n\n"
        f"- Created: {created_at}\n"
        f"- Question: {question}\n"
        "- Status: open\n"
        "- Required evidence: source_url, source_date, unit, period, confidence\n"
    )


def append_request(
    company: str,
    ticker: str,
    question: str,
    queue_path: Path = DEFAULT_QUEUE_PATH,
) -> str:
    entry = build_request(company=company, ticker=ticker, question=question)
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    with queue_path.open("a", encoding="utf-8") as handle:
        handle.write(entry)
    return entry


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a stock research request to the queue.")
    parser.add_argument("--company", required=True)
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--queue-path", type=Path, default=DEFAULT_QUEUE_PATH)
    args = parser.parse_args()

    entry = append_request(
        company=args.company,
        ticker=args.ticker,
        question=args.question,
        queue_path=args.queue_path,
    )
    print(entry.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

