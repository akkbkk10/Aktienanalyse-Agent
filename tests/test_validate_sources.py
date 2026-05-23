from __future__ import annotations

import importlib.util
import json
import tempfile
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
        "metric_id": "exm_revenue_fy2025",
        "metric_name": "Revenue",
        "value": 1.0,
        "unit": "EUR",
        "period": "FY2025",
        "accounting_basis": "GAAP",
        "statement_type": "fact",
        "source_url": "https://example.com/report",
        "source_type": "earnings release",
        "source_date": "2026-01-15",
        "last_verified": date.today().isoformat(),
        "confidence": "high",
    }


def valid_share_count_record() -> dict:
    record = valid_record()
    record.update(
        {
            "metric_id": "exm_diluted_weighted_average_shares_fy2025",
            "metric_name": "Diluted weighted average shares",
            "metric_category": "share_count",
            "value": 100.0,
            "unit": "shares millions",
        }
    )
    return record


class ValidateSourcesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = validate_sources.load_json(REPO_ROOT / "config" / "financial_metric_schema.json")
        self.rules = validate_sources.load_json(REPO_ROOT / "config" / "source_rules.json")

    def test_valid_record_has_no_errors(self) -> None:
        errors = validate_sources.validate_records([valid_record()], self.schema, self.rules)

        self.assertEqual(errors, [])

    def test_allowed_source_type_has_no_errors(self) -> None:
        record = valid_record()
        record["source_type"] = "SEC filing"

        errors = validate_sources.validate_records([record], self.schema, self.rules)

        self.assertEqual(errors, [])

    def test_disallowed_source_type_fails(self) -> None:
        record = valid_record()
        record["source_type"] = "social media"

        errors = validate_sources.validate_records([record], self.schema, self.rules)

        self.assertTrue(any(error.field == "source_type" for error in errors))

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

    def test_missing_metric_id_fails_validation(self) -> None:
        record = valid_record()
        del record["metric_id"]

        errors = validate_sources.validate_records([record], self.schema, self.rules)

        self.assertTrue(any(error.field == "metric_id" for error in errors))

    def test_valid_share_count_record_has_no_errors(self) -> None:
        errors = validate_sources.validate_records([valid_share_count_record()], self.schema, self.rules)

        self.assertEqual(errors, [])

    def test_share_count_missing_metric_id_fails_validation(self) -> None:
        record = valid_share_count_record()
        del record["metric_id"]

        errors = validate_sources.validate_records([record], self.schema, self.rules)

        self.assertTrue(any(error.field == "metric_id" for error in errors))

    def test_share_count_missing_source_metadata_fails_validation(self) -> None:
        record = valid_share_count_record()
        del record["source_date"]

        errors = validate_sources.validate_records([record], self.schema, self.rules)

        self.assertTrue(any(error.field == "source_date" for error in errors))

    def test_empty_metric_id_fails_validation(self) -> None:
        record = valid_record()
        record["metric_id"] = ""

        errors = validate_sources.validate_records([record], self.schema, self.rules)

        self.assertTrue(any(error.field == "metric_id" for error in errors))

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

    def test_gaap_and_non_gaap_values_are_separate(self) -> None:
        gaap_record = valid_record()
        non_gaap_record = valid_record()
        non_gaap_record["accounting_basis"] = "Non-GAAP"
        non_gaap_record["value"] = 2.0

        errors = validate_sources.validate_records([gaap_record, non_gaap_record], self.schema, self.rules)

        self.assertFalse(any("Conflicting value" in error.message for error in errors))

    def test_conflicting_values_fail(self) -> None:
        first_record = valid_record()
        second_record = valid_record()
        second_record["value"] = 2.0

        errors = validate_sources.validate_records([first_record, second_record], self.schema, self.rules)

        self.assertTrue(any("Conflicting value" in error.message for error in errors))

    def test_validation_errors_create_research_queue_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "metrics.json"
            json_queue_path = temp_path / "research_queue.json"
            markdown_queue_path = temp_path / "research_queue.md"
            record = valid_record()
            record["source_url"] = ""
            input_path.write_text(json.dumps([record]), encoding="utf-8")

            result = validate_sources.create_queue_entries_for_validation_errors(
                input_path=input_path,
                markdown_queue_path=markdown_queue_path,
                json_queue_path=json_queue_path,
            )

            queue = json.loads(json_queue_path.read_text(encoding="utf-8"))

            self.assertGreaterEqual(result["created_count"], 1)
            self.assertEqual(queue["items"][0]["source"], "source_validation_agent")

    def test_nvda_sample_data_passes_validation(self) -> None:
        errors = validate_sources.validate_file(REPO_ROOT / "data" / "nvda_sample_metrics.json")

        self.assertEqual(errors, [])

    def test_amd_sample_data_passes_validation(self) -> None:
        errors = validate_sources.validate_file(REPO_ROOT / "data" / "amd_sample_metrics.json")

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
