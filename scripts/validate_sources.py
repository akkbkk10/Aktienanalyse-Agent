from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "config" / "financial_metric_schema.json"
DEFAULT_SOURCE_RULES_PATH = REPO_ROOT / "config" / "source_rules.json"


class ValidationErrorDetail:
    def __init__(self, index: int, field: str, message: str) -> None:
        self.index = index
        self.field = field
        self.message = message

    def to_dict(self) -> dict[str, Any]:
        return {"index": self.index, "field": self.field, "message": self.message}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        return [payload]
    if isinstance(payload, list) and all(isinstance(item, dict) for item in payload):
        return payload
    raise ValueError("Input must be a JSON object or a list of JSON objects.")


def validate_records(
    records: list[dict[str, Any]],
    schema: dict[str, Any],
    source_rules: dict[str, Any],
    today: date | None = None,
) -> list[ValidationErrorDetail]:
    errors: list[ValidationErrorDetail] = []
    validation_date = today or date.today()
    required_fields = schema.get("required", [])
    properties = schema.get("properties", {})
    allowed_fields = set(properties)
    required_evidence = source_rules.get("required_evidence_fields", [])
    allowed_schemes = set(source_rules.get("allowed_url_schemes", []))
    max_last_verified_age_days = source_rules.get("max_last_verified_age_days")

    for index, record in enumerate(records):
        for field in required_fields:
            if field not in record:
                errors.append(ValidationErrorDetail(index, field, "Missing required field."))

        for field in required_evidence:
            if not record.get(field):
                errors.append(ValidationErrorDetail(index, field, "Missing required evidence metadata."))

        for field in record:
            if field not in allowed_fields:
                errors.append(ValidationErrorDetail(index, field, "Unexpected field."))

        for field, rule in properties.items():
            if field in record:
                errors.extend(_validate_field(index, field, record[field], rule, allowed_schemes))

        if "last_verified" in record and max_last_verified_age_days is not None:
            errors.extend(
                _validate_last_verified_freshness(
                    index=index,
                    value=record["last_verified"],
                    validation_date=validation_date,
                    max_age_days=max_last_verified_age_days,
                )
            )

    return errors


def _validate_field(
    index: int,
    field: str,
    value: Any,
    rule: dict[str, Any],
    allowed_schemes: set[str],
) -> list[ValidationErrorDetail]:
    errors: list[ValidationErrorDetail] = []
    expected_type = rule.get("type")

    if expected_type == "string" and not isinstance(value, str):
        errors.append(ValidationErrorDetail(index, field, "Expected string."))
        return errors
    if expected_type == "number" and not _is_number(value):
        errors.append(ValidationErrorDetail(index, field, "Expected number."))
        return errors

    if isinstance(value, str) and rule.get("minLength", 0) > 0 and not value.strip():
        errors.append(ValidationErrorDetail(index, field, "Expected non-empty string."))

    if "enum" in rule and value not in rule["enum"]:
        errors.append(ValidationErrorDetail(index, field, f"Expected one of {rule['enum']}."))

    if rule.get("format") == "date" and isinstance(value, str):
        try:
            date.fromisoformat(value)
        except ValueError:
            errors.append(ValidationErrorDetail(index, field, "Expected ISO date format YYYY-MM-DD."))

    if field == "source_url" and isinstance(value, str):
        parsed = urlparse(value)
        if parsed.scheme not in allowed_schemes or not parsed.netloc:
            errors.append(ValidationErrorDetail(index, field, "Expected an allowed absolute source URL."))

    return errors


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_last_verified_freshness(
    index: int,
    value: Any,
    validation_date: date,
    max_age_days: int,
) -> list[ValidationErrorDetail]:
    if not isinstance(value, str):
        return []

    try:
        last_verified = date.fromisoformat(value)
    except ValueError:
        return []

    age_days = (validation_date - last_verified).days
    if age_days > max_age_days:
        return [
            ValidationErrorDetail(
                index,
                "last_verified",
                f"Source verification is stale; expected {max_age_days} days or newer.",
            )
        ]

    return []


def validate_file(
    input_path: Path,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
    source_rules_path: Path = DEFAULT_SOURCE_RULES_PATH,
) -> list[ValidationErrorDetail]:
    payload = load_json(input_path)
    records = normalize_records(payload)
    schema = load_json(schema_path)
    source_rules = load_json(source_rules_path)
    return validate_records(records, schema, source_rules)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate sourced financial metric records.")
    parser.add_argument("input_path", type=Path, help="JSON file containing one metric record or a list of records.")
    args = parser.parse_args()

    try:
        errors = validate_file(args.input_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [{"message": str(exc)}]}, indent=2))
        return 2

    result = {"valid": not errors, "errors": [error.to_dict() for error in errors]}
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
