from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "generate_analysis_summary.py"
spec = importlib.util.spec_from_file_location("generate_analysis_summary", SCRIPT_PATH)
generate_analysis_summary = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(generate_analysis_summary)


def ratio_output() -> dict:
    return {
        "ticker": "NVDA",
        "ratio_name": "free_cash_flow_margin",
        "value": 0.46,
        "formula": "Free cash flow / Revenue",
        "period": "FY2025",
        "confidence": "high",
        "source_metric_references": [
            {
                "metric_name": "Free cash flow",
                "period": "FY2025",
                "source_url": "https://investor.nvidia.com/example",
                "source_date": "2025-02-26",
                "confidence": "high",
            }
        ],
    }


def dcf_output() -> dict:
    return {
        "ticker": "NVDA",
        "calculated": True,
        "unit": "USD millions",
        "assumptions_used": {
            "assumption_label": "Example assumptions",
            "scenarios": {
                "bear": {"discount_rate": 0.12, "terminal_growth_rate": 0.02},
                "base": {"discount_rate": 0.10, "terminal_growth_rate": 0.03},
                "bull": {"discount_rate": 0.09, "terminal_growth_rate": 0.035},
            },
        },
        "scenarios": {
            "bear": {"dcf_value": 100},
            "base": {"dcf_value": 200},
            "bull": {"dcf_value": 300},
        },
        "warnings": ["DCF output is deterministic arithmetic from explicit assumptions only."],
        "source_references": [
            {
                "metric_name": "Free cash flow",
                "period": "FY2025",
                "source_url": "https://investor.nvidia.com/example",
                "source_date": "2025-02-26",
                "confidence": "high",
            }
        ],
    }


class GenerateAnalysisSummaryTests(unittest.TestCase):
    def test_summary_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = generate_analysis_summary.generate_analysis_summary(
                ticker="NVDA",
                validation_status={"valid": True, "errors": []},
                research_gaps=[],
                ratio_outputs=[ratio_output()],
                audit_log_reference="audit_log.jsonl:1",
                dcf_output=dcf_output(),
                reports_dir=Path(temp_dir),
                generated_at="2026-05-23T12:00:00Z",
            )

            self.assertTrue(output_path.exists())
            summary = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["ticker"], "NVDA")
            self.assertEqual(summary["audit_log_reference"], "audit_log.jsonl:1")

    def test_facts_assumptions_calculations_are_separated(self) -> None:
        summary = generate_analysis_summary.build_analysis_summary(
            ticker="NVDA",
            validation_status={"valid": True, "errors": []},
            research_gaps=[],
            ratio_outputs=[ratio_output()],
            audit_log_reference="audit_log.jsonl:1",
            dcf_output=dcf_output(),
            warnings=["Source freshness checked."],
            generated_at="2026-05-23T12:00:00Z",
        )

        for section in ["facts", "assumptions", "calculated_outputs", "missing_data", "risks_warnings"]:
            self.assertIn(section, summary)
        self.assertIn("validation_status", summary["facts"])
        self.assertIn("dcf_assumptions", summary["assumptions"])
        self.assertIn("ratios", summary["calculated_outputs"])

    def test_dcf_included_when_available(self) -> None:
        summary = generate_analysis_summary.build_analysis_summary(
            ticker="NVDA",
            validation_status={"valid": True, "errors": []},
            research_gaps=[],
            ratio_outputs=[ratio_output()],
            audit_log_reference="audit_log.jsonl:1",
            dcf_output=dcf_output(),
            generated_at="2026-05-23T12:00:00Z",
        )

        self.assertTrue(summary["assumptions"]["dcf_available"])
        self.assertEqual(set(summary["calculated_outputs"]["dcf_scenarios"]), {"bear", "base", "bull"})

    def test_missing_dcf_handled_cleanly(self) -> None:
        summary = generate_analysis_summary.build_analysis_summary(
            ticker="NVDA",
            validation_status={"valid": True, "errors": []},
            research_gaps=[],
            ratio_outputs=[ratio_output()],
            audit_log_reference="audit_log.jsonl:1",
            dcf_output=None,
            generated_at="2026-05-23T12:00:00Z",
        )

        self.assertFalse(summary["assumptions"]["dcf_available"])
        self.assertIsNone(summary["assumptions"]["dcf_assumptions"])
        self.assertEqual(summary["calculated_outputs"]["dcf_scenarios"], {})
        self.assertEqual(summary["missing_data"]["dcf_status"], "not provided")

    def test_no_buy_sell_hold_recommendation_language(self) -> None:
        summary = generate_analysis_summary.build_analysis_summary(
            ticker="NVDA",
            validation_status={"valid": True, "errors": []},
            research_gaps=[],
            ratio_outputs=[ratio_output()],
            audit_log_reference="audit_log.jsonl:1",
            dcf_output=dcf_output(),
            generated_at="2026-05-23T12:00:00Z",
        )
        serialized = json.dumps(summary).lower()

        for term in ["buy", "sell", "hold", "recommendation"]:
            self.assertNotIn(term, serialized)

    def test_no_price_target_language(self) -> None:
        summary = generate_analysis_summary.build_analysis_summary(
            ticker="NVDA",
            validation_status={"valid": True, "errors": []},
            research_gaps=[],
            ratio_outputs=[ratio_output()],
            audit_log_reference="audit_log.jsonl:1",
            dcf_output=dcf_output(),
            generated_at="2026-05-23T12:00:00Z",
        )

        self.assertNotIn("price target", json.dumps(summary).lower())

    def test_no_investment_advice(self) -> None:
        summary = generate_analysis_summary.build_analysis_summary(
            ticker="NVDA",
            validation_status={"valid": True, "errors": []},
            research_gaps=[],
            ratio_outputs=[ratio_output()],
            audit_log_reference="audit_log.jsonl:1",
            dcf_output=dcf_output(),
            generated_at="2026-05-23T12:00:00Z",
        )

        generate_analysis_summary.assert_no_prohibited_language(summary)
        self.assertNotIn("investment advice", json.dumps(summary).lower())


if __name__ == "__main__":
    unittest.main()
