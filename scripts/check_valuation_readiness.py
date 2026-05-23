from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import calculate_ratios
import detect_research_gaps
import generate_report
import validate_methodology
import validate_sources
import write_audit_log


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTEXT_ROOT = REPO_ROOT / "data" / "companies"
DEFAULT_READINESS_AUDIT_LOG_PATH = REPO_ROOT / "reports" / "valuation_readiness_audit_probe.jsonl"
HIGH_PRIORITY_GAP_TYPES = {"missing_context", "missing_metric", "missing_source_metadata", "stale_metric"}


def check_readiness(
    ticker: str,
    source_data_path: Path,
    context_root: Path = DEFAULT_CONTEXT_ROOT,
    methodology_path: Path = validate_methodology.DEFAULT_METHODOLOGY_PATH,
    watchlist_path: Path = detect_research_gaps.DEFAULT_WATCHLIST_PATH,
    audit_log_path: Path = DEFAULT_READINESS_AUDIT_LOG_PATH,
    report_path: Path | None = None,
    validation_status: dict[str, Any] | None = None,
    ratio_result: dict[str, Any] | None = None,
    research_gaps: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    normalized_ticker = ticker.upper()
    blocking_reasons: list[str] = []
    warnings: list[str] = []
    required_next_actions: list[str] = []

    validation_status = validation_status or _validate_source_data(source_data_path)
    if not validation_status["valid"]:
        _block(
            blocking_reasons,
            required_next_actions,
            "Source validation failed.",
            "Resolve source validation errors before valuation readiness can pass.",
        )

    methodology_errors = validate_methodology.validate_methodology_file(methodology_path)
    methodology = _load_methodology(methodology_path, warnings)
    if methodology_errors:
        _block(
            blocking_reasons,
            required_next_actions,
            "Methodology config is invalid.",
            "Fix methodology configuration validation errors.",
        )

    if research_gaps is None:
        research_gaps = detect_research_gaps.detect_gaps(
            watchlist_path=watchlist_path,
            context_root=context_root,
        )
    high_priority_gaps = _high_priority_gaps(research_gaps)
    if high_priority_gaps:
        _block(
            blocking_reasons,
            required_next_actions,
            f"{len(high_priority_gaps)} high-priority research gap(s) remain open.",
            "Resolve high-priority research gaps and refresh the company context.",
        )

    if ratio_result is None:
        ratio_result = _calculate_ratios(normalized_ticker, context_root, warnings, blocking_reasons, required_next_actions)
    _check_required_ratios(methodology, ratio_result, blocking_reasons, required_next_actions)

    _check_prohibited_outputs(report_path, ratio_result, research_gaps, blocking_reasons, required_next_actions)

    methodology_version = str(methodology.get("methodology_version", "unknown"))
    _check_audit_log_write(
        ticker=normalized_ticker,
        methodology_version=methodology_version,
        source_data_path=source_data_path,
        context_path=context_root / normalized_ticker / "context.json",
        audit_log_path=audit_log_path,
        validation_status=validation_status,
        ratio_outputs=ratio_result.get("ratios", []),
        research_gaps=research_gaps,
        blocking_reasons=blocking_reasons,
        required_next_actions=required_next_actions,
    )

    return {
        "ticker": normalized_ticker,
        "ready_for_valuation": not blocking_reasons,
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
        "required_next_actions": _unique(required_next_actions),
    }


def _validate_source_data(source_data_path: Path) -> dict[str, Any]:
    try:
        errors = validate_sources.validate_file(source_data_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"valid": False, "errors": [{"message": str(exc)}]}
    return {"valid": not errors, "errors": [error.to_dict() for error in errors]}


def _load_methodology(methodology_path: Path, warnings: list[str]) -> dict[str, Any]:
    try:
        payload = validate_methodology.load_json(methodology_path)
    except (OSError, json.JSONDecodeError) as exc:
        warnings.append(f"Methodology config could not be loaded: {exc}")
        return {}
    if not isinstance(payload, dict):
        warnings.append("Methodology config is not a JSON object.")
        return {}
    return payload


def _calculate_ratios(
    ticker: str,
    context_root: Path,
    warnings: list[str],
    blocking_reasons: list[str],
    required_next_actions: list[str],
) -> dict[str, Any]:
    try:
        return calculate_ratios.calculate_ratios_for_ticker(
            ticker=ticker,
            context_root=context_root,
            queue_missing=False,
        )
    except (OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        warnings.append(f"Ratio calculation could not run: {exc}")
        _block(
            blocking_reasons,
            required_next_actions,
            "Required ratios are unavailable.",
            "Build a valid company context and calculate required ratios.",
        )
        return {"ticker": ticker, "ratios": [], "missing_inputs": [], "skipped": []}


def _check_required_ratios(
    methodology: dict[str, Any],
    ratio_result: dict[str, Any],
    blocking_reasons: list[str],
    required_next_actions: list[str],
) -> None:
    required_ratios = methodology.get("required_ratio_inputs", [])
    if not isinstance(required_ratios, list):
        return

    calculated = {
        ratio.get("ratio_name")
        for ratio in ratio_result.get("ratios", [])
        if isinstance(ratio, dict) and ratio.get("ratio_name")
    }
    missing = sorted(str(ratio) for ratio in required_ratios if ratio not in calculated)
    if missing:
        _block(
            blocking_reasons,
            required_next_actions,
            f"Missing required ratios: {', '.join(missing)}.",
            "Calculate all required ratios from validated company context.",
        )


def _high_priority_gaps(gaps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    high_priority = []
    for gap in gaps:
        priority = str(gap.get("priority") or gap.get("severity") or "").lower()
        gap_type = str(gap.get("gap_type") or "")
        if priority == "high" or gap_type in HIGH_PRIORITY_GAP_TYPES:
            high_priority.append(gap)
    return high_priority


def _check_prohibited_outputs(
    report_path: Path | None,
    ratio_result: dict[str, Any],
    research_gaps: list[dict[str, Any]],
    blocking_reasons: list[str],
    required_next_actions: list[str],
) -> None:
    try:
        generate_report.assert_no_prohibited_language(json.dumps(ratio_result))
        generate_report.assert_no_prohibited_language(json.dumps(research_gaps))
        if report_path is not None and report_path.exists():
            generate_report.assert_no_prohibited_language(report_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        _block(
            blocking_reasons,
            required_next_actions,
            f"Prohibited valuation-stage output detected: {exc}",
            "Remove prohibited valuation-stage language or outputs before proceeding.",
        )


def _check_audit_log_write(
    ticker: str,
    methodology_version: str,
    source_data_path: Path,
    context_path: Path,
    audit_log_path: Path,
    validation_status: dict[str, Any],
    ratio_outputs: list[dict[str, Any]],
    research_gaps: list[dict[str, Any]],
    blocking_reasons: list[str],
    required_next_actions: list[str],
) -> None:
    try:
        record = write_audit_log.build_audit_record(
            ticker=ticker,
            methodology_version=methodology_version,
            data_context_path=str(context_path),
            source_files_used=[str(source_data_path)],
            validation_status=validation_status,
            ratio_outputs=ratio_outputs,
            research_gaps_detected=research_gaps,
        )
        write_audit_log.append_audit_record(record, audit_log_path)
    except (OSError, ValueError) as exc:
        _block(
            blocking_reasons,
            required_next_actions,
            f"Audit log write check failed: {exc}",
            "Ensure the audit log path is writable.",
        )


def _block(
    blocking_reasons: list[str],
    required_next_actions: list[str],
    reason: str,
    action: str,
) -> None:
    blocking_reasons.append(reason)
    required_next_actions.append(action)


def _unique(values: list[str]) -> list[str]:
    seen = set()
    unique_values = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        unique_values.append(value)
    return unique_values


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether a ticker is ready for a future valuation stage.")
    parser.add_argument("ticker")
    parser.add_argument("--source-data-path", type=Path, required=True)
    parser.add_argument("--context-root", type=Path, default=DEFAULT_CONTEXT_ROOT)
    parser.add_argument("--methodology-path", type=Path, default=validate_methodology.DEFAULT_METHODOLOGY_PATH)
    parser.add_argument("--watchlist-path", type=Path, default=detect_research_gaps.DEFAULT_WATCHLIST_PATH)
    parser.add_argument("--audit-log-path", type=Path, default=DEFAULT_READINESS_AUDIT_LOG_PATH)
    parser.add_argument("--report-path", type=Path)
    args = parser.parse_args()

    result = check_readiness(
        ticker=args.ticker,
        source_data_path=args.source_data_path,
        context_root=args.context_root,
        methodology_path=args.methodology_path,
        watchlist_path=args.watchlist_path,
        audit_log_path=args.audit_log_path,
        report_path=args.report_path,
    )
    print(json.dumps(result, indent=2))
    return 0 if result["ready_for_valuation"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
