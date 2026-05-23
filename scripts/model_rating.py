from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTEXT_ROOT = REPO_ROOT / "data" / "companies"
DEFAULT_RULES_PATH = REPO_ROOT / "config" / "model_rating_rules.json"
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
) -> dict[str, Any]:
    normalized_ticker = ticker.upper()
    rules = load_json(rules_path)
    context = load_json(context_root / normalized_ticker / "context.json")
    market_price_metric = _find_market_price_metric(context)
    _validate_market_price_metric(market_price_metric)

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
        },
        "warnings": [
            "Model rating is a deterministic rule-based classification from fair value per share and sourced market price only.",
            "No market prices, fair values, or rules were invented.",
        ],
        "source_references": [_source_reference(market_price_metric)],
        "disclaimer": DISCLAIMER,
    }
    _assert_no_prohibited_language(result)
    return result


def _find_market_price_metric(context: dict[str, Any]) -> dict[str, Any]:
    for metric in context.get("metrics", []):
        if not isinstance(metric, dict):
            continue
        if metric.get("metric_category") == "market_price" or metric.get("metric_name") == "Current market price":
            return metric
    raise ModelRatingError("Missing externally sourced current_market_price metric.")


def _validate_market_price_metric(metric: dict[str, Any]) -> None:
    metric_id = metric.get("metric_id")
    if not isinstance(metric_id, str) or not metric_id.strip():
        raise ModelRatingError("Current market price metric must include metric_id.")
    value = metric.get("value")
    if not _is_number(value) or value <= 0:
        raise ModelRatingError("Current market price metric value must be greater than zero.")
    source_metadata = metric.get("source_metadata")
    if not isinstance(source_metadata, dict):
        raise ModelRatingError("Current market price metric must include source metadata.")
    for field in ["source_url", "source_type", "source_date", "last_verified", "confidence"]:
        if not source_metadata.get(field):
            raise ModelRatingError(f"Current market price source metadata missing {field}.")


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
        "source_url": source_metadata.get("source_url"),
        "source_type": source_metadata.get("source_type"),
        "source_date": source_metadata.get("source_date"),
        "last_verified": source_metadata.get("last_verified"),
        "confidence": source_metadata.get("confidence"),
    }


def _assert_no_prohibited_language(result: dict[str, Any]) -> None:
    serialized = json.dumps(result).lower()
    found = [term for term in PROHIBITED_OUTPUT_TERMS if term in serialized]
    if found:
        raise ModelRatingError(f"Model rating output contains prohibited language: {', '.join(found)}.")


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate rule-based model rating from fair value per share and sourced market price.")
    parser.add_argument("ticker")
    parser.add_argument("--fair-value-per-share-json", type=Path, required=True)
    parser.add_argument("--context-root", type=Path, default=DEFAULT_CONTEXT_ROOT)
    parser.add_argument("--rules-path", type=Path, default=DEFAULT_RULES_PATH)
    args = parser.parse_args()

    try:
        result = calculate_model_rating(
            ticker=args.ticker,
            fair_value_per_share_output=load_json(args.fair_value_per_share_json),
            context_root=args.context_root,
            rules_path=args.rules_path,
        )
    except (OSError, json.JSONDecodeError, ModelRatingError) as exc:
        print(json.dumps({"calculated": False, "error": str(exc)}, indent=2))
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
