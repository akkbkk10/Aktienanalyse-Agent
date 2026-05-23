from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import check_valuation_readiness


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "config" / "dcf_assumptions_schema.json"
DEFAULT_CONTEXT_ROOT = REPO_ROOT / "data" / "companies"
DEFAULT_SOURCE_DATA_PATH = REPO_ROOT / "data" / "nvda_sample_metrics.json"
PROHIBITED_OUTPUT_TERMS = [
    "price target",
    "buy",
    "sell",
    "hold",
    "recommendation",
    "investment advice",
]
FORMULAS = {
    "present_value_free_cash_flow": "free_cash_flow / (1 + discount_rate) ^ year",
    "terminal_value": "final_forecast_free_cash_flow * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)",
    "present_value_terminal_value": "terminal_value / (1 + discount_rate) ^ final_year",
    "dcf_value": "sum(present_value_free_cash_flow) + present_value_terminal_value",
}


class DCFValidationError(ValueError):
    pass


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_dcf(
    ticker: str,
    assumptions_path: Path,
    source_data_path: Path = DEFAULT_SOURCE_DATA_PATH,
    context_root: Path = DEFAULT_CONTEXT_ROOT,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
    readiness_result: dict[str, Any] | None = None,
    readiness_audit_log_path: Path = check_valuation_readiness.DEFAULT_READINESS_AUDIT_LOG_PATH,
) -> dict[str, Any]:
    normalized_ticker = ticker.upper()
    readiness = readiness_result or check_valuation_readiness.check_readiness(
        ticker=normalized_ticker,
        source_data_path=source_data_path,
        context_root=context_root,
        audit_log_path=readiness_audit_log_path,
    )
    if not readiness.get("ready_for_valuation"):
        return {
            "ticker": normalized_ticker,
            "calculated": False,
            "blocking_reasons": ["Valuation readiness gate did not pass."],
            "readiness": readiness,
            "warnings": [],
            "scenarios": {},
        }

    assumptions = load_json(assumptions_path)
    schema = load_json(schema_path)
    errors = validate_assumptions(assumptions, schema, normalized_ticker)
    if errors:
        raise DCFValidationError("; ".join(errors))

    scenarios = {
        scenario_name: _calculate_scenario(scenario_name, scenario)
        for scenario_name, scenario in assumptions["scenarios"].items()
    }
    result = {
        "ticker": normalized_ticker,
        "calculated": True,
        "schema_version": assumptions["schema_version"],
        "unit": assumptions["unit"],
        "formulas": FORMULAS,
        "assumptions_used": _assumptions_used(assumptions),
        "source_references": assumptions["source_references"],
        "warnings": _warnings(assumptions),
        "scenarios": scenarios,
    }
    _assert_no_prohibited_language(result)
    return result


