from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORTS_DIR = REPO_ROOT / "reports"
PROHIBITED_TERMS = [
    "valuation",
    "fair value",
    "intrinsic value",
    "price target",
    "buy",
    "sell",
    "hold",
    "recommendation",
    "investment advice",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def generate_report(
    ticker: str,
    validation_status: dict[str, Any],
    research_gaps: list[dict[str, Any]],
    ratio_outputs: list[dict[str, Any]],
    audit_log_reference: str,
    warnings: list[str] | None = None,
    reports_dir: Path = DEFAULT_REPORTS_DIR,
    generated_at: str | None = None,
) -> Path:
    normalized_ticker = ticker.upper()
    timestamp = generated_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report = render_report(
        ticker=normalized_ticker,
        validation_status=validation_status,
        research_gaps=research_gaps,
        ratio_outputs=ratio_outputs,
        audit_log_reference=audit_log_reference,
        warnings=warnings or [],
        generated_at=timestamp,
    )
    assert_no_prohibited_language(report)

    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"{normalized_ticker}_fact_report.md"
    report_path.write_text(report, encoding="utf-8")
    return report_path


def render_report(
    ticker: str,
    validation_status: dict[str, Any],
    research_gaps: list[dict[str, Any]],
    ratio_outputs: list[dict[str, Any]],
    audit_log_reference: str,
    warnings: list[str],
    generated_at: str,
) -> str:
    lines = [
        f"# {ticker} Fact Report",
        "",
        f"- Generated at: {generated_at}",
        f"- Ticker: {ticker}",
        f"- Audit log reference: {audit_log_reference}",
        "",
        "## Facts",
        "",
        "### Validation Status",
        "",
        f"- Valid: {validation_status.get('valid')}",
        f"- Errors: {len(validation_status.get('errors', []))}",
        "",
        "### Calculated Ratios",
        "",
    ]

    if ratio_outputs:
        for ratio in ratio_outputs:
            lines.extend(_ratio_lines(ratio))
    else:
        lines.append("- No calculated ratios provided.")

    lines.extend(["", "### Source References", ""])
    source_lines = _source_reference_lines(ratio_outputs)
    lines.extend(source_lines if source_lines else ["- No source references provided."])

    lines.extend(["", "## Missing Data", ""])
    if research_gaps:
        for gap in research_gaps:
            metric_name = gap.get("metric_name") or "company context"
            lines.append(f"- {gap.get('gap_type')}: {metric_name} - {gap.get('message')}")
    else:
        lines.append("- No research gaps provided.")

    lines.extend(["", "## Warnings", ""])
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- No warnings provided.")

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This report is fact-only and contains no target prices or advice.",
        ]
    )
    return "\n".join(lines) + "\n"


def assert_no_prohibited_language(report: str) -> None:
    normalized_report = report.lower()
    found = [term for term in PROHIBITED_TERMS if term in normalized_report]
    if found:
        raise ValueError(f"Report contains prohibited language: {', '.join(found)}.")


def _ratio_lines(ratio: dict[str, Any]) -> list[str]:
    return [
        f"- {ratio.get('ratio_name')} ({ratio.get('period')}): {ratio.get('value')}",
        f"  - Formula: {ratio.get('formula')}",
        f"  - Confidence: {ratio.get('confidence')}",
    ]


def _source_reference_lines(ratio_outputs: list[dict[str, Any]]) -> list[str]:
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
            references.append(
                f"- {source.get('metric_name')} ({source.get('period')}): "
                f"{source.get('source_type')} dated {source.get('source_date')} - {source.get('source_url')}"
            )
    return references


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a fact-only Markdown report for one ticker.")
    parser.add_argument("ticker")
    parser.add_argument("--validation-status-json", type=Path, required=True)
    parser.add_argument("--research-gaps-json", type=Path, required=True)
    parser.add_argument("--ratio-outputs-json", type=Path, required=True)
    parser.add_argument("--audit-log-reference", required=True)
    parser.add_argument("--warning", action="append", dest="warnings", default=[])
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    args = parser.parse_args()

    try:
        report_path = generate_report(
            ticker=args.ticker,
            validation_status=load_json(args.validation_status_json),
            research_gaps=load_json(args.research_gaps_json),
            ratio_outputs=load_json(args.ratio_outputs_json),
            audit_log_reference=args.audit_log_reference,
            warnings=args.warnings,
            reports_dir=args.reports_dir,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"created": False, "error": str(exc)}, indent=2))
        return 1

    print(json.dumps({"created": True, "report_path": str(report_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

