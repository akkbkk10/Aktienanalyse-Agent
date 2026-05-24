from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTEXT_ROOT = REPO_ROOT / "data" / "companies"
DEFAULT_OUTPUT_SCHEMA_PATH = REPO_ROOT / "config" / "fair_value_per_share_output_schema.json"
PROHIBITED_OUTPUT_TERMS = [
    "price target",
    "buy",
    "sell",
    "hold",
    "recommendation",
]
FORMULAS = {
    "fair_value_per_share": "dcf_value_used / diluted_share_count_used",
}
DISCLAIMER = "calculated model output only, not investment advice."


class FairValuePerShareError(ValueError):
    pass


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def calculate_fair_value_per_share(
    ticker: str,
    dcf_output: dict[str, Any],
    context_root: Path = DEFAULT_CONTEXT_ROOT,
) -> dict[str, Any]:
    normalized_ticker = ticker.upper()
    if not dcf_output.get("calculated"):
        raise FairValuePerShareError("DCF output must be calculated before fair value per share can be calculated.")

    context = load_json(context_root / normalized_ticker / "context.json")
    share_count_metric = _find_share_count_metric(context)
    _validate_share_count_metric(share_count_metric)

    currency = _currency_from_unit(str(dcf_output.get("unit", "")))
    scenarios = []
    for scenario_name, scenario in sorted(dcf_output.get("scenarios", {}).items()):
        dcf_value = scenario.get("dcf_value")
        if not _is_number(dcf_value):
            raise FairValuePerShareError(f"Scenario {scenario_name} missing numeric dcf_value.")
        scenarios.append(
            {
                "ticker": normalized_ticker,
                "scenario": scenario_name,
                "fair_value_per_share": dcf_value / share_count_metric["value"],
                "currency": currency,
                "dcf_value_used": dcf_value,
                "share_count_used": share_count_metric["value"],
                "share_count_metric_id": share_count_metric["metric_id"],
                "formula": FORMULAS["fair_value_per_share"],
                "source_references": [_source_reference(share_count_metric)],
            }
        )

    result = {
        "ticker": normalized_ticker,
        "calculated": True,
        "currency": currency,
        "formulas": FORMULAS,
        "assumptions": {
            "dcf_output_unit": dcf_output.get("unit"),
            "share_count_unit": share_count_metric.get("unit"),
            "share_count_period": share_count_metric.get("period"),
            "share_count_metric_id": share_count_metric.get("metric_id"),
        },
        "warnings": [
            "Fair value per share is deterministic arithmetic from existing DCF output and sourced share count only.",
            "No share counts or assumptions were invented.",
        ],
        "source_references": [_source_reference(share_count_metric)],
        "disclaimer": DISCLAIMER,
        "scenarios": scenarios,
    }
    _assert_no_prohibited_language(result)
    validate_fair_value_per_share_output(result)
    return result


def validate_fair_value_per_share_output(
    output: dict[str, Any],
    schema: dict[str, Any] | None = None,
) -> list[str]:
    schema = schema or load_json(DEFAULT_OUTPUT_SCHEMA_PATH)
    errors: list[str] = []

    if not isinstance(output, dict):
        raise FairValuePerShareError("Fair value per share output must be a JSON object.")

    for field in schema.get("required_fields", []):
        errors.extend(_validate_required_field(output, field, schema.get("field_types", {})))

    if output.get("calculated") is not True:
        errors.append("calculated must be true for fair value per share output.")

    assumptions = output.get("assumptions")
    if isinstance(assumptions, dict):
        for field in schema.get("assumption_required_fields", []):
            errors.extend(
                _validate_required_field(
                    assumptions,
                    field,
                    schema.get("assumption_field_types", {}),
                    prefix="assumptions.",
                )
            )

    source_references = output.get("source_references")
    if isinstance(source_references, list):
        if not source_references:
            errors.append("source_references must be a non-empty array.")
        for index, source_reference in enumerate(source_references):
            errors.extend(_validate_source_reference(index, source_reference, schema, "source_references"))

    scenarios = output.get("scenarios")
    if isinstance(scenarios, list):
        if not scenarios:
            errors.append("scenarios must be a non-empty array.")
        for index, scenario in enumerate(scenarios):
            errors.extend(_validate_fair_value_scenario(index, scenario, schema))

    if errors:
        raise FairValuePerShareError("; ".join(errors))

    return []


def _find_share_count_metric(context: dict[str, Any]) -> dict[str, Any]:
    for metric in context.get("metrics", []):
        if not isinstance(metric, dict):
            continue
        if metric.get("metric_category") == "share_count":
            return metric
    raise FairValuePerShareError("Missing sourced share_count metric.")


