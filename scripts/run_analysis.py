from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_company_context
import calculate_ratios
import check_valuation_readiness
import detect_research_gaps
import dcf_model
import generate_report
import validate_methodology
import validate_sources
import write_audit_log


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTEXT_ROOT = REPO_ROOT / "data" / "companies"
DEFAULT_MARKDOWN_QUEUE_PATH = REPO_ROOT / "research_queue.md"
DEFAULT_JSON_QUEUE_PATH = REPO_ROOT / "research_queue.json"
DEFAULT_AUDIT_LOG_PATH = REPO_ROOT / "audit_log.jsonl"
DEFAULT_REPORTS_DIR = REPO_ROOT / "reports"
DEFAULT_DCF_ASSUMPTIONS_PATH_TEMPLATE = REPO_ROOT / "data" / "companies" / "{ticker}" / "dcf_assumptions.json"


def run_analysis(
    ticker: str,
    source_data_path: Path,
    context_root: Path = DEFAULT_CONTEXT_ROOT,
    markdown_queue_path: Path = DEFAULT_MARKDOWN_QUEUE_PATH,
    json_queue_path: Path = DEFAULT_JSON_QUEUE_PATH,
    audit_log_path: Path = DEFAULT_AUDIT_LOG_PATH,
    reports_dir: Path = DEFAULT_REPORTS_DIR,
    methodology_path: Path = validate_methodology.DEFAULT_METHODOLOGY_PATH,
    watchlist_path: Path = detect_research_gaps.DEFAULT_WATCHLIST_PATH,
    rebuild_context: bool = True,
    generate_fact_report: bool = False,
    run_dcf: bool = False,
    dcf_assumptions_path: Path | None = None,
) -> dict[str, Any]:
    normalized_ticker = ticker.upper()
    warnings: list[str] = []
    validation_errors = validate_sources.validate_file(source_data_path)
    validation_status = {"valid": not validation_errors, "errors": [error.to_dict() for error in validation_errors]}
    context_path = context_root / normalized_ticker / "context.json"

    if not validation_status["valid"]:
        warnings.append("Source validation failed; context, ratios, and audit log were not updated.")
        return _summary(
            ticker=normalized_ticker,
            validation_status=validation_status,
            research_gaps_count=0,
            ratios_calculated=[],
            audit_log_written=False,
            report_path=None,
            dcf_run=False,
            dcf_scenarios_calculated=[],
            dcf_output_path=None,
            dcf_warnings=[],
            warnings=warnings,
        )

    if rebuild_context:
        build_company_context.build_company_context(source_data_path, output_root=context_root)
    elif not context_path.exists():
        warnings.append(f"Company context missing at {context_path}.")
        return _summary(
            ticker=normalized_ticker,
            validation_status=validation_status,
            research_gaps_count=0,
            ratios_calculated=[],
            audit_log_written=False,
            report_path=None,
            dcf_run=False,
            dcf_scenarios_calculated=[],
            dcf_output_path=None,
            dcf_warnings=[],
            warnings=warnings,
        )

    gap_result = detect_research_gaps.detect_and_queue_gaps(
        watchlist_path=watchlist_path,
        context_root=context_root,
        markdown_queue_path=markdown_queue_path,
        json_queue_path=json_queue_path,
    )
    ratio_result = calculate_ratios.calculate_ratios_for_ticker(
        ticker=normalized_ticker,
        context_root=context_root,
        markdown_queue_path=markdown_queue_path,
        json_queue_path=json_queue_path,
        queue_missing=True,
    )

    report_path = None
    dcf_output_path = None
    dcf_result = None
    dcf_warnings: list[str] = []
    dcf_scenarios_calculated: list[str] = []

    if run_dcf:
        readiness_result = check_valuation_readiness.check_readiness(
            ticker=normalized_ticker,
            source_data_path=source_data_path,
            context_root=context_root,
            methodology_path=methodology_path,
            watchlist_path=watchlist_path,
            audit_log_path=reports_dir / f"{normalized_ticker}_valuation_readiness_audit_probe.jsonl",
            validation_status=validation_status,
            ratio_result=ratio_result,
            research_gaps=gap_result["gaps"],
        )
        if readiness_result["ready_for_valuation"]:
            assumptions_path = dcf_assumptions_path or Path(
                str(DEFAULT_DCF_ASSUMPTIONS_PATH_TEMPLATE).format(ticker=normalized_ticker)
            )
            dcf_result = dcf_model.run_dcf(
                ticker=normalized_ticker,
                assumptions_path=assumptions_path,
                source_data_path=source_data_path,
                context_root=context_root,
                readiness_result=readiness_result,
            )
            if dcf_result.get("calculated"):
                dcf_output_path = str(_write_dcf_output(normalized_ticker, dcf_result, reports_dir))
                dcf_scenarios_calculated = sorted(dcf_result.get("scenarios", {}).keys())
                dcf_warnings = dcf_result.get("warnings", [])
            else:
                dcf_warnings = dcf_result.get("blocking_reasons", [])
        else:
            warnings.append("Valuation readiness gate blocked DCF run.")
            dcf_warnings = readiness_result["blocking_reasons"]

    if generate_fact_report:
        report_path = str(
            generate_report.generate_report(
                ticker=normalized_ticker,
                validation_status=validation_status,
                research_gaps=gap_result["gaps"],
                ratio_outputs=ratio_result["ratios"],
                audit_log_reference=str(audit_log_path),
                dcf_output=dcf_result if dcf_output_path else None,
                warnings=warnings,
                reports_dir=reports_dir,
            )
        )

    methodology = validate_methodology.load_json(methodology_path)
    audit_record = write_audit_log.build_audit_record(
        ticker=normalized_ticker,
        methodology_version=methodology["methodology_version"],
        data_context_path=str(context_path),
        source_files_used=[str(source_data_path)],
        validation_status=validation_status,
        ratio_outputs=ratio_result["ratios"],
        research_gaps_detected=gap_result["gaps"],
    )
    write_audit_log.append_audit_record(audit_record, audit_log_path)

    return _summary(
        ticker=normalized_ticker,
        validation_status=validation_status,
        research_gaps_count=len(gap_result["gaps"]),
        ratios_calculated=[ratio["ratio_name"] for ratio in ratio_result["ratios"]],
        audit_log_written=True,
        report_path=report_path,
        dcf_run=dcf_output_path is not None,
        dcf_scenarios_calculated=dcf_scenarios_calculated,
        dcf_output_path=dcf_output_path,
        dcf_warnings=dcf_warnings,
        warnings=warnings,
    )


