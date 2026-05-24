from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_analysis.py"
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "nvda_expected_summary_structure.json"
spec = importlib.util.spec_from_file_location("run_analysis", SCRIPT_PATH)
run_analysis = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run_analysis)


class EndToEndAnalysisTests(unittest.TestCase):
    def test_full_nvda_workflow_generates_expected_artifacts(self) -> None:
        expected = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_data = root / "nvda_sample_metrics.json"
            context_root = root / "companies"
            reports_dir = root / "reports"
            audit_log_path = root / "audit_log.jsonl"
            shutil.copy(REPO_ROOT / "data" / "nvda_sample_metrics.json", source_data)

            summary = run_analysis.run_analysis(
                ticker="NVDA",
                source_data_path=source_data,
                context_root=context_root,
                markdown_queue_path=root / "research_queue.md",
                json_queue_path=root / "research_queue.json",
                audit_log_path=audit_log_path,
                reports_dir=reports_dir,
                generate_fact_report=True,
            )

            self.assertEqual(set(expected["required_keys"]), set(summary))
            self.assertEqual(summary["ticker"], expected["ticker"])
            self.assertTrue(summary["validation_status"]["valid"])
            self.assertEqual(set(expected["validation_status_required_keys"]), set(summary["validation_status"]))
            self.assertEqual(summary["research_gaps_count"], 0)
            self.assertTrue(summary["audit_log_written"])
            self.assertEqual(summary["warnings"], [])

            ratios_calculated = set(summary["ratios_calculated"])
            for ratio_name in expected["expected_ratio_names"]:
                self.assertIn(ratio_name, ratios_calculated)

            context_path = context_root / "NVDA" / "context.json"
            report_path = Path(summary["report_path"])
            self.assertTrue(context_path.exists())
            self.assertTrue(audit_log_path.exists())
            self.assertTrue(report_path.exists())
            self.assertEqual(report_path.parent, reports_dir)

            report_text = report_path.read_text(encoding="utf-8")
            self.assertIn("## Facts", report_text)
            self.assertIn("## Missing Data", report_text)
            self.assertIn("## Warnings", report_text)
            self.assertIn(str(audit_log_path), report_text)

            normalized_report = report_text.lower().replace("not investment advice", "")
            for term in expected["prohibited_terms"]:
                self.assertNotIn(term.lower(), normalized_report)

            audit_lines = audit_log_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(audit_lines), 1)
            audit_record = json.loads(audit_lines[0])
            self.assertEqual(audit_record["ticker"], "NVDA")
            self.assertTrue(audit_record["ratio_outputs"])


if __name__ == "__main__":
    unittest.main()

