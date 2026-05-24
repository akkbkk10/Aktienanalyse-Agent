from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_batch_analysis


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TICKERS = ["NVDA", "AMD", "TSMC"]
DEFAULT_REPORTS_DIR = REPO_ROOT / "reports" / "v1_0_demo"
REQUIRED_ARTIFACT_KEYS = [
    "report_path",
    "analysis_summary_path",
    "dcf_output_path",
    "fair_value_per_share_output_path",
    "model_rating_output_path",
    "model_confidence_output_path",
    "model_signal_output_path",
    "audit_log_path",
]


def run_demo(
    tickers: list[str] | None = None,
    reports_dir: Path = DEFAULT_REPORTS_DIR,
) -> dict[str, Any]:
    normalized_tickers = [ticker.upper() for ticker in (tickers or DEFAULT_TICKERS)]
    reports_dir.mkdir(parents=True, exist_ok=True)
    context_root = reports_dir / "companies"
    audit_log_path = reports_dir / "audit_log.jsonl"

    batch_result = run_batch_analysis.run_batch(
        tickers=normalized_tickers,
        context_root=context_root,
        reports_dir=reports_dir,
        audit_log_path=audit_log_path,
        generate_fact_report=True,
        generate_summary=True,
        run_dcf=True,
    )
    generated_file_paths = _generated_file_paths(batch_result)

    return {
        "demo_version": "1.0-rc",
        "tickers": normalized_tickers,
        "demo_completed": _demo_completed(batch_result),
        "generated_file_paths": generated_file_paths,
        "manual_review_checklist": str(REPO_ROOT / "docs" / "V1_0_TEST_PLAN.md"),
        "batch_summary": batch_result,
    }


def _generated_file_paths(batch_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "audit_log_path": _first_audit_log_path(batch_result),
        "output_paths_by_ticker": batch_result.get("output_paths_by_ticker", {}),
    }


def _first_audit_log_path(batch_result: dict[str, Any]) -> str | None:
    for paths in batch_result.get("output_paths_by_ticker", {}).values():
        if isinstance(paths, dict) and paths.get("audit_log_path"):
            return paths["audit_log_path"]
    return None


def _demo_completed(batch_result: dict[str, Any]) -> bool:
    tickers = batch_result.get("tickers_processed", [])
    successful_runs = batch_result.get("successful_runs", [])
    failed_runs = batch_result.get("failed_runs", {})
    output_paths_by_ticker = batch_result.get("output_paths_by_ticker", {})

    if failed_runs or sorted(tickers) != sorted(successful_runs):
        return False

    for ticker in tickers:
        paths = output_paths_by_ticker.get(ticker, {})
        for key in REQUIRED_ARTIFACT_KEYS:
            value = paths.get(key)
            if not value or not Path(value).exists():
                return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the v1.0 release-candidate demo for NVDA, AMD, and TSMC.")
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--tickers", nargs="+", default=DEFAULT_TICKERS)
    args = parser.parse_args()

    try:
        result = run_demo(tickers=args.tickers, reports_dir=args.reports_dir)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"demo_completed": False, "error": str(exc)}, indent=2))
        return 1

    print(json.dumps(result, indent=2))
    return 0 if result["demo_completed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
