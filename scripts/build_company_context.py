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
DEFAULT_CONTEXT_SCHEMA_PATH = REPO_ROOT / "config" / "company_context_schema.json"
CONTEXT_SCHEMA_VERSION = "0.1.0"
SOURCE_METADATA_FIELDS = ["source_url", "source_type", "source_date", "last_verified", "confidence"]
MARKET_PRICE_SNAPSHOT_FIELDS = ["currency", "exchange", "price_type", "as_of_datetime", "fetched_at", "provider", "retrieval_method"]


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


def validate_company_context(context: dict[str, Any], schema: dict[str, Any] | None = None) -> list[str]:
    schema = schema or validate_sources.load_json(DEFAULT_CONTEXT_SCHEMA_PATH)
    errors: list[str] = []

    for field in schema.get("required_fields", []):
        if field not in context or context[field] in (None, ""):
            errors.append(f"Missing {field}.")
        elif field in schema.get("field_types", {}):
            errors.extend(_validate_contract_type(field, context[field], schema["field_types"][field]))

    metrics = context.get("metrics")
    if not isinstance(metrics, list) or not metrics:
        errors.append("Missing metrics.")
    elif isinstance(metrics, list):
        for index, metric in enumerate(metrics):
            errors.extend(_validate_context_metric(index, metric, schema))

    source_metadata = context.get("source_metadata")
    if not isinstance(source_metadata, dict):
        errors.append("Missing source_metadata.")
    else:
        for field in schema.get("source_metadata_required_fields", []):
            if field not in source_metadata:
                errors.append(f"Missing source_metadata field {field}.")
            elif field in schema.get("source_metadata_field_types", {}):
                errors.extend(
                    _validate_contract_type(
                        f"source_metadata.{field}",
                        source_metadata[field],
                        schema["source_metadata_field_types"][field],
                    )
                )

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

    for field in MARKET_PRICE_SNAPSHOT_FIELDS:
        if field in record:
            metric[field] = record[field]

    if "notes" in record:
        metric["notes"] = record["notes"]

    return metric


def _validate_context_metric(index: int, metric: Any, schema: dict[str, Any]) -> list[str]:
    if not isinstance(metric, dict):
        return [f"Metric {index} must be an object."]

    errors = []
    for field in schema.get("metric_required_fields", []):
        if field not in metric or metric[field] in (None, ""):
            errors.append(f"Metric {index} missing {field}.")
        elif field in schema.get("metric_field_types", {}):
            errors.extend(
                _validate_contract_type(
                    f"Metric {index} {field}",
                    metric[field],
                    schema["metric_field_types"][field],
                )
            )

    source_metadata = metric.get("source_metadata")
    if not isinstance(source_metadata, dict):
        errors.append(f"Metric {index} missing source metadata.")
        return errors

    for field in schema.get("metric_source_metadata_required_fields", SOURCE_METADATA_FIELDS):
        if not source_metadata.get(field):
            errors.append(f"Metric {index} missing source metadata field {field}.")
        elif field in schema.get("metric_source_metadata_field_types", {}):
            errors.extend(
                _validate_contract_type(
                    f"Metric {index} source_metadata.{field}",
                    source_metadata[field],
                    schema["metric_source_metadata_field_types"][field],
                )
            )

    return errors


def _validate_contract_type(field: str, value: Any, expected_type: str) -> list[str]:
    errors: list[str] = []

    if expected_type == "string" and not isinstance(value, str):
        errors.append(f"{field} must be a string.")
    elif expected_type == "date":
        if not isinstance(value, str):
            errors.append(f"{field} must be a date string.")
        else:
            try:
                date.fromisoformat(value)
            except ValueError:
                errors.append(f"{field} must use ISO date format YYYY-MM-DD.")
    elif expected_type == "array" and not isinstance(value, list):
        errors.append(f"{field} must be an array.")
    elif expected_type == "object" and not isinstance(value, dict):
        errors.append(f"{field} must be an object.")
    elif expected_type == "number" and not _is_number(value):
        errors.append(f"{field} must be a number.")
    elif expected_type == "string_or_null" and value is not None and not isinstance(value, str):
        errors.append(f"{field} must be a string or null.")

    return errors


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


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

