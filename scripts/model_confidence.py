from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTEXT_ROOT = REPO_ROOT / "data" / "companies"
DEFAULT_RULES_PATH = REPO_ROOT / "config" / "model_confidence_rules.json"
DEFAULT_SOURCE_RULES_PATH = REPO_ROOT / "config" / "source_rules.json"
DEFAULT_DCF_ASSUMPTIONS_PATH_TEMPLATE = REPO_ROOT / "data" / "companies" / "{ticker}" / "dcf_assumptions.json"
HIGH_PRIORITY_GAP_TYPES = {"missing_context", "missing_metric", "missing_source_metadata", "stale_metric"}
DISCLAIMER = "non-personalized model quality output, not investment advice."
PROHIBITED_OUTPUT_TERMS = [
    "price target",
    "buy",
    "sell",
    "hold",
    "recommendation",
    "model signal",
]


class ModelConfidenceError(ValueError):
    pass


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def calculate_model_confidence(
    ticker: str,
    validation_status: dict[str, Any],
    research_gaps: list[dict[str, Any]],
    context_root: Path = DEFAULT_CONTEXT_ROOT,
    dcf_assumptions_path: Path | None = None,
    rules_path: Path = DEFAULT_RULES_PATH,
    source_rules_path: Path = DEFAULT_SOURCE_RULES_PATH,
    today: date | None = None,
) -> dict[str, Any]:
    normalized_ticker = ticker.upper()
    rules = load_json(rules_path)
    source_rules = load_json(source_rules_path)
    context = _load_context(context_root / normalized_ticker / "context.json")
    metrics = [metric for metric in context.get("metrics", []) if isinstance(metric, dict)]
    validation_date = today or date.today()
    score = int(rules.get("score_ceiling", 100))
    reasons: list[str] = []
    warnings: list[str] = []
    assumption_quality = _default_assumption_quality()

    if not validation_status.get("valid"):
        score = _deduct(score, rules, "source_validation_failure")
        reasons.append("Source validation did not pass.")

    score = _apply_research_gap_deductions(score, rules, research_gaps, reasons)
    score = _apply_metric_confidence_deductions(score, rules, metrics, reasons)
    score, assumption_quality = _apply_dcf_assumption_deductions(
        score=score,
        rules=rules,
        assumptions_path=dcf_assumptions_path
        or Path(str(DEFAULT_DCF_ASSUMPTIONS_PATH_TEMPLATE).format(ticker=normalized_ticker)),
        reasons=reasons,
        warnings=warnings,
    )
    score = _apply_market_price_deductions(
        score=score,
        rules=rules,
        source_rules=source_rules,
        metrics=metrics,
        today=validation_date,
        reasons=reasons,
        warnings=warnings,
    )
    score = max(int(rules.get("score_floor", 0)), min(score, int(rules.get("score_ceiling", 100))))
    bucket = _confidence_bucket(score, rules)
    if not reasons:
        reasons.append("Validated inputs, source freshness, research gaps, and assumptions meet model quality rules.")

    result = {
        "ticker": normalized_ticker,
        "model_confidence": bucket["model_confidence"],
        "confidence_label": bucket["confidence_label"],
        "confidence_score": score,
        "reasons": reasons,
        "warnings": warnings,
        "rules_version": rules["rules_version"],
        "assumption_quality": assumption_quality,
        "source_references": _source_references(metrics),
        "disclaimer": DISCLAIMER,
    }
    _assert_no_prohibited_language(result)
    return result


def _load_context(context_path: Path) -> dict[str, Any]:
    try:
        context = load_json(context_path)
    except OSError as exc:
        raise ModelConfidenceError(f"Company context could not be loaded: {exc}") from exc
    if not isinstance(context, dict):
        raise ModelConfidenceError("Company context must be a JSON object.")
    return context


def _apply_research_gap_deductions(
    score: int,
    rules: dict[str, Any],
    research_gaps: list[dict[str, Any]],
    reasons: list[str],
) -> int:
    high_priority_count = 0
    standard_count = 0
    stale_count = 0
    for gap in research_gaps:
        gap_type = str(gap.get("gap_type") or "")
        if gap_type == "stale_metric":
            stale_count += 1
        if _is_high_priority_gap(gap):
            high_priority_count += 1
        else:
            standard_count += 1

    if high_priority_count:
        score -= high_priority_count * _deduction(rules, "high_priority_research_gap")
        reasons.append(f"{high_priority_count} high-priority research gap(s) reduce model confidence.")
    if standard_count:
        score -= standard_count * _deduction(rules, "standard_research_gap")
        reasons.append(f"{standard_count} standard research gap(s) reduce model confidence.")
    if stale_count:
        score -= stale_count * _deduction(rules, "stale_research_gap")
        reasons.append(f"{stale_count} stale data research gap(s) reduce model confidence.")
    return score


