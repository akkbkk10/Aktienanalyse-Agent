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


def fair_value_output() -> dict:
    return {
        "ticker": "NVDA",
        "calculated": True,
        "currency": "USD",
        "formulas": {"fair_value_per_share": "dcf_value_used / diluted_share_count_used"},
        "assumptions": {
            "dcf_output_unit": "USD millions",
            "share_count_unit": "shares millions",
            "share_count_period": "FY2025",
            "share_count_metric_id": "nvda_diluted_weighted_average_shares_fy2025",
        },
        "warnings": ["Fair value per share is deterministic arithmetic from existing DCF output and sourced share count only."],
        "source_references": [
            {
                "metric_id": "nvda_diluted_weighted_average_shares_fy2025",
                "metric_name": "Diluted weighted average shares",
                "period": "FY2025",
                "source_type": "investor relations",
                "source_date": "2025-02-26",
                "source_url": "https://investor.nvidia.com/example",
            }
        ],
        "disclaimer": "calculated model output only, not investment advice.",
        "scenarios": [
            {
                "scenario": "base",
                "fair_value_per_share": 12.0,
                "dcf_value_used": 1200,
                "share_count_used": 100,
                "share_count_metric_id": "nvda_diluted_weighted_average_shares_fy2025",
            }
        ],
    }


def model_rating_output() -> dict:
    return {
        "ticker": "NVDA",
        "model_rating": 3,
        "rating_label": "fairly valued / neutral on model basis",
        "fair_value_per_share_used": 12.0,
        "market_price_used": 11.5,
        "valuation_gap_percent": 4.3,
        "rules_version": "0.1.0",
        "assumptions": {
            "scenario_used": "base",
            "valuation_gap_formula": "(fair_value_per_share - current_market_price) / current_market_price",
            "market_price_metric_id": "nvda_current_market_price_2026_05_23",
            "market_price_as_of_datetime": "2026-05-23T00:15:00Z",
            "market_price_fetched_at": "2026-05-24T00:00:00Z",
        },
        "warnings": ["Model rating is a deterministic rule-based classification from fair value per share and sourced market price only."],
        "source_references": [
            {
                "metric_id": "nvda_current_market_price_2026_05_23",
                "metric_name": "Current market price",
                "period": "Latest trade timestamp 2026-05-23 00:15 UTC",
                "source_type": "market data",
                "source_date": "2026-05-23",
                "source_url": "https://www.nasdaq.com/market-activity/stocks/nvda",
                "as_of_datetime": "2026-05-23T00:15:00Z",
                "fetched_at": "2026-05-24T00:00:00Z",
            }
        ],
        "disclaimer": "non-personalized model output, not investment advice.",
    }


def model_confidence_output() -> dict:
    return {
        "ticker": "NVDA",
        "model_confidence": "A",
        "confidence_label": "high data quality, low uncertainty",
        "confidence_score": 100,
        "reasons": ["Validated inputs, source freshness, research gaps, and assumptions meet model quality rules."],
        "warnings": [],
        "rules_version": "0.1.0",
        "source_references": [
            {
                "metric_id": "nvda_current_market_price_2026_05_23",
                "metric_name": "Current market price",
                "metric_category": "market_price",
                "period": "Latest trade timestamp 2026-05-23 00:15 UTC",
                "source_type": "market data",
                "source_date": "2026-05-23",
                "source_url": "https://www.nasdaq.com/market-activity/stocks/nvda",
                "as_of_datetime": "2026-05-23T00:15:00Z",
                "fetched_at": "2026-05-24T00:00:00Z",
            }
        ],
        "disclaimer": "non-personalized model quality output, not investment advice.",
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

    def test_report_includes_model_rating_only_as_model_output(self) -> None:
        report = generate_report.render_report(
            ticker="NVDA",
            validation_status={"valid": True, "errors": []},
            research_gaps=[],
            ratio_outputs=[ratio_output()],
            audit_log_reference="audit_log.jsonl:1",
            dcf_output=dcf_output(),
            fair_value_per_share_output=fair_value_output(),
            model_rating_output=model_rating_output(),
            warnings=[],
            generated_at="2026-05-24T12:00:00Z",
        )

        self.assertIn("### Model Rating", report)
        self.assertIn("non-personalized model output, not investment advice", report)
        self.assertIn("fairly valued / neutral on model basis", report)
        self.assertIn("as_of_datetime: 2026-05-23T00:15:00Z", report)
        self.assertIn("fetched_at: 2026-05-24T00:00:00Z", report)
        for term in ["price target", "buy", "sell", "hold", "recommendation"]:
            self.assertNotIn(term, report.lower())

        generate_report.assert_no_prohibited_language(report)

    def test_report_includes_model_confidence_only_as_model_quality(self) -> None:
        report = generate_report.render_report(
            ticker="NVDA",
            validation_status={"valid": True, "errors": []},
            research_gaps=[],
            ratio_outputs=[ratio_output()],
            audit_log_reference="audit_log.jsonl:1",
            dcf_output=dcf_output(),
            model_confidence_output=model_confidence_output(),
            warnings=[],
            generated_at="2026-05-24T12:00:00Z",
        )

        self.assertIn("### Model Confidence", report)
        self.assertIn("non-personalized model quality output, not investment advice", report)
        self.assertIn("high data quality, low uncertainty", report)
        self.assertIn("as_of_datetime: 2026-05-23T00:15:00Z", report)
        self.assertIn("fetched_at: 2026-05-24T00:00:00Z", report)
        for term in ["price target", "buy", "sell", "hold", "recommendation"]:
            self.assertNotIn(term, report.lower())

        generate_report.assert_no_prohibited_language(report)

    def test_report_includes_fair_value_only_as_model_calculation(self) -> None:
        report = generate_report.render_report(
            ticker="NVDA",
            validation_status={"valid": True, "errors": []},
            research_gaps=[],
            ratio_outputs=[ratio_output()],
            audit_log_reference="audit_log.jsonl:1",
            dcf_output=dcf_output(),
            fair_value_per_share_output=fair_value_output(),
            warnings=[],
            generated_at="2026-05-23T12:00:00Z",
        )

        self.assertIn("### Fair Value Per Share Model Calculation", report)
        self.assertIn("Share count metric ID: nvda_diluted_weighted_average_shares_fy2025", report)
        self.assertIn("calculated model output only, not investment advice", report)
        for term in ["price target", "buy", "sell", "hold", "recommendation"]:
            self.assertNotIn(term, report.lower())

        generate_report.assert_no_prohibited_language(report)


if __name__ == "__main__":
    unittest.main()

