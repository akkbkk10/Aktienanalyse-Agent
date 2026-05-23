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
        "metric_name": "Revenue",
        "value": 130497,
        "unit": "USD millions",
        "period": "FY2025 ended 2025-01-26",
        "accounting_basis": "GAAP",
        "statement_type": "fact",
        "source_url": "https://example.com/report",
        "source_date": "2025-02-26",
        "last_verified": "2026-05-23",
        "confidence": "high",
    }


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
            self.assertIn("source_metadata", saved_context["metrics"][0])

    def test_missing_ticker_fails(self) -> None:
        record = valid_record()
        record["ticker"] = ""

        with self.assertRaises(build_company_context.ContextValidationError):
            build_company_context.build_context_from_records([record])

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

