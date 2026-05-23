from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_analysis.py"
spec = importlib.util.spec_from_file_location("run_analysis", SCRIPT_PATH)
run_analysis = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run_analysis)


class RunAnalysisTests(unittest.TestCase):
    def test_successful_nvda_run(self) -> None:
        with temp_analysis_workspace() as paths:
            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
            )

            self.assertEqual(result["ticker"], "NVDA")
            self.assertTrue(result["validation_status"]["valid"])
            self.assertEqual(result["research_gaps_count"], 0)
            self.assertIn("net_margin", result["ratios_calculated"])
            self.assertTrue(result["audit_log_written"])
            self.assertIsNone(result["report_path"])
            self.assertIsNone(result["analysis_summary_path"])
            self.assertFalse(result["dcf_run"])
            self.assertEqual(result["dcf_scenarios_calculated"], [])
            self.assertIsNone(result["dcf_output_path"])
            self.assertIsNone(result["fair_value_per_share_output_path"])
            self.assertIsNone(result["model_rating_output_path"])
            self.assertEqual(result["dcf_warnings"], [])
            self.assertEqual(result["warnings"], [])

    def test_missing_context_warns_when_rebuild_disabled(self) -> None:
        with temp_analysis_workspace() as paths:
            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
                rebuild_context=False,
            )

            self.assertTrue(result["validation_status"]["valid"])
            self.assertFalse(result["audit_log_written"])
            self.assertTrue(any("Company context missing" in warning for warning in result["warnings"]))

    def test_validation_failure_stops_before_audit(self) -> None:
        with temp_analysis_workspace() as paths:
            broken_source = paths["root"] / "broken_metrics.json"
            records = json.loads(paths["source_data"].read_text(encoding="utf-8"))
            del records[0]["source_url"]
            broken_source.write_text(json.dumps(records), encoding="utf-8")

            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=broken_source,
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
            )

            self.assertFalse(result["validation_status"]["valid"])
            self.assertEqual(result["ratios_calculated"], [])
            self.assertFalse(result["audit_log_written"])

    def test_audit_log_creation(self) -> None:
        with temp_analysis_workspace() as paths:
            run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
            )

            lines = paths["audit_log"].read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            record = json.loads(lines[0])
            self.assertEqual(record["ticker"], "NVDA")
            self.assertTrue(record["ratio_outputs"])

    def test_orchestrator_report_generation(self) -> None:
        with temp_analysis_workspace() as paths:
            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
                generate_fact_report=True,
            )

            report_path = Path(result["report_path"])
            report = report_path.read_text(encoding="utf-8")

            self.assertTrue(report_path.exists())
            self.assertIn("# NVDA Fact Report", report)
            self.assertIn("## Facts", report)

    def test_report_path_output_when_report_created(self) -> None:
        with temp_analysis_workspace() as paths:
            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
                generate_fact_report=True,
            )

            self.assertIsNotNone(result["report_path"])
            self.assertTrue(result["report_path"].endswith("NVDA_fact_report.md"))

    def test_no_report_mode(self) -> None:
        with temp_analysis_workspace() as paths:
            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
                generate_fact_report=False,
            )

            self.assertIsNone(result["report_path"])
            self.assertIsNone(result["analysis_summary_path"])
            self.assertFalse((paths["reports_dir"] / "NVDA_fact_report.md").exists())

    def test_summary_generation_without_dcf(self) -> None:
        with temp_analysis_workspace() as paths:
            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
                generate_summary=True,
            )

            summary_path = Path(result["analysis_summary_path"])
            summary = json.loads(summary_path.read_text(encoding="utf-8"))

            self.assertTrue(summary_path.exists())
            self.assertFalse(summary["assumptions"]["dcf_available"])
            self.assertEqual(summary["missing_data"]["dcf_status"], "not provided")
            self.assertIsNone(result["dcf_output_path"])
            self.assertTrue((paths["reports_dir"] / "NVDA_valuation_readiness_audit_probe.jsonl").exists())

    def test_summary_generation_with_dcf(self) -> None:
        with temp_analysis_workspace() as paths:
            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
                generate_summary=True,
                run_dcf=True,
                dcf_assumptions_path=paths["dcf_assumptions"],
            )

            summary = json.loads(Path(result["analysis_summary_path"]).read_text(encoding="utf-8"))

            self.assertTrue(result["dcf_run"])
            self.assertTrue(summary["assumptions"]["dcf_available"])
            self.assertEqual(set(summary["calculated_outputs"]["dcf_scenarios"]), {"bear", "base", "bull"})

    def test_summary_path_in_orchestrator_output(self) -> None:
        with temp_analysis_workspace() as paths:
            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
                generate_summary=True,
            )

            self.assertIsNotNone(result["analysis_summary_path"])
            self.assertTrue(result["analysis_summary_path"].endswith("NVDA_analysis_summary.json"))

    def test_orchestrator_without_dcf(self) -> None:
        with temp_analysis_workspace() as paths:
            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
                run_dcf=False,
            )

            self.assertFalse(result["dcf_run"])
            self.assertEqual(result["dcf_scenarios_calculated"], [])
            self.assertIsNone(result["dcf_output_path"])

    def test_orchestrator_with_dcf(self) -> None:
        with temp_analysis_workspace() as paths:
            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
                run_dcf=True,
                dcf_assumptions_path=paths["dcf_assumptions"],
            )

            self.assertTrue(result["dcf_run"])
            self.assertEqual(result["dcf_scenarios_calculated"], ["base", "bear", "bull"])
            self.assertIsNotNone(result["fair_value_per_share_output_path"])
            self.assertIsNotNone(result["model_rating_output_path"])
            self.assertTrue(result["dcf_warnings"])

    def test_readiness_gate_blocks_dcf(self) -> None:
        with temp_analysis_workspace() as paths:
            watchlist_path = paths["root"] / "watchlist_with_gap.json"
            watchlist_path.write_text(
                json.dumps(
                    {
                        "tickers": {
                            "NVDA": {
                                "company_name": "NVIDIA Corporation",
                                "required_metrics": ["Revenue", "Uncollected required metric"],
                                "max_last_verified_age_days": 180,
                                "minimum_confidence": "medium",
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
                watchlist_path=watchlist_path,
                run_dcf=True,
                dcf_assumptions_path=paths["dcf_assumptions"],
            )

            self.assertFalse(result["dcf_run"])
            self.assertIsNone(result["dcf_output_path"])
            self.assertIsNone(result["fair_value_per_share_output_path"])
            self.assertIsNone(result["model_rating_output_path"])
            self.assertTrue(any("high-priority research gap" in warning for warning in result["dcf_warnings"]))

    def test_dcf_output_file_created(self) -> None:
        with temp_analysis_workspace() as paths:
            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
                run_dcf=True,
                dcf_assumptions_path=paths["dcf_assumptions"],
            )

            output_path = Path(result["dcf_output_path"])
            output = json.loads(output_path.read_text(encoding="utf-8"))

            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.parent, paths["reports_dir"])
            self.assertTrue(output["calculated"])
            self.assertEqual(set(output["scenarios"]), {"bear", "base", "bull"})
            self.assertTrue(Path(result["fair_value_per_share_output_path"]).exists())
            self.assertTrue(Path(result["model_rating_output_path"]).exists())

    def test_fair_value_per_share_output_file_created(self) -> None:
        with temp_analysis_workspace() as paths:
            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
                run_dcf=True,
                dcf_assumptions_path=paths["dcf_assumptions"],
            )

            output_path = Path(result["fair_value_per_share_output_path"])
            output = json.loads(output_path.read_text(encoding="utf-8"))

            self.assertTrue(output_path.exists())
            self.assertTrue(output["calculated"])
            self.assertEqual({scenario["scenario"] for scenario in output["scenarios"]}, {"bear", "base", "bull"})
            self.assertEqual(output["scenarios"][0]["share_count_metric_id"], "nvda_diluted_weighted_average_shares_fy2025")

    def test_model_rating_output_file_created(self) -> None:
        with temp_analysis_workspace() as paths:
            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
                run_dcf=True,
                dcf_assumptions_path=paths["dcf_assumptions"],
            )

            output_path = Path(result["model_rating_output_path"])
            output = json.loads(output_path.read_text(encoding="utf-8"))

            self.assertTrue(output_path.exists())
            self.assertIn(output["model_rating"], {1, 2, 3, 4, 5})
            self.assertEqual(output["assumptions"]["market_price_metric_id"], "nvda_current_market_price_2026_05_23")

    def test_dcf_output_has_no_price_target_or_recommendation_language(self) -> None:
        with temp_analysis_workspace() as paths:
            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
                run_dcf=True,
                dcf_assumptions_path=paths["dcf_assumptions"],
            )

            serialized = Path(result["dcf_output_path"]).read_text(encoding="utf-8").lower()
            for term in ["price target", "buy", "sell", "hold", "recommendation", "investment advice"]:
                self.assertNotIn(term, serialized)

    def test_analysis_summary_has_no_recommendation_language(self) -> None:
        with temp_analysis_workspace() as paths:
            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
                generate_summary=True,
                run_dcf=True,
                dcf_assumptions_path=paths["dcf_assumptions"],
            )

            serialized = Path(result["analysis_summary_path"]).read_text(encoding="utf-8").lower()
            serialized = serialized.replace("not investment advice", "")
            for term in ["buy", "sell", "hold", "recommendation", "investment advice", "automated trading"]:
                self.assertNotIn(term, serialized)

    def test_analysis_summary_has_no_price_target_language(self) -> None:
        with temp_analysis_workspace() as paths:
            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
                generate_summary=True,
                run_dcf=True,
                dcf_assumptions_path=paths["dcf_assumptions"],
            )

            self.assertNotIn("price target", Path(result["analysis_summary_path"]).read_text(encoding="utf-8").lower())

    def test_generated_report_has_no_prohibited_valuation_language(self) -> None:
        with temp_analysis_workspace() as paths:
            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
                generate_fact_report=True,
            )

            report = Path(result["report_path"]).read_text(encoding="utf-8").lower()

            for term in ["valuation", "fair value", "intrinsic value", "price target", "buy", "sell", "hold", "recommendation", "investment advice"]:
                self.assertNotIn(term, report)

    def test_report_with_dcf_contains_dcf_section(self) -> None:
        with temp_analysis_workspace() as paths:
            result = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                audit_log_path=paths["audit_log"],
                reports_dir=paths["reports_dir"],
                generate_fact_report=True,
                run_dcf=True,
                dcf_assumptions_path=paths["dcf_assumptions"],
            )

            report = Path(result["report_path"]).read_text(encoding="utf-8")

            self.assertTrue(result["dcf_run"])
            self.assertIn("### DCF Calculation Output", report)
            self.assertIn("### Fair Value Per Share Model Calculation", report)
            self.assertIn("### Model Rating", report)
            self.assertIn("#### Assumptions Used", report)
            self.assertIn("#### DCF Warnings", report)
            self.assertIn("calculation output only, not investment advice", report)
            for term in ["price target", "buy", "sell", "hold", "recommendation"]:
                self.assertNotIn(term, report.lower())


class temp_analysis_workspace:
    def __enter__(self) -> dict[str, Path]:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        source_data = root / "nvda_sample_metrics.json"
        dcf_assumptions = root / "dcf_assumptions.json"
        shutil.copy(REPO_ROOT / "data" / "nvda_sample_metrics.json", source_data)
        shutil.copy(REPO_ROOT / "data" / "companies" / "NVDA" / "dcf_assumptions.json", dcf_assumptions)

        return {
            "root": root,
            "source_data": source_data,
            "dcf_assumptions": dcf_assumptions,
            "context_root": root / "companies",
            "markdown_queue": root / "research_queue.md",
            "json_queue": root / "research_queue.json",
            "audit_log": root / "audit_log.jsonl",
            "reports_dir": root / "reports",
        }

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()

