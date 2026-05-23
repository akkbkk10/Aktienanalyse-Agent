from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_analysis


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TICKER = "NVDA"
DEFAULT_SOURCE_DATA_PATH = REPO_ROOT / "data" / "nvda_sample_metrics.json"
DEFAULT_REPORTS_DIR = REPO_ROOT / "reports" / "v0_1_demo"
DEFAULT_DCF_ASSUMPTIONS_TEMPLATE = REPO_ROOT / "data" / "companies" / "{ticker}" / "dcf_assumptions.json"


def run_demo(
    ticker: str = DEFAULT_TICKER,
    source_data_path: Path = DEFAULT_SOURCE_DATA_PATH,
    reports_dir: Path = DEFAULT_REPORTS_DIR,
    dcf_assumptions_path: Path | None = None,
) -> dict[str, Any]:
    normalized_ticker = ticker.upper()
    reports_dir.mkdir(parents=True, exist_ok=True)
    context_root = reports_dir / "companies"
    audit_log_path = reports_dir / "audit_log.jsonl"
    markdown_queue_path = reports_dir / "research_queue.md"
    json_queue_path = reports_dir / "research_queue.json"
    assumptions_path = dcf_assumptions_path or Path(
        str(DEFAULT_DCF_ASSUMPTIONS_TEMPLATE).format(ticker=normalized_ticker)
    )

    summary = run_analysis.run_analysis(
        ticker=normalized_ticker,
        source_data_path=source_data_path,
        context_root=context_root,
        markdown_queue_path=markdown_queue_path,
        json_queue_path=json_queue_path,
        audit_log_path=audit_log_path,
        reports_dir=reports_dir,
        generate_fact_report=True,
        generate_summary=True,
        run_dcf=True,
        dcf_assumptions_path=assumptions_path,
    )

    generated_file_paths = {
        "context_path": str(context_root / normalized_ticker / "context.json"),
        "audit_log_path": str(audit_log_path),
        "readiness_audit_log_path": str(reports_dir / f"{normalized_ticker}_valuation_readiness_audit_probe.jsonl"),
        "dcf_output_path": summary.get("dcf_output_path"),
        "fact_report_path": summary.get("report_path"),
        "analysis_summary_path": summary.get("analysis_summary_path"),
        "research_queue_json_path": str(json_queue_path) if json_queue_path.exists() else None,
        "research_queue_markdown_path": str(markdown_queue_path) if markdown_queue_path.exists() else None,
    }

    return {
        "ticker": normalized_ticker,
        "demo_completed": _demo_completed(summary),
        "generated_file_paths": generated_file_paths,
        "orchestrator_summary": summary,
    }


def _demo_completed(summary: dict[str, Any]) -> bool:
    return bool(
        summary.get("validation_status", {}).get("valid")
        and summary.get("audit_log_written")
        and summary.get("dcf_run")
        and summary.get("dcf_output_path")
        and summary.get("report_path")
        and summary.get("analysis_summary_path")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the full v0.1 NVDA demo workflow.")
    parser.add_argument("--ticker", default=DEFAULT_TICKER)
    parser.add_argument("--source-data-path", type=Path, default=DEFAULT_SOURCE_DATA_PATH)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--dcf-assumptions-path", type=Path)
    args = parser.parse_args()

    try:
        result = run_demo(
            ticker=args.ticker,
            source_data_path=args.source_data_path,
            reports_dir=args.reports_dir,
            dcf_assumptions_path=args.dcf_assumptions_path,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"demo_completed": False, "error": str(exc)}, indent=2))
        return 1

    print(json.dumps(result, indent=2))
    return 0 if result["demo_completed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
