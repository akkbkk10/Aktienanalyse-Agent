from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    script_path = REPO_ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


build_company_context = load_script("build_company_context")
check_valuation_readiness = load_script("check_valuation_readiness")


class ValuationReadinessTests(unittest.TestCase):
    def test_ready_case(self) -> None:
        with readiness_workspace() as paths:
            result = check_valuation_readiness.check_readiness(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                audit_log_path=paths["audit_log"],
            )

            self.assertTrue(result["ready_for_valuation"])
            self.assertEqual(result["blocking_reasons"], [])
            self.assertEqual(result["required_next_actions"], [])
            self.assertTrue(paths["audit_log"].exists())

    def test_missing_ratios_block_readiness(self) -> None:
        with readiness_workspace() as paths:
            result = check_valuation_readiness.check_readiness(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                audit_log_path=paths["audit_log"],
                ratio_result={"ticker": "NVDA", "ratios": [{"ratio_name": "net_margin"}]},
            )

            self.assertFalse(result["ready_for_valuation"])
            self.assertTrue(any("Missing required ratios" in reason for reason in result["blocking_reasons"]))

    def test_stale_data_blocks_readiness(self) -> None:
        with readiness_workspace() as paths:
            stale_source = paths["root"] / "stale_metrics.json"
            records = json.loads(paths["source_data"].read_text(encoding="utf-8"))
            records[0]["last_verified"] = "2025-01-01"
            stale_source.write_text(json.dumps(records), encoding="utf-8")

            result = check_valuation_readiness.check_readiness(
                ticker="NVDA",
                source_data_path=stale_source,
                context_root=paths["context_root"],
                audit_log_path=paths["audit_log"],
            )

            self.assertFalse(result["ready_for_valuation"])
            self.assertIn("Source validation failed.", result["blocking_reasons"])

    def test_high_priority_research_gap_blocks_readiness(self) -> None:
        with readiness_workspace() as paths:
            result = check_valuation_readiness.check_readiness(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                audit_log_path=paths["audit_log"],
                research_gaps=[
                    {
                        "ticker": "NVDA",
                        "gap_type": "low_confidence",
                        "metric_name": "Revenue",
                        "priority": "high",
                        "message": "Manual escalation.",
                    }
                ],
            )

            self.assertFalse(result["ready_for_valuation"])
            self.assertTrue(any("high-priority research gap" in reason for reason in result["blocking_reasons"]))

    def test_invalid_methodology_blocks_readiness(self) -> None:
        with readiness_workspace() as paths:
            invalid_methodology = paths["root"] / "bad_methodology.json"
            methodology = json.loads((REPO_ROOT / "config" / "methodology_buffett_ai.json").read_text(encoding="utf-8"))
            del methodology["methodology_version"]
            invalid_methodology.write_text(json.dumps(methodology), encoding="utf-8")

            result = check_valuation_readiness.check_readiness(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                methodology_path=invalid_methodology,
                audit_log_path=paths["audit_log"],
            )

            self.assertFalse(result["ready_for_valuation"])
            self.assertIn("Methodology config is invalid.", result["blocking_reasons"])

    def test_prohibited_valuation_language_blocks_readiness(self) -> None:
        with readiness_workspace() as paths:
            report_path = paths["root"] / "bad_report.md"
            report_path.write_text("This draft contains a price target.", encoding="utf-8")

            result = check_valuation_readiness.check_readiness(
                ticker="NVDA",
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                audit_log_path=paths["audit_log"],
                report_path=report_path,
            )

            self.assertFalse(result["ready_for_valuation"])
            self.assertTrue(any("Prohibited valuation-stage output" in reason for reason in result["blocking_reasons"]))


class readiness_workspace:
    def __enter__(self) -> dict[str, Path]:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        source_data = root / "nvda_sample_metrics.json"
        context_root = root / "companies"
        shutil.copy(REPO_ROOT / "data" / "nvda_sample_metrics.json", source_data)
        build_company_context.build_company_context(source_data, output_root=context_root)

        return {
            "root": root,
            "source_data": source_data,
            "context_root": context_root,
            "audit_log": root / "readiness_audit.jsonl",
        }

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
