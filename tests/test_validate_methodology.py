from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_methodology.py"
spec = importlib.util.spec_from_file_location("validate_methodology", SCRIPT_PATH)
validate_methodology = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validate_methodology)


def valid_config() -> dict:
    return validate_methodology.load_json(REPO_ROOT / "config" / "methodology_buffett_ai.json")


class ValidateMethodologyTests(unittest.TestCase):
    def test_valid_methodology_config(self) -> None:
        errors = validate_methodology.validate_methodology_config(valid_config())

        self.assertEqual(errors, [])

    def test_missing_fields_fail(self) -> None:
        config = valid_config()
        del config["allowed_valuation_methods"]

        errors = validate_methodology.validate_methodology_config(config)

        self.assertTrue(any("allowed_valuation_methods" in error for error in errors))

    def test_invalid_scenario_names_fail(self) -> None:
        config = valid_config()
        config["scenario_names"] = ["bear", "base", "bull"]

        errors = validate_methodology.validate_methodology_config(config)

        self.assertTrue(any("scenario_names" in error for error in errors))

    def test_invalid_discount_rate_rules_fail(self) -> None:
        config = valid_config()
        config["discount_rate_rules"] = copy.deepcopy(config["discount_rate_rules"])
        config["discount_rate_rules"]["default_percent"] = 20.0

        errors = validate_methodology.validate_methodology_config(config)

        self.assertTrue(any("default_percent" in error for error in errors))

    def test_version_presence_required(self) -> None:
        config = valid_config()
        config["methodology_version"] = ""

        errors = validate_methodology.validate_methodology_config(config)

        self.assertTrue(any("methodology_version" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
