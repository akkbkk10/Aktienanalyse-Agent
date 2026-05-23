from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_analysis.py"
spec = importlib.util.spec_from_file_location("run_analysis", SCRIPT_PATH)
run_analysis = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run_analysis)


class WorkflowOrderTests(unittest.TestCase):
    def test_validation_runs_before_research_gaps(self) -> None:
        order = run_with_order_tracking(generate_fact_report=False, generate_summary=False, run_dcf=False)

        self.assertLess(order.index("validation"), order.index("research_gaps"))

    def test_research_gaps_run_before_ratios(self) -> None:
        order = run_with_order_tracking(generate_fact_report=False, generate_summary=False, run_dcf=False)

        self.assertLess(order.index("research_gaps"), order.index("ratios"))

    def test_readiness_runs_before_dcf(self) -> None:
        order = run_with_order_tracking(generate_fact_report=False, generate_summary=False, run_dcf=True)

        self.assertLess(order.index("readiness"), order.index("dcf"))

    def test_dcf_runs_before_report_when_enabled(self) -> None:
        order = run_with_order_tracking(generate_fact_report=True, generate_summary=False, run_dcf=True)

        self.assertLess(order.index("dcf"), order.index("report"))

    def test_audit_log_written_after_workflow_artifacts(self) -> None:
        order = run_with_order_tracking(generate_fact_report=True, generate_summary=True, run_dcf=True)

        self.assertLess(order.index("dcf_output"), order.index("audit"))
        self.assertLess(order.index("report"), order.index("audit"))
        self.assertLess(order.index("summary"), order.index("audit"))


def run_with_order_tracking(
    generate_fact_report: bool,
    generate_summary: bool,
    run_dcf: bool,
) -> list[str]:
    order: list[str] = []
    originals = {
        "validate_file": run_analysis.validate_sources.validate_file,
        "build_company_context": run_analysis.build_company_context.build_company_context,
        "detect_and_queue_gaps": run_analysis.detect_research_gaps.detect_and_queue_gaps,
        "calculate_ratios_for_ticker": run_analysis.calculate_ratios.calculate_ratios_for_ticker,
        "check_readiness": run_analysis.check_valuation_readiness.check_readiness,
        "run_dcf": run_analysis.dcf_model.run_dcf,
        "write_dcf_output": run_analysis._write_dcf_output,
        "generate_report": run_analysis.generate_report.generate_report,
        "generate_analysis_summary": run_analysis.generate_analysis_summary.generate_analysis_summary,
        "build_audit_record": run_analysis.write_audit_log.build_audit_record,
        "append_audit_record": run_analysis.write_audit_log.append_audit_record,
    }

    def validate_file(_source_data_path: Path):
        order.append("validation")
        return []

    def build_company_context(_source_data_path: Path, output_root: Path):
        order.append("context")
        context_path = output_root / "TEST" / "context.json"
        context_path.parent.mkdir(parents=True, exist_ok=True)
        context_path.write_text("{}", encoding="utf-8")
        return {"ticker": "TEST"}

    def detect_and_queue_gaps(**_kwargs):
        order.append("research_gaps")
        return {"gaps": [], "queue": {"gap_count": 0, "items": []}}

    def calculate_ratios_for_ticker(**_kwargs):
        order.append("ratios")
        return {"ticker": "TEST", "ratios": [{"ratio_name": "net_margin"}], "missing_inputs": [], "skipped": []}

    def check_readiness(**_kwargs):
        order.append("readiness")
        return {"ticker": "TEST", "ready_for_valuation": True, "blocking_reasons": [], "warnings": []}

    def dcf(**_kwargs):
        order.append("dcf")
        return {"ticker": "TEST", "calculated": True, "scenarios": {"base": {}}, "warnings": []}

    def write_dcf_output(_ticker: str, _dcf_result: dict, reports_dir: Path):
        order.append("dcf_output")
        output_path = reports_dir / "TEST_dcf_output.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("{}", encoding="utf-8")
        return output_path

    def report(**kwargs):
        order.append("report")
        reports_dir = kwargs["reports_dir"]
        report_path = reports_dir / "TEST_fact_report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("# TEST", encoding="utf-8")
        return report_path

    def summary(**kwargs):
        order.append("summary")
        reports_dir = kwargs["reports_dir"]
        summary_path = reports_dir / "TEST_analysis_summary.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text("{}", encoding="utf-8")
        return summary_path

    def build_audit_record(**_kwargs):
        order.append("audit_record")
        return {
            "timestamp": "2026-05-23T00:00:00Z",
            "ticker": "TEST",
            "methodology_version": "0.1.0",
            "data_context_path": "context.json",
            "source_files_used": [],
            "validation_status": {"valid": True, "errors": []},
            "ratio_outputs": [],
            "research_gaps_detected": [],
            "git_commit_hash": None,
        }

    def append_audit_record(_record: dict, audit_log_path: Path):
        order.append("audit")
        audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        audit_log_path.write_text("{}", encoding="utf-8")
        return _record

    run_analysis.validate_sources.validate_file = validate_file
    run_analysis.build_company_context.build_company_context = build_company_context
    run_analysis.detect_research_gaps.detect_and_queue_gaps = detect_and_queue_gaps
    run_analysis.calculate_ratios.calculate_ratios_for_ticker = calculate_ratios_for_ticker
    run_analysis.check_valuation_readiness.check_readiness = check_readiness
    run_analysis.dcf_model.run_dcf = dcf
    run_analysis._write_dcf_output = write_dcf_output
    run_analysis.generate_report.generate_report = report
    run_analysis.generate_analysis_summary.generate_analysis_summary = summary
    run_analysis.write_audit_log.build_audit_record = build_audit_record
    run_analysis.write_audit_log.append_audit_record = append_audit_record

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_analysis.run_analysis(
                ticker="TEST",
                source_data_path=root / "source.json",
                context_root=root / "companies",
                markdown_queue_path=root / "research_queue.md",
                json_queue_path=root / "research_queue.json",
                audit_log_path=root / "audit_log.jsonl",
                reports_dir=root / "reports",
                generate_fact_report=generate_fact_report,
                generate_summary=generate_summary,
                run_dcf=run_dcf,
            )
    finally:
        run_analysis.validate_sources.validate_file = originals["validate_file"]
        run_analysis.build_company_context.build_company_context = originals["build_company_context"]
        run_analysis.detect_research_gaps.detect_and_queue_gaps = originals["detect_and_queue_gaps"]
        run_analysis.calculate_ratios.calculate_ratios_for_ticker = originals["calculate_ratios_for_ticker"]
        run_analysis.check_valuation_readiness.check_readiness = originals["check_readiness"]
        run_analysis.dcf_model.run_dcf = originals["run_dcf"]
        run_analysis._write_dcf_output = originals["write_dcf_output"]
        run_analysis.generate_report.generate_report = originals["generate_report"]
        run_analysis.generate_analysis_summary.generate_analysis_summary = originals["generate_analysis_summary"]
        run_analysis.write_audit_log.build_audit_record = originals["build_audit_record"]
        run_analysis.write_audit_log.append_audit_record = originals["append_audit_record"]

    return order


if __name__ == "__main__":
    unittest.main()