def _apply_metric_confidence_deductions(
    score: int,
    rules: dict[str, Any],
    metrics: list[dict[str, Any]],
    reasons: list[str],
) -> int:
    low_count = 0
    medium_count = 0
    for metric in metrics:
        source_metadata = metric.get("source_metadata")
        confidence = source_metadata.get("confidence") if isinstance(source_metadata, dict) else None
        if confidence == "low":
            low_count += 1
        elif confidence == "medium":
            medium_count += 1

    if low_count:
        score -= low_count * _deduction(rules, "low_metric_confidence")
        reasons.append(f"{low_count} metric(s) have low confidence.")
    if medium_count:
        score -= medium_count * _deduction(rules, "medium_metric_confidence")
        reasons.append(f"{medium_count} metric(s) have medium confidence.")
    return score


def _apply_dcf_assumption_deductions(
    score: int,
    rules: dict[str, Any],
    assumptions_path: Path,
    reasons: list[str],
    warnings: list[str],
) -> tuple[int, dict[str, Any]]:
    assumption_quality = _default_assumption_quality()
    try:
        assumptions = load_json(assumptions_path)
    except (OSError, json.JSONDecodeError):
        reasons.append("Assumption set is missing or unreadable.")
        assumption_quality.update(
            {
                "status": "missing_or_unreadable",
                "active_signal_allowed": False,
                "blocking_reasons": ["Assumption set is missing or unreadable."],
            }
        )
        return score - _deduction(rules, "missing_dcf_assumptions"), assumption_quality

    missing_items = _missing_dcf_assumption_items(assumptions, rules)
    if missing_items:
        reasons.append(f"Assumption set is incomplete: {', '.join(missing_items)}.")
        assumption_quality.update(
            {
                "status": "incomplete",
                "active_signal_allowed": False,
                "blocking_reasons": [f"Assumption set is incomplete: {', '.join(missing_items)}."],
            }
        )
        return score - _deduction(rules, "incomplete_dcf_assumptions"), assumption_quality

    manual_review_matches = _manual_review_assumption_matches(assumptions, rules)
    if manual_review_matches:
        cap = int(rules.get("assumption_quality", {}).get("manual_review_confidence_cap", score))
        score = min(score - _deduction(rules, "manual_review_dcf_assumptions"), cap)
        reason = "Assumption set is labeled as example, test, temporary, or requiring manual review."
        reasons.append(reason)
        warnings.append("Assumption quality is insufficient for active directional output until reviewed assumptions replace the example set.")
        assumption_quality.update(
            {
                "status": "manual_review_required",
                "active_signal_allowed": not bool(rules.get("assumption_quality", {}).get("blocks_active_signal", True)),
                "matched_terms": manual_review_matches,
                "blocking_reasons": [reason],
            }
        )
    return score, assumption_quality


def _default_assumption_quality() -> dict[str, Any]:
    return {
        "status": "sufficient",
        "active_signal_allowed": True,
        "matched_terms": [],
        "blocking_reasons": [],
    }


def _manual_review_assumption_matches(assumptions: dict[str, Any], rules: dict[str, Any]) -> list[str]:
    quality_rules = rules.get("assumption_quality", {})
    keywords = [str(keyword).lower() for keyword in quality_rules.get("manual_review_keywords", [])]
    text_parts = [
        assumptions.get("assumption_label"),
        *(assumptions.get("assumption_notes") if isinstance(assumptions.get("assumption_notes"), list) else []),
    ]
    haystack = " ".join(str(part).lower() for part in text_parts if part)
    return sorted({_safe_manual_review_term(keyword) for keyword in keywords if keyword and keyword in haystack})


def _safe_manual_review_term(keyword: str) -> str:
    if keyword == "placeholder":
        return "temporary"
    return keyword


def _missing_dcf_assumption_items(assumptions: dict[str, Any], rules: dict[str, Any]) -> list[str]:
    missing = []
    scenarios = assumptions.get("scenarios")
    if not isinstance(scenarios, dict):
        return ["scenarios"]

    for scenario_name in rules.get("required_dcf_scenarios", []):
        scenario = scenarios.get(scenario_name)
        if not isinstance(scenario, dict):
            missing.append(f"{scenario_name}.scenario")
            continue
        for field in rules.get("required_dcf_scenario_fields", []):
            value = scenario.get(field)
            if value in (None, "", []):
                missing.append(f"{scenario_name}.{field}")
    return missing