def validate_assumptions(
    assumptions: dict[str, Any],
    schema: dict[str, Any],
    ticker: str,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(assumptions, dict):
        return ["Assumptions must be a JSON object."]

    for field in schema.get("required_fields", []):
        if field not in assumptions or assumptions[field] in (None, "", []):
            errors.append(f"Missing required field: {field}.")

    if assumptions.get("ticker") != ticker:
        errors.append(f"Assumptions ticker must be {ticker}.")

    scenarios = assumptions.get("scenarios")
    if not isinstance(scenarios, dict):
        errors.append("scenarios must be an object.")
        return errors

    required_scenarios = schema.get("required_scenarios", [])
    for scenario_name in required_scenarios:
        if scenario_name not in scenarios:
            errors.append(f"Missing required scenario: {scenario_name}.")

    for scenario_name, scenario in scenarios.items():
        errors.extend(_validate_scenario(str(scenario_name), scenario, schema))

    errors.extend(_validate_source_references(assumptions.get("source_references"), schema))
    return errors


def _validate_scenario(scenario_name: str, scenario: Any, schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(scenario, dict):
        return [f"Scenario {scenario_name} must be an object."]

    for field in schema.get("required_scenario_fields", []):
        if field not in scenario or scenario[field] in (None, "", []):
            errors.append(f"Scenario {scenario_name} missing required field: {field}.")

    discount_rate = scenario.get("discount_rate")
    terminal_growth_rate = scenario.get("terminal_growth_rate")
    for field in schema.get("rate_fields", []):
        value = scenario.get(field)
        if not _is_number(value):
            errors.append(f"Scenario {scenario_name} {field} must be a number.")
        elif value <= 0 or value >= 1:
            errors.append(f"Scenario {scenario_name} {field} must be greater than 0 and less than 1.")

    if _is_number(discount_rate) and _is_number(terminal_growth_rate) and terminal_growth_rate >= discount_rate:
        errors.append(f"Scenario {scenario_name} terminal_growth_rate must be lower than discount_rate.")

    starting_free_cash_flow = scenario.get("starting_free_cash_flow")
    if not _is_number(starting_free_cash_flow):
        errors.append(f"Scenario {scenario_name} starting_free_cash_flow must be a number.")

    forecast_years = scenario.get("forecast_years")
    if not isinstance(forecast_years, list) or not forecast_years:
        errors.append(f"Scenario {scenario_name} forecast_years must be a non-empty list.")
        return errors

    seen_years = set()
    for index, forecast in enumerate(forecast_years):
        if not isinstance(forecast, dict):
            errors.append(f"Scenario {scenario_name} forecast year {index} must be an object.")
            continue
        for field in schema.get("required_forecast_year_fields", []):
            if field not in forecast:
                errors.append(f"Scenario {scenario_name} forecast year {index} missing {field}.")
        year = forecast.get("year")
        free_cash_flow = forecast.get("free_cash_flow")
        if not isinstance(year, int) or year <= 0:
            errors.append(f"Scenario {scenario_name} forecast year {index} year must be a positive integer.")
        elif year in seen_years:
            errors.append(f"Scenario {scenario_name} forecast year {year} is duplicated.")
        else:
            seen_years.add(year)
        if not _is_number(free_cash_flow):
            errors.append(f"Scenario {scenario_name} forecast year {index} free_cash_flow must be a number.")

    return errors


def _validate_source_references(source_references: Any, schema: dict[str, Any]) -> list[str]:
    if not isinstance(source_references, list) or not source_references:
        return ["source_references must be a non-empty list."]

    errors = []
    for index, source_reference in enumerate(source_references):
        if not isinstance(source_reference, dict):
            errors.append(f"source_references item {index} must be an object.")
            continue
        for field in schema.get("source_reference_fields", []):
            if not source_reference.get(field):
                errors.append(f"source_references item {index} missing {field}.")
    return errors


def _calculate_scenario(scenario_name: str, scenario: dict[str, Any]) -> dict[str, Any]:
    discount_rate = scenario["discount_rate"]
    terminal_growth_rate = scenario["terminal_growth_rate"]
    forecast_years = sorted(scenario["forecast_years"], key=lambda forecast: forecast["year"])
    discounted_cash_flows = [
        {
            "year": forecast["year"],
            "free_cash_flow": forecast["free_cash_flow"],
            "present_value": forecast["free_cash_flow"] / ((1 + discount_rate) ** forecast["year"]),
        }
        for forecast in forecast_years
    ]
    final_forecast = forecast_years[-1]
    terminal_value = (
        final_forecast["free_cash_flow"]
        * (1 + terminal_growth_rate)
        / (discount_rate - terminal_growth_rate)
    )
    present_value_terminal_value = terminal_value / ((1 + discount_rate) ** final_forecast["year"])
    dcf_value = sum(item["present_value"] for item in discounted_cash_flows) + present_value_terminal_value

    return {
        "scenario": scenario_name,
        "discounted_cash_flows": discounted_cash_flows,
        "terminal_value": terminal_value,
        "present_value_terminal_value": present_value_terminal_value,
        "dcf_value": dcf_value,
    }


def _assumptions_used(assumptions: dict[str, Any]) -> dict[str, Any]:
    return {
        "assumption_label": assumptions.get("assumption_label"),
        "unit": assumptions.get("unit"),
        "scenarios": assumptions.get("scenarios"),
    }


def _warnings(assumptions: dict[str, Any]) -> list[str]:
    warnings = [
        "DCF output is deterministic arithmetic from explicit assumptions only.",
        "No assumptions were invented by the model.",
    ]
    notes = assumptions.get("assumption_notes", [])
    if isinstance(notes, list):
        warnings.extend(str(note) for note in notes)
    return warnings


def _assert_no_prohibited_language(result: dict[str, Any]) -> None:
    serialized = json.dumps(result).lower()
    found = [term for term in PROHIBITED_OUTPUT_TERMS if term in serialized]
    if found:
        raise DCFValidationError(f"DCF output contains prohibited language: {', '.join(found)}.")


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic DCF scenarios from explicit assumptions.")
    parser.add_argument("ticker")
    parser.add_argument("--assumptions-path", type=Path, required=True)
    parser.add_argument("--source-data-path", type=Path, default=DEFAULT_SOURCE_DATA_PATH)
    parser.add_argument("--context-root", type=Path, default=DEFAULT_CONTEXT_ROOT)
    parser.add_argument("--schema-path", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument("--readiness-audit-log-path", type=Path, default=check_valuation_readiness.DEFAULT_READINESS_AUDIT_LOG_PATH)
    args = parser.parse_args()

    try:
        result = run_dcf(
            ticker=args.ticker,
            assumptions_path=args.assumptions_path,
            source_data_path=args.source_data_path,
            context_root=args.context_root,
            schema_path=args.schema_path,
            readiness_audit_log_path=args.readiness_audit_log_path,
        )
    except (OSError, json.JSONDecodeError, DCFValidationError) as exc:
        print(json.dumps({"calculated": False, "error": str(exc)}, indent=2))
        return 1

    print(json.dumps(result, indent=2))
    return 0 if result.get("calculated") else 1


if __name__ == "__main__":
    raise SystemExit(main())
