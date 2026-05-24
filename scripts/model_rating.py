from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTEXT_ROOT = REPO_ROOT / "data" / "companies"
DEFAULT_RULES_PATH = REPO_ROOT / "config" / "model_rating_rules.json"
DEFAULT_SOURCE_RULES_PATH = REPO_ROOT / "config" / "source_rules.json"
DEFAULT_OUTPUT_SCHEMA_PATH = REPO_ROOT / "config" / "model_rating_output_schema.json"
REQUIRED_MARKET_PRICE_SNAPSHOT_FIELDS = [
    "metric_id",
    "value",
    "currency",
    "exchange",
    "price_type",
    "as_of_datetime",
    "fetched_at",
    "provider",
    "retrieval_method",
]
PROHIBITED_OUTPUT_TERMS = [
    "price target",
    "buy",
    "sell",
    "hold",
    "recommendation",
]
DISCLAIMER = "non-personalized model output, not investment advice."


class ModelRatingError(ValueError):
    pass


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def calculate_model_rating(
    ticker: str,
    fair_value_per_share_output: dict[str, Any],
    context_root: Path = DEFAULT_CONTEXT_ROOT,
    rules_path: Path = DEFAULT_RULES_PATH,
    source_rules_path: Path = DEFAULT_SOURCE_RULES_PATH,
    today: date | None = None,
) -> dict[str, Any]:
    normalized_ticker = ticker.upper()
    rules = load_json(rules_path)
    source_rules = load_json(source_rules_path)
    context = load_json(context_root / normalized_ticker / "context.json")
    market_price_metric = _find_market_price_metric(context)
    _validate_market_price_metric(
        market_price_metric,
        max_age_days=source_rules.get("market_price_snapshot_max_age_days"),
        today=today or date.today(),
    )

    scenario_name = rules["scenario_used"]
    fair_value_scenario = _find_fair_value_scenario(fair_value_per_share_output, scenario_name)
    fair_value = fair_value_scenario.get("fair_value_per_share")
    if not _is_number(fair_value):
        raise ModelRatingError(f"Fair value per share scenario {scenario_name} missing numeric fair_value_per_share.")

    market_price = market_price_metric["value"]
    valuation_gap_percent = ((fair_value - market_price) / market_price) * 100
    bucket = _rating_bucket(valuation_gap_percent, rules)
    result = {
        "ticker": normalized_ticker,
        "model_rating": bucket["model_rating"],
        "rating_label": bucket["rating_label"],
        "fair_value_per_share_used": fair_value,
        "market_price_used": market_price,
        "valuation_gap_percent": valuation_gap_percent,
        "rules_version": rules["rules_version"],
        "assumptions": {
            "scenario_used": scenario_name,
            "valuation_gap_formula": rules["valuation_gap_formula"],
            "market_price_metric_id": market_price_metric["metric_id"],
            "market_price_unit": market_price_metric["unit"],
            "market_price_period": market_price_metric["period"],
            "market_price_as_of_datetime": market_price_metric["as_of_datetime"],
            "market_price_fetched_at": market_price_metric["fetched_at"],
            "market_price_provider": market_price_metric["provider"],
            "market_price_retrieval_method": market_price_metric["retrieval_method"],
        },
        "warnings": [
            "Model rating is a deterministic rule-based classification from fair value per share and sourced market price only.",
            "No market prices, fair values, or rules were invented.",
        ],
        "source_references": [_source_reference(market_price_metric)],
        "disclaimer": DISCLAIMER,
    }
    _assert_no_prohibited_language(result)
    validate_model_rating_output(result)
    return result


def validate_model_rating_output(
    output: dict[str, Any],
    schema: dict[str, Any] | None = None,
) -> list[str]:
    schema = schema or load_json(DEFAULT_OUTPUT_SCHEMA_PATH)
    errors: list[str] = []

    if not isinstance(output, dict):
        raise ModelRatingError("Model rating output must be a JSON object.")

    for field in schema.get("required_fields", []):
        errors.extend(_validate_required_field(output, field, schema.get("field_types", {})))

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
            errors.extend(_validate_source_reference(index, source_reference, schema))

    if errors:
        raise ModelRatingError("; ".join(errors))

    return []


def _find_market_price_metric(context: dict[str, Any]) -> dict[str, Any]:
    for metric in context.get("metrics", []):
        if not isinstance(metric, dict):
            continue
        if metric.get("metric_category") == "market_price" or metric.get("metric_name") == "Current market price":
            return metric
    raise ModelRatingError("Missing externally sourced current_market_price metric.")


