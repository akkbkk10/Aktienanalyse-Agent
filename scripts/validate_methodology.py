from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_METHODOLOGY_PATH = REPO_ROOT / "config" / "methodology_buffett_ai.json"
REQUIRED_FIELDS = [
    "methodology_version",
    "allowed_valuation_methods",
    "required_ratio_inputs",
    "scenario_names",
    "discount_rate_rules",
    "margin_of_safety_rules",
    "prohibited_outputs_before_valuation_stage",
]
ALLOWED_SCENARIO_NAMES = {"conservative", "base", "optimistic"}
REQUIRED_PROHIBITED_OUTPUTS = {
    "DCF",
    "fair value",
    "intrinsic value",
    "price target",
    "recommendation",
    "memo generation",
    "investment advice",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_methodology_config(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in config:
            errors.append(f"Missing required field: {field}.")

    if not config.get("methodology_version"):
        errors.append("methodology_version must be present and non-empty.")

    errors.extend(_validate_non_empty_list(config, "allowed_valuation_methods"))
    errors.extend(_validate_non_empty_list(config, "required_ratio_inputs"))
    errors.extend(_validate_scenarios(config.get("scenario_names")))
    errors.extend(_validate_discount_rate_rules(config.get("discount_rate_rules")))
    errors.extend(_validate_margin_of_safety_rules(config.get("margin_of_safety_rules")))
    errors.extend(_validate_prohibited_outputs(config.get("prohibited_outputs_before_valuation_stage")))

    return errors


def validate_methodology_file(path: Path = DEFAULT_METHODOLOGY_PATH) -> list[str]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        return ["Methodology config must be a JSON object."]
    return validate_methodology_config(payload)


def _validate_non_empty_list(config: dict[str, Any], field: str) -> list[str]:
    value = config.get(field)
    if not isinstance(value, list) or not value:
        return [f"{field} must be a non-empty list."]
    if not all(isinstance(item, str) and item.strip() for item in value):
        return [f"{field} must contain only non-empty strings."]
    return []


def _validate_scenarios(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        return ["scenario_names must be a non-empty list."]
    if set(value) != ALLOWED_SCENARIO_NAMES:
        return ["scenario_names must contain exactly conservative, base, and optimistic."]
    return []


def _validate_discount_rate_rules(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["discount_rate_rules must be an object."]

    errors = []
    for field in ["min_percent", "max_percent", "default_percent"]:
        if not isinstance(value.get(field), (int, float)):
            errors.append(f"discount_rate_rules.{field} must be numeric.")

    if errors:
        return errors

    min_percent = value["min_percent"]
    max_percent = value["max_percent"]
    default_percent = value["default_percent"]

    if min_percent < 0:
        errors.append("discount_rate_rules.min_percent must be non-negative.")
    if max_percent <= min_percent:
        errors.append("discount_rate_rules.max_percent must be greater than min_percent.")
    if not min_percent <= default_percent <= max_percent:
        errors.append("discount_rate_rules.default_percent must be within min_percent and max_percent.")
    if value.get("requires_source_or_assumption") is not True:
        errors.append("discount_rate_rules.requires_source_or_assumption must be true.")

    return errors


def _validate_margin_of_safety_rules(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["margin_of_safety_rules must be an object."]
    if not isinstance(value.get("minimum_percent"), (int, float)):
        return ["margin_of_safety_rules.minimum_percent must be numeric."]
    if value["minimum_percent"] < 0:
        return ["margin_of_safety_rules.minimum_percent must be non-negative."]
    if value.get("requires_explicit_scenario") is not True:
        return ["margin_of_safety_rules.requires_explicit_scenario must be true."]
    return []


def _validate_prohibited_outputs(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        return ["prohibited_outputs_before_valuation_stage must be a non-empty list."]

    missing = REQUIRED_PROHIBITED_OUTPUTS - set(value)
    if missing:
        return [f"prohibited_outputs_before_valuation_stage missing: {', '.join(sorted(missing))}."]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate valuation methodology configuration without running valuation.")
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_METHODOLOGY_PATH)
    args = parser.parse_args()

    try:
        errors = validate_methodology_file(args.path)
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
        return 2

    print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