def _summary(
    ticker: str,
    validation_status: dict[str, Any],
    research_gaps_count: int,
    ratios_calculated: list[str],
    audit_log_written: bool,
    report_path: str | None,
    dcf_run: bool,
    dcf_scenarios_calculated: list[str],
    dcf_output_path: str | None,
    dcf_warnings: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "ticker": ticker,
        "validation_status": validation_status,
        "research_gaps_count": research_gaps_count,
        "ratios_calculated": ratios_calculated,
        "audit_log_written": audit_log_written,
        "report_path": report_path,
        "dcf_run": dcf_run,
        "dcf_scenarios_calculated": dcf_scenarios_calculated,
        "dcf_output_path": dcf_output_path,
        "dcf_warnings": dcf_warnings,
        "warnings": warnings,
    }


def _write_dcf_output(ticker: str, dcf_result: dict[str, Any], reports_dir: Path) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{ticker}_dcf_output.json"
    output_path.write_text(json.dumps(dcf_result, indent=2, sort_keys=True), encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic pre-valuation analysis workflow for one ticker.")
    parser.add_argument("ticker")
    parser.add_argument("--source-data-path", type=Path, required=True)
    parser.add_argument("--context-root", type=Path, default=DEFAULT_CONTEXT_ROOT)
    parser.add_argument("--markdown-queue-path", type=Path, default=DEFAULT_MARKDOWN_QUEUE_PATH)
    parser.add_argument("--json-queue-path", type=Path, default=DEFAULT_JSON_QUEUE_PATH)
    parser.add_argument("--audit-log-path", type=Path, default=DEFAULT_AUDIT_LOG_PATH)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--methodology-path", type=Path, default=validate_methodology.DEFAULT_METHODOLOGY_PATH)
    parser.add_argument("--watchlist-path", type=Path, default=detect_research_gaps.DEFAULT_WATCHLIST_PATH)
    parser.add_argument("--no-rebuild-context", action="store_true")
    parser.add_argument("--generate-report", action="store_true")
    parser.add_argument("--run-dcf", action="store_true")
    parser.add_argument("--dcf-assumptions-path", type=Path)
    args = parser.parse_args()

    try:
        result = run_analysis(
            ticker=args.ticker,
            source_data_path=args.source_data_path,
            context_root=args.context_root,
            markdown_queue_path=args.markdown_queue_path,
            json_queue_path=args.json_queue_path,
            audit_log_path=args.audit_log_path,
            reports_dir=args.reports_dir,
            methodology_path=args.methodology_path,
            watchlist_path=args.watchlist_path,
            rebuild_context=not args.no_rebuild_context,
            generate_fact_report=args.generate_report,
            run_dcf=args.run_dcf,
            dcf_assumptions_path=args.dcf_assumptions_path,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ticker": args.ticker.upper(), "error": str(exc)}, indent=2))
        return 1

    print(json.dumps(result, indent=2))
    return 0 if result["validation_status"]["valid"] and result["audit_log_written"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

