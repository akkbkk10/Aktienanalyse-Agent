from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "generate_report.py"
spec = importlib.util.spec_from_file_location("generate_report", SCRIPT_PATH)
generate_report = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(generate_report)


def ratio_output() -> dict:
    return {
        "ticker": "NVDA",
        "ratio_name": "net_margin",
        "value": 0.55,
        "formula": "Net income / Revenue",
        "input_metrics_used": ["Net income", "Revenue"],
        "source_metric_references": [
            {
                "metric_name": "Net income",
                "period": "FY2025",
                "source_type": "earnings release",
                "source_date": "2025-02-26",
                "source_url": "https://investor.nvidia.com/example",
            }
        ],
        "period": "FY2025",
        "confidence": "high",
    }


class GenerateReportTests(unittest.TestCase):
    def test_report_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = generate_report.generate_report(
                ticker="NVDA",
                validation_status={"valid": True, "errors": []},
                research_gaps=[],
                ratio_outputs=[ratio_output()],
                audit_log_reference="audit_log.jsonl:1",
                reports_dir=Path(temp_dir),
                generated_at="2026-05-23T12:00:00Z",
            )

            self.assertTrue(report_path.exists())
            self.assertIn("# NVDA Fact Report", report_path.read_text(encoding="utf-8"))

    def test_source_references_are_included(self) -> None:
        report = generate_report.render_report(
            ticker="NVDA",
            validation_status={"valid": True, "errors": []},
            research_gaps=[],
            ratio_outputs=[ratio_output()],
            audit_log_reference="audit_log.jsonl:1",
            warnings=[],
            generated_at="2026-05-23T12:00:00Z",
        )

        self.assertIn("https://investor.nvidia.com/example", report)
        self.assertIn("earnings release", report)

    def test_missing_data_section(self) -> None:
        report = generate_report.render_report(
            ticker="NVDA",
            validation_status={"valid": True, "errors": []},
            research_gaps=[{"gap_type": "missing_metric", "metric_name": "Revenue", "message": "Required metric is missing."}],
            ratio_outputs=[],
            audit_log_reference="audit_log.jsonl:1",
            warnings=["Example warning"],
            generated_at="2026-05-23T12:00:00Z",
        )

        self.assertIn("## Missing Data", report)
        self.assertIn("missing_metric: Revenue", report)
        self.assertIn("## Warnings", report)

    def test_prohibited_valuation_language_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            generate_report.assert_no_prohibited_language("This includes a price target.")


if __name__ == "__main__":
    unittest.main()

