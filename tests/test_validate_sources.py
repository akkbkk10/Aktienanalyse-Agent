from __future__ import annotations

import importlib.util
import unittest
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_sources.py"
spec = importlib.util.spec_from_file_location("validate_sources", SCRIPT_PATH)
validate_sources = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validate_sources)


def valid_record() -> dict:
    return {
        "company": "Example AG",
        "ticker": "EXM",
        "metric_name": "Revenue",
        "value": 1.0,
        "unit": "EUR",
        "period": "FY2025",
        "accounting_basis": "GAAP",
        "statement_type": "fact",
        "source_url": "https://example.com/report",
        "source_date": "2026-01-15",
        "last_verified": date.today().isoformat(),
        "confidence": "high",
    }


class ValidateSourcesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = validate_sources.load_json(REPO_ROOT / "config" / "financial_metric_schema.json")
        self.rules = validate_sources.load_json(REPO_ROOT / "config" / "source_rules.json")

    def test_valid_record_has_no_errors(self) -> None:
        errors = validate_sources.validate_records([valid_record()], self.schema, self.rules)

        self.assertEqual(errors, [])

    def test_missing_evidence_metadata_fails(self) -> None:
        record = valid_record()
        del record["source_url"]

        errors = validate_sources.validate_records([record], self.schema, self.rules)

        self.assertTrue(any(error.field == "source_url" for error in errors))

    def test_missing_source_url_fails(self) -> None:
        record = valid_record()
        record["source_url"] = ""

        errors = validate_sources.validate_records([record], self.schema, self.rules)

        self.assertTrue(any(error.field == "source_url" for error in errors))

    def test_missing_unit_fails(self) -> None:
        record = valid_record()
        record["unit"] = ""

        errors = validate_sources.validate_records([record], self.schema, self.rules)

        self.assertTrue(any(error.field == "unit" for error in errors))

    def test_invalid_accounting_basis_fails(self) -> None:
        record = valid_record()
        record["accounting_basis"] = "Adjusted"

        errors = validate_sources.validate_records([record], self.schema, self.rules)

        self.assertTrue(any(error.field == "accounting_basis" for error in errors))

    def test_http_source_url_fails(self) -> None:
        record = valid_record()
        record["source_url"] = "http://example.com/report"

        errors = validate_sources.validate_records([record], self.schema, self.rules)

        self.assertTrue(any(error.field == "source_url" for error in errors))

    def test_stale_last_verified_fails(self) -> None:
        record = valid_record()
        record["last_verified"] = "2025-01-01"

        errors = validate_sources.validate_records(
            [record],
            self.schema,
            self.rules,
            today=date(2026, 5, 23),
        )

        self.assertTrue(any(error.field == "last_verified" for error in errors))

    def test_invalid_confidence_fails(self) -> None:
        record = valid_record()
        record["confidence"] = "certain"

        errors = validate_sources.validate_records([record], self.schema, self.rules)

        self.assertTrue(any(error.field == "confidence" for error in errors))


if __name__ == "__main__":
    unittest.main()
