from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_v1_0_demo.py"
spec = importlib.util.spec_from_file_location("run_v1_0_demo", SCRIPT_PATH)
run_v1_0_demo = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run_v1_0_demo)

DCF_MODEL_PATH = REPO_ROOT / "scripts" / "dcf_model.py"
dcf_spec = importlib.util.spec_from_file_location("dcf_model", DCF_MODEL_PATH)
dcf_model = importlib.util.module_from_spec(dcf_spec)
assert dcf_spec.loader is not None
dcf_spec.loader.exec_module(dcf_model)

FAIR_VALUE_PATH = REPO_ROOT / "scripts" / "fair_value_per_share.py"
fair_value_spec = importlib.util.spec_from_file_location("fair_value_per_share", FAIR_VALUE_PATH)
fair_value_per_share = importlib.util.module_from_spec(fair_value_spec)
assert fair_value_spec.loader is not None
fair_value_spec.loader.exec_module(fair_value_per_share)

MODEL_RATING_PATH = REPO_ROOT / "scripts" / "model_rating.py"
model_rating_spec = importlib.util.spec_from_file_location("model_rating", MODEL_RATING_PATH)
model_rating = importlib.util.module_from_spec(model_rating_spec)
assert model_rating_spec.loader is not None
model_rating_spec.loader.exec_module(model_rating)

MODEL_CONFIDENCE_PATH = REPO_ROOT / "scripts" / "model_confidence.py"
model_confidence_spec = importlib.util.spec_from_file_location("model_confidence", MODEL_CONFIDENCE_PATH)
model_confidence = importlib.util.module_from_spec(model_confidence_spec)
assert model_confidence_spec.loader is not None
model_confidence_spec.loader.exec_module(model_confidence)

MODEL_SIGNAL_PATH = REPO_ROOT / "scripts" / "model_signal.py"
model_signal_spec = importlib.util.spec_from_file_location("model_signal", MODEL_SIGNAL_PATH)
model_signal = importlib.util.module_from_spec(model_signal_spec)
assert model_signal_spec.loader is not None
model_signal_spec.loader.exec_module(model_signal)

ANALYSIS_SUMMARY_PATH = REPO_ROOT / "scripts" / "generate_analysis_summary.py"
analysis_summary_spec = importlib.util.spec_from_file_location("generate_analysis_summary", ANALYSIS_SUMMARY_PATH)
analysis_summary = importlib.util.module_from_spec(analysis_summary_spec)
assert analysis_summary_spec.loader is not None
analysis_summary_spec.loader.exec_module(analysis_summary)


