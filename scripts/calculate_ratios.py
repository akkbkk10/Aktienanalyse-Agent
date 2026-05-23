from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import create_research_request


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTEXT_ROOT = REPO_ROOT / "data" / "companies"
DEFAULT_MARKDOWN_QUEUE_PATH = REPO_ROOT / "research_queue.md"
DEFAULT_JSON_QUEUE_PATH = REPO_ROOT / "research_queue.json"
CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}
MARGIN_DEFINITIONS = {
    "gross_margin": ("Gross profit", "Revenue", "Gross profit / Revenue"),
    "operating_margin": ("Operating income", "Revenue", "Operating income / Revenue"),
    "net_margin": ("Net income", "Revenue", "Net income / Revenue"),
    "free_cash_flow_margin": ("Free cash flow", "Revenue", "Free cash flow / Revenue"),
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def calculate_ratios_from_context(
    context: dict[str, Any],
    markdown_queue_path: Path = DEFAULT_MARKDOWN_QUEUE_PATH,
    json_queue_path: Path = DEFAULT_JSON_QUEUE_PATH,
    queue_missing: bool = True,
) -> dict[str, Any]:
    ticker = context["ticker"]
    company_name = context.get("company_name", ticker)
    metrics = [metric for metric in context.get("metrics", []) if isinstance(metric, dict)]
    metrics_by_period = _metrics_by_period(metrics)
    ratios: list[dict[str, Any]] = []
    missing_inputs: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for period, period_metrics in metrics_by_period.items():
        for ratio_name, (numerator_name, denominator_name, formula) in MARGIN_DEFINITIONS.items():
            missing = [name for name in [numerator_name, denominator_name] if name not in period_metrics]
            if missing:
                missing_inputs.append(_missing_input(ticker, company_name, ratio_name, period, missing))
                continue

            numerator = period_metrics[numerator_name]
            denominator = period_metrics[denominator_name]
            if denominator["value"] == 0:
                skipped.append(
                    {
                        "ticker": ticker,
                        "ratio_name": ratio_name,
                        "period": period,
                        "reason": "Revenue is zero; ratio calculation skipped.",
                    }
                )
                continue

            ratios.append(_ratio_record(ticker, ratio_name, numerator, denominator, formula, period))

    ratios.extend(_calculate_revenue_growth(ticker, metrics_by_period))
    queue_result = (
        _queue_missing_inputs(missing_inputs, markdown_queue_path, json_queue_path)
        if queue_missing
        else _empty_queue_result(missing_inputs)
    )

    return {
        "ticker": ticker,
        "ratios": ratios,
        "missing_inputs": missing_inputs,
        "skipped": skipped,
        "queue": queue_result,
    }


def calculate_ratios_for_ticker(
    ticker: str,
    context_root: Path = DEFAULT_CONTEXT_ROOT,
    markdown_queue_path: Path = DEFAULT_MARKDOWN_QUEUE_PATH,
    json_queue_path: Path = DEFAULT_JSON_QUEUE_PATH,
    queue_missing: bool = True,
) -> dict[str, Any]:
    context_path = context_root / ticker.upper() / "context.json"
    context = load_json(context_path)
    return calculate_ratios_from_context(
        context=context,
        markdown_queue_path=markdown_queue_path,
        json_queue_path=json_queue_path,
        queue_missing=queue_missing,
    )


def _metrics_by_period(metrics: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = {}
    for metric in metrics:
        if metric.get("metric_category") in {"share_count", "market_price"}:
            continue
        period = str(metric.get("period", ""))
        metric_name = str(metric.get("metric_name", ""))
        if period and metric_name:
            grouped.setdefault(period, {})[metric_name] = metric
    return grouped


def _ratio_record(
    ticker: str,
    ratio_name: str,
    numerator: dict[str, Any],
    denominator: dict[str, Any],
    formula: str,
    period: str,
) -> dict[str, Any]:
    return {
        "ticker": ticker,
        "ratio_name": ratio_name,
        "value": numerator["value"] / denominator["value"],
        "formula": formula,
        "input_metrics_used": [numerator["metric_name"], denominator["metric_name"]],
        "input_metric_ids_used": [numerator["metric_id"], denominator["metric_id"]],
        "source_metric_references": [_source_reference(numerator), _source_reference(denominator)],
        "period": period,
        "confidence": _combined_confidence([numerator, denominator]),
    }


def _calculate_revenue_growth(ticker: str, metrics_by_period: dict[str, dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    revenue_metrics = [
        metrics["Revenue"]
        for _, metrics in sorted(metrics_by_period.items())
        if "Revenue" in metrics
    ]
    ratios = []

    for index in range(1, len(revenue_metrics)):
        current = revenue_metrics[index]
        prior = revenue_metrics[index - 1]
        if prior["value"] == 0:
            continue
        ratios.append(
            {
                "ticker": ticker,
                "ratio_name": "revenue_growth",
                "value": (current["value"] - prior["value"]) / prior["value"],
                "formula": "(Current period Revenue - Prior period Revenue) / Prior period Revenue",
                "input_metrics_used": ["Revenue", "Revenue"],
                "input_metric_ids_used": [current["metric_id"], prior["metric_id"]],
                "source_metric_references": [_source_reference(current), _source_reference(prior)],
                "period": current["period"],
                "confidence": _combined_confidence([current, prior]),
            }
        )

    return ratios


def _source_reference(metric: dict[str, Any]) -> dict[str, Any]:
    source_metadata = metric.get("source_metadata", {})
    return {
        "metric_id": metric.get("metric_id"),
        "metric_name": metric.get("metric_name"),
        "period": metric.get("period"),
        "accounting_basis": metric.get("accounting_basis"),
        "source_url": source_metadata.get("source_url"),
        "source_type": source_metadata.get("source_type"),
        "source_date": source_metadata.get("source_date"),
        "last_verified": source_metadata.get("last_verified"),
        "confidence": source_metadata.get("confidence"),
    }


def _combined_confidence(metrics: list[dict[str, Any]]) -> str:
    confidences = [metric.get("source_metadata", {}).get("confidence", "low") for metric in metrics]
    return min(confidences, key=lambda confidence: CONFIDENCE_RANK.get(confidence, -1))


def _missing_input(
    ticker: str,
    company_name: str,
    ratio_name: str,
    period: str,
    missing_metrics: list[str],
) -> dict[str, Any]:
    return {
        "ticker": ticker,
        "company_name": company_name,
        "ratio_name": ratio_name,
        "period": period,
        "missing_metrics": missing_metrics,
    }


def _queue_missing_inputs(
    missing_inputs: list[dict[str, Any]],
    markdown_queue_path: Path,
    json_queue_path: Path,
) -> dict[str, Any]:
    results = []
    for missing in missing_inputs:
        question = (
            f"Find missing input metrics for {missing['ratio_name']} in {missing['period']}: "
            f"{', '.join(missing['missing_metrics'])}."
        )
        results.append(
            create_research_request.append_request(
                company=missing["company_name"],
                ticker=missing["ticker"],
                question=question,
                markdown_queue_path=markdown_queue_path,
                json_queue_path=json_queue_path,
                source="ratio_calculation_agent",
                context=missing,
            )
        )

    return {
        "missing_input_count": len(missing_inputs),
        "created_count": sum(1 for result in results if result["created"]),
        "duplicate_count": sum(1 for result in results if not result["created"]),
        "items": results,
    }


def _empty_queue_result(missing_inputs: list[dict[str, Any]]) -> dict[str, Any]:
    return {"missing_input_count": len(missing_inputs), "created_count": 0, "duplicate_count": 0, "items": []}


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate deterministic ratios from a validated company context.")
    parser.add_argument("ticker")
    parser.add_argument("--context-root", type=Path, default=DEFAULT_CONTEXT_ROOT)
    parser.add_argument("--markdown-queue-path", type=Path, default=DEFAULT_MARKDOWN_QUEUE_PATH)
    parser.add_argument("--json-queue-path", type=Path, default=DEFAULT_JSON_QUEUE_PATH)
    parser.add_argument("--no-queue", action="store_true", help="Do not create queue entries for missing inputs.")
    args = parser.parse_args()

    result = calculate_ratios_for_ticker(
        ticker=args.ticker,
        context_root=args.context_root,
        markdown_queue_path=args.markdown_queue_path,
        json_queue_path=args.json_queue_path,
        queue_missing=not args.no_queue,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
