from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTEXT_ROOT = REPO_ROOT / "data" / "companies"
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
    return result


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