def _validate_share_count_metric(metric: dict[str, Any]) -> None:
    metric_id = metric.get("metric_id")
    if not isinstance(metric_id, str) or not metric_id.strip():
        raise FairValuePerShareError("Share count metric must include metric_id.")
    value = metric.get("value")
    if not _is_number(value) or value <= 0:
        raise FairValuePerShareError("Share count metric value must be greater than zero.")
    source_metadata = metric.get("source_metadata")
    if not isinstance(source_metadata, dict):
        raise FairValuePerShareError("Share count metric must include source metadata.")
    for field in ["source_url", "source_type", "source_date", "last_verified", "confidence"]:
        if not source_metadata.get(field):
            raise FairValuePerShareError(f"Share count metric source metadata missing {field}.")


def _validate_fair_value_scenario(index: int, scenario: Any, schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not isinstance(scenario, dict):
        return [f"scenarios item {index} must be an object."]

    for field in schema.get("scenario_required_fields", []):
        errors.extend(
            _validate_required_field(
                scenario,
                field,
                schema.get("scenario_field_types", {}),
                prefix=f"scenarios item {index} ",
            )
        )

    source_references = scenario.get("source_references")
    if isinstance(source_references, list):
        if not source_references:
            errors.append(f"scenarios item {index} source_references must be a non-empty array.")
        for source_index, source_reference in enumerate(source_references):
            errors.extend(
                _validate_source_reference(
                    source_index,
                    source_reference,
                    schema,
                    f"scenarios item {index} source_references",
                )
            )

    return errors


def _validate_source_reference(
    index: int,
    source_reference: Any,
    schema: dict[str, Any],
    label: str,
) -> list[str]:
    errors: list[str] = []

    if not isinstance(source_reference, dict):
        return [f"{label} item {index} must be an object."]

    for field in schema.get("source_reference_required_fields", []):
        errors.extend(
            _validate_required_field(
                source_reference,
                field,
                schema.get("source_reference_field_types", {}),
                prefix=f"{label} item {index} ",
            )
        )

    return errors


def _source_reference(metric: dict[str, Any]) -> dict[str, Any]:
    source_metadata = metric.get("source_metadata", {})
    return {
        "metric_id": metric.get("metric_id"),
        "metric_name": metric.get("metric_name"),
        "metric_category": metric.get("metric_category"),
        "period": metric.get("period"),
        "unit": metric.get("unit"),
        "accounting_basis": metric.get("accounting_basis"),
        "source_url": source_metadata.get("source_url"),
        "source_type": source_metadata.get("source_type"),
        "source_date": source_metadata.get("source_date"),
        "last_verified": source_metadata.get("last_verified"),
        "confidence": source_metadata.get("confidence"),
    }


def _currency_from_unit(unit: str) -> str:
    return unit.split()[0] if unit else "unknown"


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_required_field(
    payload: dict[str, Any],
    field: str,
    field_types: dict[str, str],
    prefix: str = "",
) -> list[str]:
    if field not in payload or payload[field] in (None, ""):
        return [f"{prefix}missing required field: {field}."]

    expected_type = field_types.get(field)
    if expected_type:
        return _validate_contract_type(f"{prefix}{field}", payload[field], expected_type)

    return []


def _validate_contract_type(field: str, value: Any, expected_type: str) -> list[str]:
    errors: list[str] = []

    if expected_type == "string" and not isinstance(value, str):
        errors.append(f"{field} must be a string.")
    elif expected_type == "boolean" and not isinstance(value, bool):
        errors.append(f"{field} must be a boolean.")
    elif expected_type == "array" and not isinstance(value, list):
        errors.append(f"{field} must be an array.")
    elif expected_type == "object" and not isinstance(value, dict):
        errors.append(f"{field} must be an object.")
    elif expected_type == "number" and not _is_number(value):
        errors.append(f"{field} must be a number.")
    elif expected_type == "date":
        if not isinstance(value, str):
            errors.append(f"{field} must be a date string.")
        else:
            try:
                date.fromisoformat(value)
            except ValueError:
                errors.append(f"{field} must use ISO date format YYYY-MM-DD.")

    return errors


def _assert_no_prohibited_language(result: dict[str, Any]) -> None:
    serialized = json.dumps(result).lower()
    found = [term for term in PROHIBITED_OUTPUT_TERMS if term in serialized]
    if found:
        raise FairValuePerShareError(f"Fair value per share output contains prohibited language: {', '.join(found)}.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate deterministic fair value per share from DCF output and sourced share count.")
    parser.add_argument("ticker")
    parser.add_argument("--dcf-output-path", type=Path, required=True)
    parser.add_argument("--context-root", type=Path, default=DEFAULT_CONTEXT_ROOT)
    args = parser.parse_args()

    try:
        result = calculate_fair_value_per_share(
            ticker=args.ticker,
            dcf_output=load_json(args.dcf_output_path),
            context_root=args.context_root,
        )
    except (OSError, json.JSONDecodeError, FairValuePerShareError) as exc:
        print(json.dumps({"calculated": False, "error": str(exc)}, indent=2))
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
