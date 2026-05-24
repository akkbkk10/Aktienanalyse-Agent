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
DEFAULT_DCF_OUTPUT_SCHEMA_PATH = REPO_ROOT / "config" / "dcf_output_schema.json"
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
        result = {
            "ticker": normalized_ticker,
            "calculated": False,
            "blocking_reasons": ["Valuation readiness gate did not pass."],
            "readiness": readiness,
            "warnings": [],
            "scenarios": {},
        }
        validate_dcf_output(result)
        return result

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
        "source_metric_ids": _source_metric_ids(assumptions["source_references"]),
        "warnings": _warnings(assumptions),
        "scenarios": scenarios,
    }
    _assert_no_prohibited_language(result)
    validate_dcf_output(result)
    return result


def validate_dcf_output(
    output: dict[str, Any],
    schema: dict[str, Any] | None = None,
) -> list[str]:
    schema = schema or load_json(DEFAULT_DCF_OUTPUT_SCHEMA_PATH)
    errors: list[str] = []

    if not isinstance(output, dict):
        raise DCFValidationError("DCF output must be a JSON object.")

    for field in schema.get("required_fields", []):
        errors.extend(_validate_required_field(output, field, schema.get("field_types", {})))

    calculated = output.get("calculated")
    if calculated is True:
        errors.extend(_validate_calculated_dcf_output(output, schema))
    elif calculated is False:
        errors.extend(_validate_blocked_dcf_output(output, schema))

    if errors:
        raise DCFValidationError("; ".join(errors))

    return []


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


def _validate_calculated_dcf_output(output: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for field in schema.get("calculated_required_fields", []):
        errors.extend(_validate_required_field(output, field, schema.get("calculated_field_types", {})))

    source_references = output.get("source_references")
    if isinstance(source_references, list):
        if not source_references:
            errors.append("source_references must be a non-empty array.")
        for index, source_reference in enumerate(source_references):
            if not isinstance(source_reference, dict):
                errors.append(f"source_references item {index} must be an object.")
                continue
            for field in schema.get("source_reference_required_fields", []):
                errors.extend(
                    _validate_required_field(
                        source_reference,
                        field,
                        schema.get("source_reference_field_types", {}),
                        prefix=f"source_references item {index} ",
                    )
                )

    scenarios = output.get("scenarios")
    if isinstance(scenarios, dict):
        if not scenarios:
            errors.append("scenarios must be a non-empty object for calculated DCF output.")
        for scenario_name, scenario in scenarios.items():
            if not isinstance(scenario, dict):
                errors.append(f"Scenario {scenario_name} must be an object.")
                continue
            for field in schema.get("scenario_required_fields", []):
                errors.extend(
                    _validate_required_field(
                        scenario,
                        field,
                        schema.get("scenario_field_types", {}),
                        prefix=f"Scenario {scenario_name} ",
                    )
                )
            discounted_cash_flows = scenario.get("discounted_cash_flows")
            if isinstance(discounted_cash_flows, list):
                if not discounted_cash_flows:
                    errors.append(f"Scenario {scenario_name} discounted_cash_flows must be a non-empty array.")
                for index, cash_flow in enumerate(discounted_cash_flows):
                    if not isinstance(cash_flow, dict):
                        errors.append(f"Scenario {scenario_name} discounted_cash_flows item {index} must be an object.")
                        continue
                    for field in schema.get("discounted_cash_flow_required_fields", []):
                        errors.extend(
                            _validate_required_field(
                                cash_flow,
                                field,
                                schema.get("discounted_cash_flow_field_types", {}),
                                prefix=f"Scenario {scenario_name} discounted_cash_flows item {index} ",
                            )
                        )

    return errors


def _validate_blocked_dcf_output(output: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for field in schema.get("blocked_required_fields", []):
        errors.extend(_validate_required_field(output, field, schema.get("blocked_field_types", {})))

    scenarios = output.get("scenarios")
    if isinstance(scenarios, dict) and scenarios:
        errors.append("scenarios must be empty when DCF output is not calculated.")

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
            from datetime import date

            try:
                date.fromisoformat(value)
            except ValueError:
                errors.append(f"{field} must use ISO date format YYYY-MM-DD.")

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
        "starting_free_cash_flow_metric_id": scenario.get("starting_free_cash_flow_metric_id"),
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


def _source_metric_ids(source_references: list[dict[str, Any]]) -> list[str]:
    metric_ids = []
    for source in source_references:
        metric_id = source.get("metric_id")
        if metric_id and metric_id not in metric_ids:
            metric_ids.append(metric_id)
    return metric_ids


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
