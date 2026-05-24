from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "build_company_context.py"
spec = importlib.util.spec_from_file_location("build_company_context", SCRIPT_PATH)
build_company_context = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(build_company_context)


def valid_record() -> dict:
    return {
        "company": "NVIDIA Corporation",
        "ticker": "NVDA",
        "metric_id": "nvda_revenue_fy2025",
        "metric_name": "Revenue",
        "value": 130497,
        "unit": "USD millions",
        "period": "FY2025 ended 2025-01-26",
        "accounting_basis": "GAAP",
        "statement_type": "fact",
        "source_url": "https://example.com/report",
        "source_type": "earnings release",
        "source_date": "2025-02-26",
        "last_verified": "2026-05-23",
        "confidence": "high",
    }


def valid_share_count_record() -> dict:
    record = valid_record()
    record.update(
        {
            "metric_id": "nvda_diluted_weighted_average_shares_fy2025",
            "metric_name": "Diluted weighted average shares",
            "metric_category": "share_count",
            "value": 24804,
            "unit": "shares millions",
        }
    )
    return record


class BuildCompanyContextTests(unittest.TestCase):
    def test_context_creation_writes_persistent_context(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            metrics_path = temp_path / "metrics.json"
            output_root = temp_path / "companies"
            metrics_path.write_text(json.dumps([valid_record()]), encoding="utf-8")

            context = build_company_context.build_company_context(
                metrics_path=metrics_path,
                output_root=output_root,
                last_updated="2026-05-23",
            )

            output_path = output_root / "NVDA" / "context.json"
            saved_context = json.loads(output_path.read_text(encoding="utf-8"))

            self.assertEqual(context["ticker"], "NVDA")
            self.assertEqual(context["company_name"], "NVIDIA Corporation")
            self.assertEqual(context["schema_version"], "0.1.0")
            self.assertEqual(context["last_updated"], "2026-05-23")
            self.assertEqual(len(saved_context["metrics"]), 1)
            self.assertEqual(saved_context["metrics"][0]["metric_id"], "nvda_revenue_fy2025")
            self.assertIn("source_metadata", saved_context["metrics"][0])

    def test_company_context_preserves_metric_id(self) -> None:
        context = build_company_context.build_context_from_records([valid_record()])

        self.assertEqual(context["metrics"][0]["metric_id"], "nvda_revenue_fy2025")

    def test_company_context_preserves_share_count_metadata(self) -> None:
        context = build_company_context.build_context_from_records([valid_share_count_record()])

        self.assertEqual(context["metrics"][0]["metric_id"], "nvda_diluted_weighted_average_shares_fy2025")
        self.assertEqual(context["metrics"][0]["metric_category"], "share_count")
        self.assertEqual(context["metrics"][0]["unit"], "shares millions")

    def test_existing_company_context_files_satisfy_contract(self) -> None:
        for ticker in ["NVDA", "AMD", "TSMC"]:
            with self.subTest(ticker=ticker):
                context_path = REPO_ROOT / "data" / "companies" / ticker / "context.json"
                context = json.loads(context_path.read_text(encoding="utf-8"))

                self.assertEqual(build_company_context.validate_company_context(context), [])

    def test_missing_ticker_fails(self) -> None:
        record = valid_record()
        record["ticker"] = ""

        with self.assertRaises(build_company_context.ContextValidationError):
            build_company_context.build_context_from_records([record])

    def test_missing_required_top_level_field_fails_contract_validation(self) -> None:
        context = build_company_context.build_context_from_records([valid_record()])
        del context["company_name"]

        with self.assertRaises(build_company_context.ContextValidationError):
            build_company_context.validate_company_context(context)

    def test_invalid_required_top_level_field_type_fails_contract_validation(self) -> None:
        context = build_company_context.build_context_from_records([valid_record()])
        context["ticker"] = 123

        with self.assertRaises(build_company_context.ContextValidationError):
            build_company_context.validate_company_context(context)

    def test_missing_metrics_fails(self) -> None:
        context = {
            "schema_version": "0.1.0",
            "ticker": "NVDA",
            "company_name": "NVIDIA Corporation",
            "last_updated": "2026-05-23",
            "metrics": [],
            "source_metadata": {"source_file": None, "metric_count": 0},
        }

        with self.assertRaises(build_company_context.ContextValidationError):
            build_company_context.validate_company_context(context)

    def test_missing_context_metric_source_metadata_field_fails_contract_validation(self) -> None:
        context = build_company_context.build_context_from_records([valid_record()])
        del context["metrics"][0]["source_metadata"]["source_url"]

        with self.assertRaises(build_company_context.ContextValidationError):
            build_company_context.validate_company_context(context)

    def test_invalid_source_metadata_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            metrics_path = temp_path / "metrics.json"
            record = valid_record()
            record["source_url"] = ""
            metrics_path.write_text(json.dumps([record]), encoding="utf-8")

            with self.assertRaises(build_company_context.ContextValidationError):
                build_company_context.build_company_context(metrics_path=metrics_path, output_root=temp_path)


if __name__ == "__main__":
    unittest.main()

