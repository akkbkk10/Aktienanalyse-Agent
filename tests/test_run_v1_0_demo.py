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

    def test_demo_points_to_manual_review_checklist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_v1_0_demo.run_demo(reports_dir=Path(temp_dir) / "reports")

            checklist = Path(result["manual_review_checklist"])
            self.assertTrue(checklist.exists())
            self.assertEqual(checklist.name, "V1_0_TEST_PLAN.md")


if __name__ == "__main__":
    unittest.main()
