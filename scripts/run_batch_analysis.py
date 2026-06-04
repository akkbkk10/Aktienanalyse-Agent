from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_analysis


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORTS_DIR = REPO_ROOT / "reports" / "batch"
DEFAULT_CONTEXT_ROOT = REPO_ROOT / "reports" / "batch" / "companies"
DEFAULT_AUDIT_LOG_PATH = REPO_ROOT / "reports" / "batch" / "audit_log.jsonl"


def run_batch(
    tickers: list[str],
    source_data_paths: dict[str, Path] | None = None,
    context_root: Path = DEFAULT_CONTEXT_ROOT,
    reports_dir: Path = DEFAULT_REPORTS_DIR,
    audit_log_path: Path = DEFAULT_AUDIT_LOG_PATH,
    markdown_queue_path: Path | None = None,
    json_queue_path: Path | None = None,
    generate_fact_report: bool = False,
    generate_summary: bool = False,
    run_dcf: bool = False,
    today: date | None = None,
) -> dict[str, Any]:
    normalized_tickers = [ticker.upper() for ticker in tickers]
    source_data_paths = {ticker.upper(): path for ticker, path in (source_data_paths or {}).items()}
    successful_runs: list[str] = []
    failed_runs: dict[str, dict[str, Any]] = {}
    output_paths_by_ticker: dict[str, dict[str, str | None]] = {}
    warnings_by_ticker: dict[str, list[str]] = {}

    for ticker in normalized_tickers:
        ticker_reports_dir = reports_dir / ticker
        source_data_path = source_data_paths.get(ticker, _default_source_data_path(ticker))
        dcf_assumptions_path = _default_dcf_assumptions_path(ticker)

        try:
            summary = run_analysis.run_analysis(
                ticker=ticker,
                source_data_path=source_data_path,
                context_root=context_root,
                markdown_queue_path=markdown_queue_path or reports_dir / "research_queue.md",
                json_queue_path=json_queue_path or reports_dir / "research_queue.json",
                audit_log_path=audit_log_path,
                reports_dir=ticker_reports_dir,
                generate_fact_report=generate_fact_report,
                generate_summary=generate_summary,
                run_dcf=run_dcf,
                dcf_assumptions_path=dcf_assumptions_path if dcf_assumptions_path.exists() else None,
                today=today,
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            failed_runs[ticker] = {"error": str(exc)}
            output_paths_by_ticker[ticker] = {}
            warnings_by_ticker[ticker] = [str(exc)]
            continue

        if summary.get("validation_status", {}).get("valid") and summary.get("audit_log_written"):
            successful_runs.append(ticker)
        else:
            failed_runs[ticker] = {"summary": summary}

        output_paths_by_ticker[ticker] = {
            "report_path": summary.get("report_path"),
            "analysis_summary_path": summary.get("analysis_summary_path"),
            "dcf_output_path": summary.get("dcf_output_path"),
            "fair_value_per_share_output_path": summary.get("fair_value_per_share_output_path"),
            "model_rating_output_path": summary.get("model_rating_output_path"),
            "model_rating_status": summary.get("model_rating_status"),
            "model_confidence_output_path": summary.get("model_confidence_output_path"),
            "model_signal_output_path": summary.get("model_signal_output_path"),
            "audit_log_path": str(audit_log_path) if summary.get("audit_log_written") else None,
        }
        warnings_by_ticker[ticker] = (
            summary.get("warnings", [])
            + summary.get("dcf_warnings", [])
            + summary.get("model_rating_unavailable_reasons", [])
        )

    return {
        "tickers_processed": normalized_tickers,
        "successful_runs": successful_runs,
        "failed_runs": failed_runs,
        "output_paths_by_ticker": output_paths_by_ticker,
        "warnings_by_ticker": warnings_by_ticker,
    }


def _default_source_data_path(ticker: str) -> Path:
    if ticker == "NVDA":
        return REPO_ROOT / "data" / "nvda_sample_metrics.json"
    return REPO_ROOT / "data" / f"{ticker.lower()}_sample_metrics.json"


def _default_dcf_assumptions_path(ticker: str) -> Path:
    return REPO_ROOT / "data" / "companies" / ticker / "dcf_assumptions.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the deterministic workflow independently for one or more tickers.",
        epilog=(
            "Each ticker is processed independently. Generated artifacts are written "
            "under --reports-dir and should remain in ignored reports/ paths. The "
            "batch workflow never fetches live data and does not produce price "
            "targets, recommendations, investment advice, or trading actions."
        ),
    )
    parser.add_argument("tickers", nargs="+", help="Ticker symbols to process, for example: NVDA AMD TSMC.")
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR, help="Output directory for generated batch artifacts.")
    parser.add_argument("--context-root", type=Path, default=DEFAULT_CONTEXT_ROOT, help="Directory for generated company contexts.")
    parser.add_argument("--audit-log-path", type=Path, default=DEFAULT_AUDIT_LOG_PATH, help="Path for the batch audit log JSONL file.")
    parser.add_argument("--generate-report", action="store_true", help="Generate fact-only Markdown reports.")
    parser.add_argument("--generate-summary", action="store_true", help="Generate structured JSON analysis summaries.")
    parser.add_argument("--run-dcf", action="store_true", help="Run DCF and downstream model-output stages when readiness passes.")
    args = parser.parse_args()

    result = run_batch(
        tickers=args.tickers,
        context_root=args.context_root,
        reports_dir=args.reports_dir,
        audit_log_path=args.audit_log_path,
        generate_fact_report=args.generate_report,
        generate_summary=args.generate_summary,
        run_dcf=args.run_dcf,
    )
    print(json.dumps(result, indent=2))
    return 0 if not result["failed_runs"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
