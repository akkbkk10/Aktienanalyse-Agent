from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORTS_DIR = REPO_ROOT / "reports"
PROHIBITED_TERMS = [
    "price target",
    "buy",
    "sell",
    "hold",
    "recommendation",
    "investment advice",
    "automated trading",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def generate_analysis_summary(
    ticker: str,
    validation_status: dict[str, Any],
    research_gaps: list[dict[str, Any]],
    ratio_outputs: list[dict[str, Any]],
    audit_log_reference: str,
    dcf_output: dict[str, Any] | None = None,
    fair_value_per_share_output: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
    reports_dir: Path = DEFAULT_REPORTS_DIR,
    generated_at: str | None = None,
) -> Path:
    summary = build_analysis_summary(
        ticker=ticker,
        validation_status=validation_status,
        research_gaps=research_gaps,
        ratio_outputs=ratio_outputs,
        audit_log_reference=audit_log_reference,
        dcf_output=dcf_output,
        fair_value_per_share_output=fair_value_per_share_output,
        warnings=warnings or [],
        generated_at=generated_at,
    )
    assert_no_prohibited_language(summary)

    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{ticker.upper()}_analysis_summary.json"
    output_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return output_path


def build_analysis_summary(
    ticker: str,
    validation_status: dict[str, Any],
    research_gaps: list[dict[str, Any]],
    ratio_outputs: list[dict[str, Any]],
    audit_log_reference: str,
    dcf_output: dict[str, Any] | None = None,
    fair_value_per_share_output: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    normalized_ticker = ticker.upper()
    timestamp = generated_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    dcf_scenarios = dcf_output.get("scenarios", {}) if dcf_output else {}
    dcf_assumptions = dcf_output.get("assumptions_used", {}) if dcf_output else None
    dcf_warnings = dcf_output.get("warnings", []) if dcf_output else []
    fair_value_scenarios = fair_value_per_share_output.get("scenarios", []) if fair_value_per_share_output else []
    fair_value_assumptions = fair_value_per_share_output.get("assumptions", {}) if fair_value_per_share_output else None
    fair_value_warnings = fair_value_per_share_output.get("warnings", []) if fair_value_per_share_output else []

    summary = {
        "ticker": normalized_ticker,
        "generated_at": timestamp,
        "audit_log_reference": audit_log_reference,
        "facts": {
            "validation_status": validation_status,
            "ratio_source_references": _ratio_source_references(ratio_outputs),
            "dcf_source_references": dcf_output.get("source_references", []) if dcf_output else [],
            "fair_value_per_share_source_references": fair_value_per_share_output.get("source_references", []) if fair_value_per_share_output else [],
        },
        "assumptions": {
            "dcf_assumptions": dcf_assumptions,
            "dcf_available": dcf_output is not None,
            "fair_value_per_share_assumptions": fair_value_assumptions,
            "fair_value_per_share_available": fair_value_per_share_output is not None,
        },
        "calculated_outputs": {
            "ratios": ratio_outputs,
            "dcf_scenarios": dcf_scenarios,
            "fair_value_per_share_scenarios": fair_value_scenarios,
        },
        "missing_data": {
            "research_gaps": research_gaps,
            "dcf_status": "included" if dcf_output else "not provided",
            "fair_value_per_share_status": "included" if fair_value_per_share_output else "not provided",
        },
        "risks_warnings": {
            "warnings": warnings or [],
            "dcf_warnings": dcf_warnings,
            "fair_value_per_share_warnings": fair_value_warnings,
        },
    }
    return summary


def assert_no_prohibited_language(summary: dict[str, Any]) -> None:
    serialized = json.dumps(summary).lower().replace("not investment advice", "")
    found = [term for term in PROHIBITED_TERMS if term in serialized]
    if found:
        raise ValueError(f"Analysis summary contains prohibited language: {', '.join(found)}.")


def _ratio_source_references(ratio_outputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    references = []
    seen = set()
    for ratio in ratio_outputs:
        for source in ratio.get("source_metric_references", []):
            key = (
                source.get("metric_name"),
                source.get("period"),
                source.get("source_url"),
            )
            if key in seen:
                continue
            seen.add(key)
            references.append(source)
    return references


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a structured analysis summary JSON file.")
    parser.add_argument("ticker")
    parser.add_argument("--validation-status-json", type=Path, required=True)
    parser.add_argument("--research-gaps-json", type=Path, required=True)
    parser.add_argument("--ratio-outputs-json", type=Path, required=True)
    parser.add_argument("--dcf-output-json", type=Path)
    parser.add_argument("--fair-value-per-share-json", type=Path)
    parser.add_argument("--audit-log-reference", required=True)
    parser.add_argument("--warning", action="append", dest="warnings", default=[])
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    args = parser.parse_args()

    try:
        output_path = generate_analysis_summary(
            ticker=args.ticker,
            validation_status=load_json(args.validation_status_json),
            research_gaps=load_json(args.research_gaps_json),
            ratio_outputs=load_json(args.ratio_outputs_json),
            audit_log_reference=args.audit_log_reference,
            dcf_output=load_json(args.dcf_output_json) if args.dcf_output_json else None,
            fair_value_per_share_output=load_json(args.fair_value_per_share_json) if args.fair_value_per_share_json else None,
            warnings=args.warnings,
            reports_dir=args.reports_dir,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"created": False, "error": str(exc)}, indent=2))
        return 1

    print(json.dumps({"created": True, "summary_path": str(output_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