class RunV10DemoTests(unittest.TestCase):
    def test_demo_runs_supported_sample_tickers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_v1_0_demo.run_demo(reports_dir=Path(temp_dir) / "reports")

            self.assertTrue(result["demo_completed"])
            self.assertEqual(result["tickers"], ["NVDA", "AMD", "TSMC"])
            self.assertEqual(result["batch_summary"]["successful_runs"], ["NVDA", "AMD", "TSMC"])
            self.assertEqual(result["batch_summary"]["failed_runs"], {})

    def test_demo_generates_required_artifacts_per_ticker(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            reports_dir = Path(temp_dir) / "reports"
            result = run_v1_0_demo.run_demo(reports_dir=reports_dir)

            output_paths = result["generated_file_paths"]["output_paths_by_ticker"]
            for ticker in ["NVDA", "AMD", "TSMC"]:
                for key in run_v1_0_demo.REQUIRED_ARTIFACT_KEYS:
                    path = Path(output_paths[ticker][key])
                    self.assertTrue(path.exists(), f"{ticker} {key}")
                    self.assertTrue(path.is_relative_to(reports_dir), f"{ticker} {key}")

    def test_demo_writes_expected_artifacts_to_custom_reports_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            reports_dir = Path(temp_dir) / "custom_reports"
            result = run_v1_0_demo.run_demo(reports_dir=reports_dir)

            audit_log_path = Path(result["generated_file_paths"]["audit_log_path"])
            self.assertTrue(audit_log_path.exists())
            self.assertEqual(audit_log_path, reports_dir / "audit_log.jsonl")

            expected_keys = {
                "report_path",
                "analysis_summary_path",
                "dcf_output_path",
                "fair_value_per_share_output_path",
                "model_rating_output_path",
                "model_confidence_output_path",
                "model_signal_output_path",
            }
            output_paths = result["generated_file_paths"]["output_paths_by_ticker"]
            for ticker in ["NVDA", "AMD", "TSMC"]:
                ticker_dir = reports_dir / ticker
                self.assertTrue(ticker_dir.is_dir(), ticker)
                for key in expected_keys:
                    path = Path(output_paths[ticker][key])
                    self.assertTrue(path.exists(), f"{ticker} {key}")
                    self.assertTrue(path.is_relative_to(ticker_dir), f"{ticker} {key}")

    def test_demo_outputs_expected_calculation_layers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_v1_0_demo.run_demo(reports_dir=Path(temp_dir) / "reports")
            output_paths = result["generated_file_paths"]["output_paths_by_ticker"]

            for ticker in ["NVDA", "AMD", "TSMC"]:
                dcf_output = json.loads(Path(output_paths[ticker]["dcf_output_path"]).read_text(encoding="utf-8"))
                fair_value = json.loads(
                    Path(output_paths[ticker]["fair_value_per_share_output_path"]).read_text(encoding="utf-8")
                )
                model_rating = json.loads(Path(output_paths[ticker]["model_rating_output_path"]).read_text(encoding="utf-8"))
                model_confidence = json.loads(
                    Path(output_paths[ticker]["model_confidence_output_path"]).read_text(encoding="utf-8")
                )
                model_signal = json.loads(Path(output_paths[ticker]["model_signal_output_path"]).read_text(encoding="utf-8"))

                self.assertEqual(set(dcf_output["scenarios"]), {"bear", "base", "bull"})
                self.assertTrue(fair_value["calculated"])
                self.assertIn(model_rating["model_rating"], [1, 2, 3, 4, 5])
                self.assertIn(model_confidence["model_confidence"], ["A", "B", "C", "D"])
                self.assertNotEqual(model_confidence["model_confidence"], "A")
                self.assertEqual(model_confidence["assumption_quality"]["status"], "manual_review_required")
                self.assertTrue(model_confidence["warnings"])
                self.assertEqual(model_signal["model_signal"], "unavailable")
                self.assertTrue(model_signal["blocking_reasons"])

    def test_demo_dcf_outputs_satisfy_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_v1_0_demo.run_demo(reports_dir=Path(temp_dir) / "reports")
            output_paths = result["generated_file_paths"]["output_paths_by_ticker"]

            for ticker in ["NVDA", "AMD", "TSMC"]:
                with self.subTest(ticker=ticker):
                    dcf_output = json.loads(Path(output_paths[ticker]["dcf_output_path"]).read_text(encoding="utf-8"))

                    self.assertEqual(dcf_model.validate_dcf_output(dcf_output), [])

    def test_demo_fair_value_outputs_satisfy_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_v1_0_demo.run_demo(reports_dir=Path(temp_dir) / "reports")
            output_paths = result["generated_file_paths"]["output_paths_by_ticker"]

            for ticker in ["NVDA", "AMD", "TSMC"]:
                with self.subTest(ticker=ticker):
                    fair_value_output = json.loads(
                        Path(output_paths[ticker]["fair_value_per_share_output_path"]).read_text(encoding="utf-8")
                    )

                    self.assertEqual(fair_value_per_share.validate_fair_value_per_share_output(fair_value_output), [])

    def test_demo_model_rating_outputs_satisfy_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_v1_0_demo.run_demo(reports_dir=Path(temp_dir) / "reports")
            output_paths = result["generated_file_paths"]["output_paths_by_ticker"]

            for ticker in ["NVDA", "AMD", "TSMC"]:
                with self.subTest(ticker=ticker):
                    rating_output = json.loads(
                        Path(output_paths[ticker]["model_rating_output_path"]).read_text(encoding="utf-8")
                    )

                    self.assertEqual(model_rating.validate_model_rating_output(rating_output), [])

    def test_demo_model_confidence_outputs_satisfy_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_v1_0_demo.run_demo(reports_dir=Path(temp_dir) / "reports")
            output_paths = result["generated_file_paths"]["output_paths_by_ticker"]

            for ticker in ["NVDA", "AMD", "TSMC"]:
                with self.subTest(ticker=ticker):
                    confidence_output = json.loads(
                        Path(output_paths[ticker]["model_confidence_output_path"]).read_text(encoding="utf-8")
                    )

                    self.assertEqual(model_confidence.validate_model_confidence_output(confidence_output), [])

    def test_demo_model_signal_outputs_satisfy_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_v1_0_demo.run_demo(reports_dir=Path(temp_dir) / "reports")
            output_paths = result["generated_file_paths"]["output_paths_by_ticker"]

            for ticker in ["NVDA", "AMD", "TSMC"]:
                with self.subTest(ticker=ticker):
                    signal_output = json.loads(
                        Path(output_paths[ticker]["model_signal_output_path"]).read_text(encoding="utf-8")
                    )

                    self.assertEqual(model_signal.validate_model_signal_output(signal_output), [])

    def test_demo_analysis_summary_outputs_satisfy_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_v1_0_demo.run_demo(reports_dir=Path(temp_dir) / "reports")
            output_paths = result["generated_file_paths"]["output_paths_by_ticker"]

            for ticker in ["NVDA", "AMD", "TSMC"]:
                with self.subTest(ticker=ticker):
                    summary_output = json.loads(
                        Path(output_paths[ticker]["analysis_summary_path"]).read_text(encoding="utf-8")
                    )

                    self.assertEqual(analysis_summary.validate_analysis_summary_output(summary_output), [])

    def test_demo_preserves_source_reference_evidence_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_v1_0_demo.run_demo(reports_dir=Path(temp_dir) / "reports")
            output_paths = result["generated_file_paths"]["output_paths_by_ticker"]

            for ticker in ["NVDA", "AMD", "TSMC"]:
                with self.subTest(ticker=ticker):
                    dcf_output = json.loads(Path(output_paths[ticker]["dcf_output_path"]).read_text(encoding="utf-8"))
                    fair_value_output = json.loads(
                        Path(output_paths[ticker]["fair_value_per_share_output_path"]).read_text(encoding="utf-8")
                    )
                    model_rating_output = json.loads(
                        Path(output_paths[ticker]["model_rating_output_path"]).read_text(encoding="utf-8")
                    )
                    model_confidence_output = json.loads(
                        Path(output_paths[ticker]["model_confidence_output_path"]).read_text(encoding="utf-8")
                    )
                    summary_output = json.loads(Path(output_paths[ticker]["analysis_summary_path"]).read_text(encoding="utf-8"))

                    _assert_source_references_include_fields(
                        self,
                        dcf_output["source_references"],
                        {"metric_id", "metric_name", "period", "source_url", "source_date", "confidence"},
                    )
                    _assert_source_references_include_fields(
                        self,
                        fair_value_output["source_references"],
                        {
                            "metric_id",
                            "metric_name",
                            "period",
                            "unit",
                            "source_url",
                            "source_type",
                            "source_date",
                            "last_verified",
                            "confidence",
                        },
                    )
                    _assert_source_references_include_fields(
                        self,
                        fair_value_output["scenarios"][0]["source_references"],
                        {
                            "metric_id",
                            "metric_name",
                            "period",
                            "unit",
                            "source_url",
                            "source_type",
                            "source_date",
                            "last_verified",
                            "confidence",
                        },
                    )
                    _assert_source_references_include_fields(
                        self,
                        model_rating_output["source_references"],
                        {
                            "metric_id",
                            "metric_name",
                            "period",
                            "unit",
                            "currency",
                            "as_of_datetime",
                            "fetched_at",
                            "provider",
                            "retrieval_method",
                            "source_url",
                            "source_type",
                            "source_date",
                            "last_verified",
                            "confidence",
                        },
                    )
                    _assert_source_references_include_fields(
                        self,
                        model_confidence_output["source_references"],
                        {
                            "metric_id",
                            "metric_name",
                            "period",
                            "unit",
                            "source_url",
                            "source_type",
                            "source_date",
                            "last_verified",
                            "confidence",
                        },
                    )

                    facts = summary_output["facts"]
                    summary_reference_fields = {
                        "ratio_source_references": {
                            "metric_id",
                            "metric_name",
                            "period",
                            "source_url",
                            "source_type",
                            "source_date",
                            "last_verified",
                            "confidence",
                        },
                        "dcf_source_references": {
                            "metric_id",
                            "metric_name",
                            "period",
                            "source_url",
                            "source_date",
                            "confidence",
                        },
                        "fair_value_per_share_source_references": {
                            "metric_id",
                            "metric_name",
                            "period",
                            "unit",
                            "source_url",
                            "source_type",
                            "source_date",
                            "last_verified",
                            "confidence",
                        },
                        "model_rating_source_references": {
                            "metric_id",
                            "metric_name",
                            "period",
                            "unit",
                            "currency",
                            "as_of_datetime",
                            "fetched_at",
                            "provider",
                            "retrieval_method",
                            "source_url",
                            "source_type",
                            "source_date",
                            "last_verified",
                            "confidence",
                        },
                        "model_confidence_source_references": {
                            "metric_id",
                            "metric_name",
                            "period",
                            "unit",
                            "source_url",
                            "source_type",
                            "source_date",
                            "last_verified",
                            "confidence",
                        },
                    }
                    for section, required_fields in summary_reference_fields.items():
                        _assert_source_references_include_fields(self, facts[section], required_fields)

    def test_demo_points_to_manual_review_checklist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_v1_0_demo.run_demo(reports_dir=Path(temp_dir) / "reports")

            checklist = Path(result["manual_review_checklist"])
            self.assertTrue(checklist.exists())
            self.assertEqual(checklist.name, "V1_0_TEST_PLAN.md")


def _assert_source_references_include_fields(
    test_case: unittest.TestCase,
    source_references: list[dict],
    required_fields: set[str],
) -> None:
    test_case.assertTrue(source_references)
    for source_reference in source_references:
        for field in required_fields:
            test_case.assertIn(field, source_reference)
            test_case.assertNotIn(source_reference[field], (None, ""))


if __name__ == "__main__":
    unittest.main()
