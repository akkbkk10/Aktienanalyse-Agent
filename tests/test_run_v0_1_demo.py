from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_v0_1_demo.py"
spec = importlib.util.spec_from_file_location("run_v0_1_demo", SCRIPT_PATH)
run_v0_1_demo = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run_v0_1_demo)


class RunV01DemoTests(unittest.TestCase):
    def test_demo_script_runs_full_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_v0_1_demo.run_demo(reports_dir=Path(temp_dir) / "reports")

            self.assertTrue(result["demo_completed"])
            summary = result["orchestrator_summary"]
            self.assertTrue(summary["validation_status"]["valid"])
            self.assertTrue(summary["dcf_run"])
            self.assertTrue(summary["audit_log_written"])

    def test_demo_outputs_generated_file_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            reports_dir = Path(temp_dir) / "reports"
            result = run_v0_1_demo.run_demo(reports_dir=reports_dir)
            generated_paths = result["generated_file_paths"]

            for key in [
                "context_path",
                "audit_log_path",
                "readiness_audit_log_path",
                "dcf_output_path",
                "fact_report_path",
                "analysis_summary_path",
            ]:
                self.assertIsNotNone(generated_paths[key])
                self.assertTrue(Path(generated_paths[key]).exists(), key)
                self.assertTrue(Path(generated_paths[key]).is_relative_to(reports_dir))

    def test_demo_summary_contains_expected_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_v0_1_demo.run_demo(reports_dir=Path(temp_dir) / "reports")

            analysis_summary = json.loads(
                Path(result["generated_file_paths"]["analysis_summary_path"]).read_text(encoding="utf-8")
            )
            dcf_output = json.loads(Path(result["generated_file_paths"]["dcf_output_path"]).read_text(encoding="utf-8"))

            self.assertIn("facts", analysis_summary)
            self.assertIn("assumptions", analysis_summary)
            self.assertIn("calculated_outputs", analysis_summary)
            self.assertEqual(set(dcf_output["scenarios"]), {"bear", "base", "bull"})

    def test_demo_outputs_no_prohibited_language(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_v0_1_demo.run_demo(reports_dir=Path(temp_dir) / "reports")
            generated_paths = result["generated_file_paths"]
            combined = "\n".join(
                Path(path).read_text(encoding="utf-8").lower()
                for path in [
                    generated_paths["dcf_output_path"],
                    generated_paths["fact_report_path"],
                    generated_paths["analysis_summary_path"],
                ]
            ).replace("not investment advice", "")

            for term in ["price target", "buy", "sell", "hold", "recommendation", "investment advice", "automated trading"]:
                self.assertNotIn(term, combined)


if __name__ == "__main__":
    unittest.main()