def _apply_market_price_deductions(
    score: int,
    rules: dict[str, Any],
    source_rules: dict[str, Any],
    metrics: list[dict[str, Any]],
    today: date,
    reasons: list[str],
    warnings: list[str],
) -> int:
    market_price = _find_market_price_metric(metrics)
    if market_price is None:
        reasons.append("Market price snapshot is missing.")
        return score - _deduction(rules, "missing_market_price_snapshot")

    fetched_at = _parse_iso_datetime(str(market_price.get("fetched_at", "")))
    max_age_days = source_rules.get("market_price_snapshot_max_age_days")
    if fetched_at is None:
        reasons.append("Market price snapshot fetched_at is missing or invalid.")
        return score - _deduction(rules, "missing_market_price_snapshot")
    if max_age_days is not None and (today - fetched_at.date()).days > int(max_age_days):
        reasons.append(f"Market price snapshot is older than {max_age_days} days.")
        warnings.append("Stale market price lowers model confidence but does not block the analysis workflow.")
        return score - _deduction(rules, "stale_market_price_snapshot")
    return score


def _find_market_price_metric(metrics: list[dict[str, Any]]) -> dict[str, Any] | None:
    for metric in metrics:
        if metric.get("metric_category") == "market_price" or metric.get("metric_name") == "Current market price":
            return metric
    return None


def _confidence_bucket(score: int, rules: dict[str, Any]) -> dict[str, Any]:
    for bucket in rules.get("confidence_buckets", []):
        minimum = bucket.get("minimum_score")
        maximum = bucket.get("maximum_score")
        if minimum is not None and score < minimum:
            continue
        if maximum is not None and score > maximum:
            continue
        return bucket
    raise ModelConfidenceError("No model confidence bucket matched the calculated score.")


def _source_references(metrics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    references = []
    for metric in metrics:
        source_metadata = metric.get("source_metadata")
        if not isinstance(source_metadata, dict):
            continue
        reference = {
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
        if metric.get("metric_category") == "market_price":
            reference.update(
                {
                    "currency": metric.get("currency"),
                    "exchange": metric.get("exchange"),
                    "price_type": metric.get("price_type"),
                    "as_of_datetime": metric.get("as_of_datetime"),
                    "fetched_at": metric.get("fetched_at"),
                    "provider": metric.get("provider"),
                    "retrieval_method": metric.get("retrieval_method"),
                }
            )
        references.append(reference)
    return references


def _is_high_priority_gap(gap: dict[str, Any]) -> bool:
    priority = str(gap.get("priority") or gap.get("severity") or "").lower()
    gap_type = str(gap.get("gap_type") or "")
    return priority == "high" or gap_type in HIGH_PRIORITY_GAP_TYPES


def _deduct(score: int, rules: dict[str, Any], key: str) -> int:
    return score - _deduction(rules, key)


def _deduction(rules: dict[str, Any], key: str) -> int:
    return int(rules.get("deductions", {}).get(key, 0))


def _parse_iso_datetime(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _assert_no_prohibited_language(result: dict[str, Any]) -> None:
    serialized = json.dumps(result).lower().replace("not investment advice", "")
    found = [term for term in PROHIBITED_OUTPUT_TERMS if term in serialized]
    if found:
        raise ModelConfidenceError(f"Model confidence output contains prohibited language: {', '.join(found)}.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate rule-based model confidence from validated inputs.")
    parser.add_argument("ticker")
    parser.add_argument("--validation-status-json", type=Path, required=True)
    parser.add_argument("--research-gaps-json", type=Path, required=True)
    parser.add_argument("--context-root", type=Path, default=DEFAULT_CONTEXT_ROOT)
    parser.add_argument("--dcf-assumptions-path", type=Path)
    parser.add_argument("--rules-path", type=Path, default=DEFAULT_RULES_PATH)
    parser.add_argument("--source-rules-path", type=Path, default=DEFAULT_SOURCE_RULES_PATH)
    args = parser.parse_args()

    try:
        result = calculate_model_confidence(
            ticker=args.ticker,
            validation_status=load_json(args.validation_status_json),
            research_gaps=load_json(args.research_gaps_json),
            context_root=args.context_root,
            dcf_assumptions_path=args.dcf_assumptions_path,
            rules_path=args.rules_path,
            source_rules_path=args.source_rules_path,
        )
    except (OSError, json.JSONDecodeError, ModelConfidenceError) as exc:
        print(json.dumps({"calculated": False, "error": str(exc)}, indent=2))
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
