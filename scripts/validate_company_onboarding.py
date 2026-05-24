from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_company_context
import validate_sources


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WATCHLIST_PATH = REPO_ROOT / "config" / "watchlist.json"
DEFAULT_DCF_SCHEMA_PATH = REPO_ROOT / "config" / "dcf_assumptions_schema.json"
REQUIRED_FINANCIAL_METRICS = ["Revenue", "Net income", "Free cash flow"]
MARKET_PRICE_SNAPSHOT_FIELDS = [
    "currency",
    "exchange",
    "price_type",
    "as_of_datetime",
    "fetched_at",
    "provider",
    "retrieval_method",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_onboarding_package(
    ticker: str,
    metrics_path: Path,
    dcf_assumptions_path: Path,
    watchlist_path: Path = DEFAULT_WATCHLIST_PATH,
) -> dict[str, Any]:
    normalized_ticker = ticker.upper()
    checks: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []

    try:
        records = validate_sources.normalize_records(validate_sources.load_json(metrics_path))
        _add_check(checks, "metrics_file", True, f"Loaded {len(records)} metric record(s).")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        _add_check(checks, "metrics_file", False, f"Metrics file could not be loaded: {exc}")
        records = []

    if records:
        source_errors = validate_sources.validate_file(metrics_path)
        _add_check(
            checks,
            "source_validation",
            not source_errors,
            "Source validation passed." if not source_errors else f"Source validation failed with {len(source_errors)} error(s).",
            [error.to_dict() for error in source_errors],
        )
        _check_ticker(records, normalized_ticker, checks)
        _check_required_metrics(records, checks)
        _check_metric_ids(records, checks)
        _check_source_metadata(records, checks)
        _check_market_price_snapshot(records, checks)
        _check_share_count(records, checks)
        _check_company_context_generation(metrics_path, checks)
    else:
        for check_name in [
            "source_validation",
            "ticker_consistency",
            "required_financial_metrics",
            "metric_id_presence",
            "source_metadata",
            "market_price_snapshot",
            "share_count",
            "company_context_generation",
        ]:
            _add_check(checks, check_name, False, "Skipped because metric records were unavailable.")

    _check_dcf_assumptions(dcf_assumptions_path, normalized_ticker, checks)
    _check_watchlist(normalized_ticker, watchlist_path, checks)

    return {
        "ticker": normalized_ticker,
        "ready": all(check["passed"] for check in checks),
        "checks": checks,
        "blocking_reasons": [check["message"] for check in checks if not check["passed"]],
    }


def _check_ticker(records: list[dict[str, Any]], ticker: str, checks: list[dict[str, Any]]) -> None:
    mismatches = [index for index, record in enumerate(records) if str(record.get("ticker", "")).upper() != ticker]
    _add_check(
        checks,
        "ticker_consistency",
        not mismatches,
        "All records match the onboarding ticker." if not mismatches else f"Records with mismatched ticker: {mismatches}.",
    )


def _check_required_metrics(records: list[dict[str, Any]], checks: list[dict[str, Any]]) -> None:
    metric_names = {str(record.get("metric_name", "")) for record in records}
    missing = [metric for metric in REQUIRED_FINANCIAL_METRICS if metric not in metric_names]
    _add_check(
        checks,
        "required_financial_metrics",
        not missing,
        "Required financial metrics are present." if not missing else f"Missing required financial metrics: {', '.join(missing)}.",
    )


def _check_metric_ids(records: list[dict[str, Any]], checks: list[dict[str, Any]]) -> None:
    missing = [index for index, record in enumerate(records) if not str(record.get("metric_id", "")).strip()]
    _add_check(
        checks,
        "metric_id_presence",
        not missing,
        "Every metric has metric_id." if not missing else f"Records missing metric_id: {missing}.",
    )


def _check_source_metadata(records: list[dict[str, Any]], checks: list[dict[str, Any]]) -> None:
    required = ["source_url", "source_type", "source_date", "confidence", "last_verified"]
    missing = []
    for index, record in enumerate(records):
        missing_fields = [field for field in required if not record.get(field)]
        if missing_fields:
            missing.append({"index": index, "missing_fields": missing_fields})
    _add_check(
        checks,
        "source_metadata",
        not missing,
        "Every metric has source metadata." if not missing else "One or more records are missing source metadata.",
        missing,
    )


def _check_market_price_snapshot(records: list[dict[str, Any]], checks: list[dict[str, Any]]) -> None:
    market_records = [
        record
        for record in records
        if record.get("metric_category") == "market_price" or record.get("metric_name") == "Current market price"
    ]
    missing = []
    for index, record in enumerate(market_records):
        missing_fields = [field for field in MARKET_PRICE_SNAPSHOT_FIELDS if not record.get(field)]
        if missing_fields:
            missing.append({"market_record_index": index, "missing_fields": missing_fields})
    passed = bool(market_records) and not missing
    if not market_records:
        message = "Market price snapshot record is missing."
    elif missing:
        message = "Market price snapshot is missing required fields."
    else:
        message = "Market price snapshot fields are present."
    _add_check(checks, "market_price_snapshot", passed, message, missing)


def _check_share_count(records: list[dict[str, Any]], checks: list[dict[str, Any]]) -> None:
    share_count_records = [
        record
        for record in records
        if record.get("metric_category") == "share_count"
        or "share" in str(record.get("metric_name", "")).lower()
    ]
    _add_check(
        checks,
        "share_count",
        bool(share_count_records),
        "Share count metric is present." if share_count_records else "Share count metric is missing.",
    )


def _check_company_context_generation(metrics_path: Path, checks: list[dict[str, Any]]) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            context = build_company_context.build_company_context(metrics_path, output_root=Path(temp_dir))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            _add_check(checks, "company_context_generation", False, f"Company context generation failed: {exc}")
            return
    _add_check(
        checks,
        "company_context_generation",
        bool(context.get("metrics")),
        "Company context generation passed.",
    )


def _check_dcf_assumptions(dcf_assumptions_path: Path, ticker: str, checks: list[dict[str, Any]]) -> None:
    try:
        assumptions = load_json(dcf_assumptions_path)
        schema = load_json(DEFAULT_DCF_SCHEMA_PATH)
    except (OSError, json.JSONDecodeError) as exc:
        _add_check(checks, "dcf_assumptions", False, f"DCF assumptions could not be loaded: {exc}")
        return

    missing = []
    for field in schema.get("required_fields", []):
        if not assumptions.get(field):
            missing.append(field)
    if str(assumptions.get("ticker", "")).upper() != ticker:
        missing.append("ticker")

    scenarios = assumptions.get("scenarios", {})
    for scenario_name in schema.get("required_scenarios", []):
        scenario = scenarios.get(scenario_name) if isinstance(scenarios, dict) else None
        if not isinstance(scenario, dict):
            missing.append(f"scenarios.{scenario_name}")
            continue
        for field in schema.get("required_scenario_fields", []):
            if scenario.get(field) in (None, "", []):
                missing.append(f"scenarios.{scenario_name}.{field}")

    for index, source in enumerate(assumptions.get("source_references", [])):
        for field in schema.get("source_reference_fields", []):
            if not source.get(field):
                missing.append(f"source_references.{index}.{field}")

    _add_check(
        checks,
        "dcf_assumptions",
        not missing,
        "DCF assumptions are complete." if not missing else f"DCF assumptions missing fields: {', '.join(missing)}.",
        missing,
    )


def _check_watchlist(ticker: str, watchlist_path: Path, checks: list[dict[str, Any]]) -> None:
    try:
        watchlist = load_json(watchlist_path)
    except (OSError, json.JSONDecodeError) as exc:
        _add_check(checks, "watchlist_entry", False, f"Watchlist could not be loaded: {exc}")
        return

    tickers = watchlist.get("tickers", {}) if isinstance(watchlist, dict) else {}
    entry = tickers.get(ticker)
    if not isinstance(entry, dict):
        _add_check(checks, "watchlist_entry", False, f"Watchlist entry for {ticker} is missing.")
        return

    required_metrics = entry.get("required_metrics")
    passed = isinstance(required_metrics, list) and bool(required_metrics)
    _add_check(
        checks,
        "watchlist_entry",
        passed,
        "Watchlist entry is present." if passed else f"Watchlist entry for {ticker} has no required_metrics.",
    )


def _add_check(
    checks: list[dict[str, Any]],
    name: str,
    passed: bool,
    message: str,
    details: Any | None = None,
) -> None:
    check = {"name": name, "passed": passed, "message": message}
    if details:
        check["details"] = details
    checks.append(check)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a new company onboarding package.")
    parser.add_argument("ticker")
    parser.add_argument("--metrics-path", type=Path, required=True)
    parser.add_argument("--dcf-assumptions-path", type=Path, required=True)
    parser.add_argument("--watchlist-path", type=Path, default=DEFAULT_WATCHLIST_PATH)
    args = parser.parse_args()

    result = validate_onboarding_package(
        ticker=args.ticker,
        metrics_path=args.metrics_path,
        dcf_assumptions_path=args.dcf_assumptions_path,
        watchlist_path=args.watchlist_path,
    )
    print(json.dumps(result, indent=2))
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