def _validate_market_price_metric(metric: dict[str, Any], max_age_days: int | None, today: date) -> None:
    for field in REQUIRED_MARKET_PRICE_SNAPSHOT_FIELDS:
        if not metric.get(field):
            raise ModelRatingError(f"Current market price snapshot missing {field}.")

    value = metric.get("value")
    if not _is_number(value) or value <= 0:
        raise ModelRatingError("Current market price metric value must be greater than zero.")
    source_metadata = metric.get("source_metadata")
    if not isinstance(source_metadata, dict):
        raise ModelRatingError("Current market price metric must include source metadata.")
    for field in ["source_url", "source_type", "source_date", "last_verified", "confidence"]:
        if not source_metadata.get(field):
            raise ModelRatingError(f"Current market price source metadata missing {field}.")

    if _parse_iso_datetime(str(metric["as_of_datetime"])) is None:
        raise ModelRatingError("Current market price snapshot as_of_datetime must be an ISO datetime.")
    fetched_at = _parse_iso_datetime(str(metric["fetched_at"]))
    if fetched_at is None:
        raise ModelRatingError("Current market price snapshot fetched_at must be an ISO datetime.")
    if max_age_days is not None and (today - fetched_at.date()).days > max_age_days:
        raise ModelRatingError(f"Current market price snapshot is stale; expected fetched_at {max_age_days} days or newer.")


def _find_fair_value_scenario(fair_value_per_share_output: dict[str, Any], scenario_name: str) -> dict[str, Any]:
    if not fair_value_per_share_output.get("calculated"):
        raise ModelRatingError("Fair value per share output must be calculated before model rating can be calculated.")
    for scenario in fair_value_per_share_output.get("scenarios", []):
        if scenario.get("scenario") == scenario_name:
            return scenario
    raise ModelRatingError(f"Missing fair value per share scenario: {scenario_name}.")


def _rating_bucket(valuation_gap_percent: float, rules: dict[str, Any]) -> dict[str, Any]:
    for bucket in rules.get("rating_buckets", []):
        minimum = bucket.get("minimum_gap_percent")
        maximum = bucket.get("maximum_gap_percent")
        if minimum is not None and valuation_gap_percent < minimum:
            continue
        if maximum is not None and valuation_gap_percent > maximum:
            continue
        return bucket
    raise ModelRatingError("No model rating bucket matched valuation gap percent.")


def _source_reference(metric: dict[str, Any]) -> dict[str, Any]:
    source_metadata = metric.get("source_metadata", {})
    return {
        "metric_id": metric.get("metric_id"),
        "metric_name": metric.get("metric_name"),
        "metric_category": metric.get("metric_category"),
        "period": metric.get("period"),
        "unit": metric.get("unit"),
        "currency": metric.get("currency"),
        "exchange": metric.get("exchange"),
        "price_type": metric.get("price_type"),
        "as_of_datetime": metric.get("as_of_datetime"),
        "fetched_at": metric.get("fetched_at"),
        "provider": metric.get("provider"),
        "retrieval_method": metric.get("retrieval_method"),
        "source_url": source_metadata.get("source_url"),
        "source_type": source_metadata.get("source_type"),
        "source_date": source_metadata.get("source_date"),
        "last_verified": source_metadata.get("last_verified"),
        "confidence": source_metadata.get("confidence"),
    }


def _validate_source_reference(index: int, source_reference: Any, schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not isinstance(source_reference, dict):
        return [f"source_references item {index} must be an object."]

    for field in schema.get("source_reference_required_fields", []):
        errors.extend(
            _validate_required_field(
                source_reference,
                field,
                schema.get("source_reference_field_types", {}),
                prefix=f"source_references item {index} ",
            )
        )

    return errors


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
    elif expected_type == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
        errors.append(f"{field} must be an integer.")
    elif expected_type == "date":
        if not isinstance(value, str):
            errors.append(f"{field} must be a date string.")
        else:
            try:
                date.fromisoformat(value)
            except ValueError:
                errors.append(f"{field} must use ISO date format YYYY-MM-DD.")
    elif expected_type == "datetime":
        if not isinstance(value, str):
            errors.append(f"{field} must be a datetime string.")
        elif _parse_iso_datetime(value) is None:
            errors.append(f"{field} must use ISO datetime format.")

    return errors


def _assert_no_prohibited_language(result: dict[str, Any]) -> None:
    serialized = json.dumps(result).lower()
    found = [term for term in PROHIBITED_OUTPUT_TERMS if term in serialized]
    if found:
        raise ModelRatingError(f"Model rating output contains prohibited language: {', '.join(found)}.")


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _parse_iso_datetime(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate rule-based model rating from fair value per share and sourced market price.")
    parser.add_argument("ticker")
    parser.add_argument("--fair-value-per-share-json", type=Path, required=True)
    parser.add_argument("--context-root", type=Path, default=DEFAULT_CONTEXT_ROOT)
    parser.add_argument("--rules-path", type=Path, default=DEFAULT_RULES_PATH)
    parser.add_argument("--source-rules-path", type=Path, default=DEFAULT_SOURCE_RULES_PATH)
    args = parser.parse_args()

    try:
        result = calculate_model_rating(
            ticker=args.ticker,
            fair_value_per_share_output=load_json(args.fair_value_per_share_json),
            context_root=args.context_root,
            rules_path=args.rules_path,
            source_rules_path=args.source_rules_path,
        )
    except (OSError, json.JSONDecodeError, ModelRatingError) as exc:
        print(json.dumps({"calculated": False, "error": str(exc)}, indent=2))
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
