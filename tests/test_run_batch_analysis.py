from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_batch_analysis.py"
spec = importlib.util.spec_from_file_location("run_batch_analysis", SCRIPT_PATH)
run_batch_analysis = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run_batch_analysis)


class RunBatchAnalysisTests(unittest.TestCase):
    def test_single_ticker_batch(self) -> None:
        with batch_workspace() as paths:
            result = run_batch_analysis.run_batch(
                tickers=["NVDA"],
                context_root=paths["context_root"],
                reports_dir=paths["reports_dir"],
                audit_log_path=paths["audit_log"],
                generate_fact_report=True,
                generate_summary=True,
                run_dcf=True,
            )

            self.assertEqual(result["tickers_processed"], ["NVDA"])
            self.assertEqual(result["successful_runs"], ["NVDA"])
            self.assertEqual(result["failed_runs"], {})
            self.assertTrue(Path(result["output_paths_by_ticker"]["NVDA"]["report_path"]).exists())
            self.assertTrue(Path(result["output_paths_by_ticker"]["NVDA"]["analysis_summary_path"]).exists())
            self.assertTrue(Path(result["output_paths_by_ticker"]["NVDA"]["dcf_output_path"]).exists())
            self.assertTrue(Path(result["output_paths_by_ticker"]["NVDA"]["fair_value_per_share_output_path"]).exists())
            self.assertTrue(Path(result["output_paths_by_ticker"]["NVDA"]["model_rating_output_path"]).exists())
            self.assertTrue(Path(result["output_paths_by_ticker"]["NVDA"]["model_confidence_output_path"]).exists())

    def test_multiple_tickers_with_missing_data(self) -> None:
        with batch_workspace() as paths:
            result = run_batch_analysis.run_batch(
                tickers=["NVDA", "MSFT"],
                context_root=paths["context_root"],
                reports_dir=paths["reports_dir"],
                audit_log_path=paths["audit_log"],
                generate_summary=True,
            )

            self.assertEqual(result["tickers_processed"], ["NVDA", "MSFT"])
            self.assertIn("NVDA", result["successful_runs"])
            self.assertIn("MSFT", result["failed_runs"])
            self.assertIn("MSFT", result["warnings_by_ticker"])

    def test_nvda_and_amd_successful_batch_runs(self) -> None:
        with batch_workspace() as paths:
            result = run_batch_analysis.run_batch(
                tickers=["NVDA", "AMD"],
                context_root=paths["context_root"],
                reports_dir=paths["reports_dir"],
                audit_log_path=paths["audit_log"],
                generate_fact_report=True,
                generate_summary=True,
                run_dcf=True,
            )

            self.assertEqual(result["tickers_processed"], ["NVDA", "AMD"])
            self.assertEqual(result["successful_runs"], ["NVDA", "AMD"])
            self.assertEqual(result["failed_runs"], {})
            for ticker in ["NVDA", "AMD"]:
                self.assertTrue(Path(result["output_paths_by_ticker"][ticker]["report_path"]).exists())
                self.assertTrue(Path(result["output_paths_by_ticker"][ticker]["analysis_summary_path"]).exists())
                self.assertTrue(Path(result["output_paths_by_ticker"][ticker]["dcf_output_path"]).exists())
                self.assertTrue(Path(result["output_paths_by_ticker"][ticker]["fair_value_per_share_output_path"]).exists())
                self.assertTrue(Path(result["output_paths_by_ticker"][ticker]["model_rating_output_path"]).exists())
                self.assertTrue(Path(result["output_paths_by_ticker"][ticker]["model_confidence_output_path"]).exists())

    def test_partial_failure_handling(self) -> None:
        with batch_workspace() as paths:
            result = run_batch_analysis.run_batch(
                tickers=["MISSING", "NVDA"],
                context_root=paths["context_root"],
                reports_dir=paths["reports_dir"],
                audit_log_path=paths["audit_log"],
                generate_fact_report=False,
            )

            self.assertEqual(result["successful_runs"], ["NVDA"])
            self.assertIn("MISSING", result["failed_runs"])
            self.assertEqual(result["output_paths_by_ticker"]["MISSING"], {})

    def test_output_structure(self) -> None:
        with batch_workspace() as paths:
            result = run_batch_analysis.run_batch(
                tickers=["NVDA"],
                context_root=paths["context_root"],
                reports_dir=paths["reports_dir"],
                audit_log_path=paths["audit_log"],
            )

            self.assertEqual(
                set(result),
                {
                    "tickers_processed",
                    "successful_runs",
                    "failed_runs",
                    "output_paths_by_ticker",
                    "warnings_by_ticker",
                },
            )
            self.assertEqual(
                set(result["output_paths_by_ticker"]["NVDA"]),
                {
                    "report_path",
                    "analysis_summary_path",
                    "dcf_output_path",
                    "fair_value_per_share_output_path",
                    "model_rating_output_path",
                    "model_rating_status",
                    "model_confidence_output_path",
                    "audit_log_path",
                },
            )


class batch_workspace:
    def __enter__(self) -> dict[str, Path]:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        return {
            "root": root,
            "context_root": root / "companies",
            "reports_dir": root / "reports",
            "audit_log": root / "audit_log.jsonl",
        }

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
