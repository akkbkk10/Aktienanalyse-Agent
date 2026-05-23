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
            )

            self.assertEqual(result["ticker"], "NVDA")
            self.assertTrue(result["validation_status"]["valid"])
            self.assertEqual(result["research_gaps_count"], 0)
            self.assertIn("net_margin", result["ratios_calculated"])
            self.assertTrue(result["audit_log_written"])
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
            )

            lines = paths["audit_log"].read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            record = json.loads(lines[0])
            self.assertEqual(record["ticker"], "NVDA")
            self.assertTrue(record["ratio_outputs"])


class temp_analysis_workspace:
    def __enter__(self) -> dict[str, Path]:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        source_data = root / "nvda_sample_metrics.json"
        shutil.copy(REPO_ROOT / "data" / "nvda_sample_metrics.json", source_data)

        return {
            "root": root,
            "source_data": source_data,
            "context_root": root / "companies",
            "markdown_queue": root / "research_queue.md",
            "json_queue": root / "research_queue.json",
            "audit_log": root / "audit_log.jsonl",
        }

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()

