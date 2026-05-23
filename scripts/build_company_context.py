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

import validate_sources


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "data" / "companies"
CONTEXT_SCHEMA_VERSION = "0.1.0"
SOURCE_METADATA_FIELDS = ["source_url", "source_type", "source_date", "last_verified", "confidence"]


class ContextValidationError(ValueError):
    pass


def build_company_context(
    metrics_path: Path,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    last_updated: str | None = None,
) -> dict[str, Any]:
    records = validate_sources.normalize_records(validate_sources.load_json(metrics_path))
    source_errors = validate_sources.validate_file(metrics_path)
    if source_errors:
        messages = ", ".join(f"record {error.index} {error.field}: {error.message}" for error in source_errors)
        raise ContextValidationError(f"Invalid source metadata: {messages}")

    context = build_context_from_records(records=records, metrics_path=metrics_path, last_updated=last_updated)
    validate_company_context(context)
    write_company_context(context=context, output_root=output_root)
    return context


def build_context_from_records(
    records: list[dict[str, Any]],
    metrics_path: Path | None = None,
    last_updated: str | None = None,
) -> dict[str, Any]:
    if not records:
        raise ContextValidationError("Company context requires at least one metric.")

    ticker = _single_required_value(records, "ticker")
    company_name = _single_required_value(records, "company")

    context = {
        "schema_version": CONTEXT_SCHEMA_VERSION,
        "ticker": ticker,
        "company_name": company_name,
        "last_updated": last_updated or date.today().isoformat(),
        "metrics": [_metric_to_context_metric(record) for record in records],
        "source_metadata": {
            "source_file": str(metrics_path) if metrics_path else None,
            "metric_count": len(records),
        },
    }
    return context


def validate_company_context(context: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not context.get("ticker"):
        errors.append("Missing ticker.")
    if not context.get("company_name"):
        errors.append("Missing company name.")
    if not context.get("schema_version"):
        errors.append("Missing schema version.")
    if not context.get("last_updated"):
        errors.append("Missing last_updated.")

    metrics = context.get("metrics")
    if not isinstance(metrics, list) or not metrics:
        errors.append("Missing metrics.")
    elif isinstance(metrics, list):
        for index, metric in enumerate(metrics):
            errors.extend(_validate_context_metric(index, metric))

    if errors:
        raise ContextValidationError("; ".join(errors))

    return []


def write_company_context(context: dict[str, Any], output_root: Path = DEFAULT_OUTPUT_ROOT) -> Path:
    ticker = context["ticker"]
    output_path = output_root / ticker / "context.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(context, handle, indent=2)
        handle.write("\n")
    return output_path


def _single_required_value(records: list[dict[str, Any]], field: str) -> str:
    values = {str(record.get(field, "")).strip() for record in records if str(record.get(field, "")).strip()}
    if not values:
        raise ContextValidationError(f"Missing {field}.")
    if len(values) > 1:
        raise ContextValidationError(f"Multiple {field} values are not allowed in one company context.")
    return values.pop()


def _metric_to_context_metric(record: dict[str, Any]) -> dict[str, Any]:
    source_metadata = {field: record[field] for field in SOURCE_METADATA_FIELDS}
    metric = {
        "metric_id": record["metric_id"],
        "metric_name": record["metric_name"],
        "value": record["value"],
        "unit": record["unit"],
        "period": record["period"],
        "accounting_basis": record["accounting_basis"],
        "statement_type": record["statement_type"],
        "source_metadata": source_metadata,
    }

    if "metric_category" in record:
        metric["metric_category"] = record["metric_category"]

    if "notes" in record:
        metric["notes"] = record["notes"]

    return metric


def _validate_context_metric(index: int, metric: Any) -> list[str]:
    if not isinstance(metric, dict):
        return [f"Metric {index} must be an object."]

    errors = []
    for field in ["metric_id", "metric_name", "value", "unit", "period", "accounting_basis", "statement_type"]:
        if field not in metric or metric[field] in (None, ""):
            errors.append(f"Metric {index} missing {field}.")

    source_metadata = metric.get("source_metadata")
    if not isinstance(source_metadata, dict):
        errors.append(f"Metric {index} missing source metadata.")
        return errors

    for field in SOURCE_METADATA_FIELDS:
        if not source_metadata.get(field):
            errors.append(f"Metric {index} missing source metadata field {field}.")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a persistent company context from sourced metrics.")
    parser.add_argument("metrics_path", type=Path, help="JSON file containing sourced financial metric records.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--last-updated")
    args = parser.parse_args()

    try:
        context = build_company_context(
            metrics_path=args.metrics_path,
            output_root=args.output_root,
            last_updated=args.last_updated,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"created": False, "error": str(exc)}, indent=2))
        return 1

    output_path = args.output_root / context["ticker"] / "context.json"
    print(json.dumps({"created": True, "output_path": str(output_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

