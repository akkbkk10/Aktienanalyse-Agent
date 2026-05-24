from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULES_PATH = REPO_ROOT / "config" / "model_signal_rules.json"
DEFAULT_SOURCE_RULES_PATH = REPO_ROOT / "config" / "source_rules.json"
DISCLAIMER = "non-personalized model output, not investment advice."
PROHIBITED_OUTPUT_TERMS = [
    "price target",
    "buy",
    "sell",
    "hold",
    "recommendation",
]


class ModelSignalError(ValueError):
    pass


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def calculate_model_signal(
    ticker: str,
    model_rating_output: dict[str, Any] | None,
    model_confidence_output: dict[str, Any] | None,
    research_gaps: list[dict[str, Any]],
    rules_path: Path = DEFAULT_RULES_PATH,
    source_rules_path: Path = DEFAULT_SOURCE_RULES_PATH,
    today: date | None = None,
) -> dict[str, Any]:
    normalized_ticker = ticker.upper()
    rules = load_json(rules_path)
    source_rules = load_json(source_rules_path)
    validation_date = today or date.today()
    reasons: list[str] = []
    blocking_reasons: list[str] = []
    warnings: list[str] = []

    if not isinstance(model_rating_output, dict):
        blocking_reasons.append("Model rating is unavailable.")
    if not isinstance(model_confidence_output, dict):
        blocking_reasons.append("Model confidence is unavailable.")

    model_rating = model_rating_output.get("model_rating") if isinstance(model_rating_output, dict) else None
    valuation_gap = model_rating_output.get("valuation_gap_percent") if isinstance(model_rating_output, dict) else None
    model_confidence = (
        model_confidence_output.get("model_confidence") if isinstance(model_confidence_output, dict) else None
    )

    if model_confidence in rules.get("unavailable", {}).get("confidence_values", []):
        blocking_reasons.append("Model confidence is D.")

    assumption_quality_reason = _assumption_quality_blocking_reason(model_confidence_output)
    if assumption_quality_reason:
        blocking_reasons.append(assumption_quality_reason)
        warnings.append("Assumption quality blocks active model output until reviewed assumptions are provided.")

    high_priority_gaps = _high_priority_gaps(research_gaps, rules)
    if high_priority_gaps:
        blocking_reasons.append(f"{len(high_priority_gaps)} high-priority research gap(s) remain open.")

    if isinstance(model_rating_output, dict):
        freshness_reason = _market_price_freshness_blocking_reason(
            model_rating_output=model_rating_output,
            max_age_days=source_rules.get("market_price_snapshot_max_age_days"),
            today=validation_date,
        )
        if freshness_reason:
            blocking_reasons.append(freshness_reason)

    if blocking_reasons:
        signal = "unavailable"
        reasons.append("Model signal is unavailable because required model-quality gates did not pass.")
    elif _matches_positive(model_rating, model_confidence, valuation_gap, rules):
        signal = "model_positive"
        reasons.append("Model rating, model confidence, model gap, research gaps, and market price freshness meet positive rules.")
    elif _matches_negative(model_rating, model_confidence, valuation_gap, rules):
        signal = "model_negative"
        reasons.append("Model rating, model confidence, model gap, research gaps, and market price freshness meet negative rules.")
    else:
        signal = "model_neutral"
        reasons.append("Model inputs do not meet positive or negative rule limits.")

    result = {
        "ticker": normalized_ticker,
        "model_signal": signal,
        "reasons": reasons,
        "blocking_reasons": _unique(blocking_reasons),
        "model_rating_used": _model_rating_used(model_rating_output),
        "model_confidence_used": _model_confidence_used(model_confidence_output),
        "rules_version": rules["rules_version"],
        "warnings": warnings,
        "disclaimer": DISCLAIMER,
    }
    _validate_allowed_signal(result, rules)
    _assert_no_prohibited_language(result)
    return result


def _matches_positive(model_rating: Any, model_confidence: Any, valuation_gap: Any, rules: dict[str, Any]) -> bool:
    positive_rules = rules.get("positive", {})
    return (
        _is_number(model_rating)
        and model_rating >= positive_rules.get("minimum_model_rating", 4)
        and model_confidence in positive_rules.get("allowed_confidence", [])
        and _is_number(valuation_gap)
        and valuation_gap >= positive_rules.get("minimum_valuation_gap_percent", 15.0)
    )


def _matches_negative(model_rating: Any, model_confidence: Any, valuation_gap: Any, rules: dict[str, Any]) -> bool:
    negative_rules = rules.get("negative", {})
    return (
        _is_number(model_rating)
        and model_rating <= negative_rules.get("maximum_model_rating", 2)
        and model_confidence in negative_rules.get("allowed_confidence", [])
        and _is_number(valuation_gap)
        and valuation_gap <= negative_rules.get("maximum_valuation_gap_percent", -15.0)
    )


