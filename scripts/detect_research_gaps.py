from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import create_research_request


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WATCHLIST_PATH = REPO_ROOT / "config" / "watchlist.json"
DEFAULT_CONTEXT_ROOT = REPO_ROOT / "data" / "companies"
DEFAULT_MARKDOWN_QUEUE_PATH = REPO_ROOT / "research_queue.md"
DEFAULT_JSON_QUEUE_PATH = REPO_ROOT / "research_queue.json"
REQUIRED_SOURCE_METADATA_FIELDS = ["source_url", "source_type", "source_date", "last_verified", "confidence"]
CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def detect_gaps(
    watchlist_path: Path = DEFAULT_WATCHLIST_PATH,
    context_root: Path = DEFAULT_CONTEXT_ROOT,
    today: date | None = None,
) -> list[dict[str, Any]]:
    watchlist = load_json(watchlist_path)
    validation_date = today or date.today()
    gaps: list[dict[str, Any]] = []

    for ticker, rules in watchlist.get("tickers", {}).items():
        context_path = context_root / ticker / "context.json"
        if not context_path.exists():
            gaps.append(_gap(ticker, rules, "missing_context", None, "Company context file is missing."))
            continue

        context = load_json(context_path)
        metrics = context.get("metrics", [])
        metric_by_name = {metric.get("metric_name"): metric for metric in metrics if isinstance(metric, dict)}

        for metric_name in rules.get("required_metrics", []):
            metric = metric_by_name.get(metric_name)
            if metric is None:
                gaps.append(_gap(ticker, rules, "missing_metric", metric_name, "Required metric is missing."))
                continue

            gaps.extend(_detect_metric_gaps(ticker, rules, metric, validation_date))

    return gaps


def create_queue_entries_for_gaps(
    gaps: list[dict[str, Any]],
    markdown_queue_path: Path = DEFAULT_MARKDOWN_QUEUE_PATH,
    json_queue_path: Path = DEFAULT_JSON_QUEUE_PATH,
) -> dict[str, Any]:
    results = []
    for gap in gaps:
        results.append(
            create_research_request.append_request(
                company=gap["company_name"],
                ticker=gap["ticker"],
                question=_question_for_gap(gap),
                markdown_queue_path=markdown_queue_path,
                json_queue_path=json_queue_path,
                source="research_gap_agent",
                context=gap,
            )
        )

    return {
        "gap_count": len(gaps),
        "created_count": sum(1 for result in results if result["created"]),
        "duplicate_count": sum(1 for result in results if not result["created"]),
        "items": results,
    }


def detect_and_queue_gaps(
    watchlist_path: Path = DEFAULT_WATCHLIST_PATH,
    context_root: Path = DEFAULT_CONTEXT_ROOT,
    markdown_queue_path: Path = DEFAULT_MARKDOWN_QUEUE_PATH,
    json_queue_path: Path = DEFAULT_JSON_QUEUE_PATH,
    today: date | None = None,
) -> dict[str, Any]:
    gaps = detect_gaps(watchlist_path=watchlist_path, context_root=context_root, today=today)
    queue_result = create_queue_entries_for_gaps(
        gaps=gaps,
        markdown_queue_path=markdown_queue_path,
        json_queue_path=json_queue_path,
    )
    return {"gaps": gaps, "queue": queue_result}


def _detect_metric_gaps(
    ticker: str,
    rules: dict[str, Any],
    metric: dict[str, Any],
    validation_date: date,
) -> list[dict[str, Any]]:
    gaps = []
    metric_name = metric.get("metric_name")
    source_metadata = metric.get("source_metadata")

    if not isinstance(source_metadata, dict):
        return [
            _gap(
                ticker,
                rules,
                "missing_source_metadata",
                metric_name,
                "Metric source metadata is missing.",
            )
        ]

    missing_fields = [field for field in REQUIRED_SOURCE_METADATA_FIELDS if not source_metadata.get(field)]
    if missing_fields:
        gaps.append(
            _gap(
                ticker,
                rules,
                "missing_source_metadata",
                metric_name,
                f"Metric source metadata missing fields: {', '.join(missing_fields)}.",
            )
        )

    last_verified = source_metadata.get("last_verified")
    max_age_days = int(rules.get("max_last_verified_age_days", 180))
    if isinstance(last_verified, str):
        try:
            verified_date = date.fromisoformat(last_verified)
        except ValueError:
            gaps.append(_gap(ticker, rules, "stale_metric", metric_name, "Metric last_verified is invalid."))
        else:
            if (validation_date - verified_date).days > max_age_days:
                gaps.append(
                    _gap(
                        ticker,
                        rules,
                        "stale_metric",
                        metric_name,
                        f"Metric source verification is older than {max_age_days} days.",
                    )
                )

    confidence = source_metadata.get("confidence")
    minimum_confidence = rules.get("minimum_confidence", "medium")
    if _confidence_rank(confidence) < _confidence_rank(minimum_confidence):
        gaps.append(
            _gap(
                ticker,
                rules,
                "low_confidence",
                metric_name,
                f"Metric confidence is below required minimum {minimum_confidence}.",
            )
        )

    return gaps


def _gap(
    ticker: str,
    rules: dict[str, Any],
    gap_type: str,
    metric_name: str | None,
    message: str,
) -> dict[str, Any]:
    return {
        "ticker": ticker,
        "company_name": rules.get("company_name", ticker),
        "gap_type": gap_type,
        "metric_name": metric_name,
        "message": message,
    }


def _question_for_gap(gap: dict[str, Any]) -> str:
    metric = gap["metric_name"] or "company context"
    return f"Resolve research gap for {metric}: {gap['gap_type']} - {gap['message']}"


def _confidence_rank(confidence: Any) -> int:
    if not isinstance(confidence, str):
        return -1
    return CONFIDENCE_RANK.get(confidence, -1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect company context research gaps and queue follow-up work.")
    parser.add_argument("--watchlist-path", type=Path, default=DEFAULT_WATCHLIST_PATH)
    parser.add_argument("--context-root", type=Path, default=DEFAULT_CONTEXT_ROOT)
    parser.add_argument("--markdown-queue-path", type=Path, default=DEFAULT_MARKDOWN_QUEUE_PATH)
    parser.add_argument("--json-queue-path", type=Path, default=DEFAULT_JSON_QUEUE_PATH)
    parser.add_argument("--today", help="Override validation date in YYYY-MM-DD format.")
    args = parser.parse_args()

    validation_date = date.fromisoformat(args.today) if args.today else None
    result = detect_and_queue_gaps(
        watchlist_path=args.watchlist_path,
        context_root=args.context_root,
        markdown_queue_path=args.markdown_queue_path,
        json_queue_path=args.json_queue_path,
        today=validation_date,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

