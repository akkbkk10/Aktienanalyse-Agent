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


def dcf_output() -> dict:
    return {
        "ticker": "NVDA",
        "calculated": True,
        "unit": "USD millions",
        "formulas": {
            "dcf_value": "sum(present_value_free_cash_flow) + present_value_terminal_value",
        },
        "assumptions_used": {
            "assumption_label": "Example assumptions for deterministic DCF calculation tests",
            "unit": "USD millions",
            "scenarios": {
                "bear": {
                    "discount_rate": 0.12,
                    "terminal_growth_rate": 0.02,
                    "starting_free_cash_flow": 60724,
                    "forecast_years": [{"year": 1, "free_cash_flow": 62000}],
                },
                "base": {
                    "discount_rate": 0.10,
                    "terminal_growth_rate": 0.03,
                    "starting_free_cash_flow": 60724,
                    "forecast_years": [{"year": 1, "free_cash_flow": 66000}],
                },
                "bull": {
                    "discount_rate": 0.09,
                    "terminal_growth_rate": 0.035,
                    "starting_free_cash_flow": 60724,
                    "forecast_years": [{"year": 1, "free_cash_flow": 70000}],
                },
            },
        },
        "source_references": [
            {
                "metric_name": "Free cash flow",
                "period": "FY2025",
                "source_date": "2025-02-26",
                "source_url": "https://investor.nvidia.com/example",
            }
        ],
        "warnings": [
            "DCF output is deterministic arithmetic from explicit assumptions only.",
            "No assumptions were invented by the model.",
        ],
        "scenarios": {
            "bear": {"dcf_value": 100, "terminal_value": 80, "present_value_terminal_value": 70},
            "base": {"dcf_value": 200, "terminal_value": 160, "present_value_terminal_value": 140},
            "bull": {"dcf_value": 300, "terminal_value": 240, "present_value_terminal_value": 210},
        },
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
            dcf_output=None,
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
            dcf_output=None,
            warnings=["Example warning"],
            generated_at="2026-05-23T12:00:00Z",
        )

        self.assertIn("## Missing Data", report)
        self.assertIn("missing_metric: Revenue", report)
        self.assertIn("## Warnings", report)

    def test_prohibited_valuation_language_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            generate_report.assert_no_prohibited_language("This includes a price target.")

    def test_report_without_dcf_excludes_dcf_section(self) -> None:
        report = generate_report.render_report(
            ticker="NVDA",
            validation_status={"valid": True, "errors": []},
            research_gaps=[],
            ratio_outputs=[ratio_output()],
            audit_log_reference="audit_log.jsonl:1",
            dcf_output=None,
            warnings=[],
            generated_at="2026-05-23T12:00:00Z",
        )

        self.assertNotIn("### DCF Calculation Output", report)

    def test_report_with_dcf_includes_scenarios(self) -> None:
        report = generate_report.render_report(
            ticker="NVDA",
            validation_status={"valid": True, "errors": []},
            research_gaps=[],
            ratio_outputs=[ratio_output()],
            audit_log_reference="audit_log.jsonl:1",
            dcf_output=dcf_output(),
            warnings=[],
            generated_at="2026-05-23T12:00:00Z",
        )

        self.assertIn("### DCF Calculation Output", report)
        self.assertIn("- bear:", report)
        self.assertIn("- base:", report)
        self.assertIn("- bull:", report)

    def test_dcf_assumptions_are_shown_clearly(self) -> None:
        report = generate_report.render_report(
            ticker="NVDA",
            validation_status={"valid": True, "errors": []},
            research_gaps=[],
            ratio_outputs=[ratio_output()],
            audit_log_reference="audit_log.jsonl:1",
            dcf_output=dcf_output(),
            warnings=[],
            generated_at="2026-05-23T12:00:00Z",
        )

        self.assertIn("#### Assumptions Used", report)
        self.assertIn("Discount rate: 0.1", report)
        self.assertIn("Starting free cash flow: 60724", report)

    def test_dcf_warnings_are_shown_clearly(self) -> None:
        report = generate_report.render_report(
            ticker="NVDA",
            validation_status={"valid": True, "errors": []},
            research_gaps=[],
            ratio_outputs=[ratio_output()],
            audit_log_reference="audit_log.jsonl:1",
            dcf_output=dcf_output(),
            warnings=[],
            generated_at="2026-05-23T12:00:00Z",
        )

        self.assertIn("#### DCF Warnings", report)
        self.assertIn("No assumptions were invented by the model.", report)

    def test_dcf_report_has_no_recommendation_or_price_target_language(self) -> None:
        report = generate_report.render_report(
            ticker="NVDA",
            validation_status={"valid": True, "errors": []},
            research_gaps=[],
            ratio_outputs=[ratio_output()],
            audit_log_reference="audit_log.jsonl:1",
            dcf_output=dcf_output(),
            warnings=[],
            generated_at="2026-05-23T12:00:00Z",
        )
        normalized_report = report.lower()

        for term in ["price target", "buy", "sell", "hold", "recommendation"]:
            self.assertNotIn(term, normalized_report)

        generate_report.assert_no_prohibited_language(report)


if __name__ == "__main__":
    unittest.main()