def _market_price_freshness_blocking_reason(
    model_rating_output: dict[str, Any],
    max_age_days: int | None,
    today: date,
) -> str | None:
    references = model_rating_output.get("source_references", [])
    market_reference = None
    for reference in references:
        if not isinstance(reference, dict):
            continue
        if reference.get("metric_category") == "market_price" or reference.get("metric_name") == "Current market price":
            market_reference = reference
            break
    if market_reference is None:
        return "Market price snapshot reference is missing."

    fetched_at = _parse_iso_datetime(str(market_reference.get("fetched_at", "")))
    if fetched_at is None:
        return "Market price snapshot fetched_at is missing or invalid."
    if max_age_days is not None and (today - fetched_at.date()).days > int(max_age_days):
        return f"Market price snapshot is stale; expected fetched_at {max_age_days} days or newer."
    return None


def _high_priority_gaps(research_gaps: list[dict[str, Any]], rules: dict[str, Any]) -> list[dict[str, Any]]:
    high_priority_gap_types = set(rules.get("unavailable", {}).get("high_priority_gap_types", []))
    high_priority = []
    for gap in research_gaps:
        priority = str(gap.get("priority") or gap.get("severity") or "").lower()
        gap_type = str(gap.get("gap_type") or "")
        if priority == "high" or gap_type in high_priority_gap_types:
            high_priority.append(gap)
    return high_priority


def _model_rating_used(model_rating_output: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(model_rating_output, dict):
        return None
    return {
        "model_rating": model_rating_output.get("model_rating"),
        "rating_label": model_rating_output.get("rating_label"),
        "valuation_gap_percent": model_rating_output.get("valuation_gap_percent"),
        "rules_version": model_rating_output.get("rules_version"),
    }


def _model_confidence_used(model_confidence_output: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(model_confidence_output, dict):
        return None
    return {
        "model_confidence": model_confidence_output.get("model_confidence"),
        "confidence_label": model_confidence_output.get("confidence_label"),
        "confidence_score": model_confidence_output.get("confidence_score"),
        "assumption_quality": model_confidence_output.get("assumption_quality"),
        "rules_version": model_confidence_output.get("rules_version"),
    }


def _assumption_quality_blocking_reason(model_confidence_output: dict[str, Any] | None) -> str | None:
    if not isinstance(model_confidence_output, dict):
        return None
    assumption_quality = model_confidence_output.get("assumption_quality")
    if not isinstance(assumption_quality, dict):
        return None
    if assumption_quality.get("active_signal_allowed", True):
        return None
    blocking_reasons = assumption_quality.get("blocking_reasons")
    if isinstance(blocking_reasons, list) and blocking_reasons:
        return f"Assumption quality gate did not pass: {blocking_reasons[0]}"
    return "Assumption quality gate did not pass."


def _validate_allowed_signal(result: dict[str, Any], rules: dict[str, Any]) -> None:
    allowed_signals = set(rules.get("allowed_signals", []))
    if result.get("model_signal") not in allowed_signals:
        raise ModelSignalError(f"Unsupported model signal: {result.get('model_signal')}")


def _assert_no_prohibited_language(result: dict[str, Any]) -> None:
    serialized = json.dumps(result).lower().replace("not investment advice", "")
    found = [term for term in PROHIBITED_OUTPUT_TERMS if term in serialized]
    if found:
        raise ModelSignalError(f"Model signal output contains prohibited language: {', '.join(found)}.")


def _parse_iso_datetime(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _unique(values: list[str]) -> list[str]:
    seen = set()
    unique_values = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        unique_values.append(value)
    return unique_values


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate rule-based non-personalized model signal.")
    parser.add_argument("ticker")
    parser.add_argument("--model-rating-json", type=Path, required=True)
    parser.add_argument("--model-confidence-json", type=Path, required=True)
    parser.add_argument("--research-gaps-json", type=Path, required=True)
    parser.add_argument("--rules-path", type=Path, default=DEFAULT_RULES_PATH)
    parser.add_argument("--source-rules-path", type=Path, default=DEFAULT_SOURCE_RULES_PATH)
    args = parser.parse_args()

    try:
        result = calculate_model_signal(
            ticker=args.ticker,
            model_rating_output=load_json(args.model_rating_json),
            model_confidence_output=load_json(args.model_confidence_json),
            research_gaps=load_json(args.research_gaps_json),
            rules_path=args.rules_path,
            source_rules_path=args.source_rules_path,
        )
    except (OSError, json.JSONDecodeError, ModelSignalError) as exc:
        print(json.dumps({"calculated": False, "error": str(exc)}, indent=2))
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
