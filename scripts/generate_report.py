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
    dcf_output: dict[str, Any] | None = None,
    fair_value_per_share_output: dict[str, Any] | None = None,
    model_rating_output: dict[str, Any] | None = None,
    model_rating_status: str = "not_requested",
    model_rating_unavailable_reasons: list[str] | None = None,
    model_confidence_output: dict[str, Any] | None = None,
    model_signal_output: dict[str, Any] | None = None,
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
        dcf_output=dcf_output,
        fair_value_per_share_output=fair_value_per_share_output,
        model_rating_output=model_rating_output,
        model_rating_status=model_rating_status,
        model_rating_unavailable_reasons=model_rating_unavailable_reasons or [],
        model_confidence_output=model_confidence_output,
        model_signal_output=model_signal_output,
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
    dcf_output: dict[str, Any] | None,
    fair_value_per_share_output: dict[str, Any] | None = None,
    model_rating_output: dict[str, Any] | None = None,
    model_rating_status: str = "not_requested",
    model_rating_unavailable_reasons: list[str] | None = None,
    model_confidence_output: dict[str, Any] | None = None,
    model_signal_output: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
    generated_at: str = "",
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

    if dcf_output:
        lines.extend(_dcf_section_lines(dcf_output))

    if fair_value_per_share_output:
        lines.extend(_fair_value_per_share_section_lines(fair_value_per_share_output))

    if model_rating_output:
        lines.extend(_model_rating_section_lines(model_rating_output))
    elif model_rating_status == "unavailable":
        lines.extend(_model_rating_unavailable_lines(model_rating_unavailable_reasons or []))

    if model_confidence_output:
        lines.extend(_model_confidence_section_lines(model_confidence_output))

    if model_signal_output:
        lines.extend(_model_signal_section_lines(model_signal_output))

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
            "- This report is fact-only and contains no directional call or advice.",
        ]
    )
    return "\n".join(lines) + "\n"


def assert_no_prohibited_language(report: str) -> None:
    normalized_report = report.lower().replace("not investment advice", "")
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
                f"- {_metric_label(source)} ({source.get('period')}): "
                f"{source.get('source_type')} dated {source.get('source_date')} - {source.get('source_url')}"
            )
    return references


def _dcf_section_lines(dcf_output: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "### DCF Calculation Output",
        "",
        "- Disclaimer: calculation output only, not investment advice.",
        "- Unit: " + str(dcf_output.get("unit")),
        "",
        "#### Assumptions Used",
        "",
    ]

    assumptions = dcf_output.get("assumptions_used", {})
    lines.append(f"- Label: {assumptions.get('assumption_label')}")
    for scenario_name, scenario in assumptions.get("scenarios", {}).items():
        lines.append(f"- {scenario_name}:")
        lines.append(f"  - Discount rate: {scenario.get('discount_rate')}")
        lines.append(f"  - Terminal growth rate: {scenario.get('terminal_growth_rate')}")
        lines.append(f"  - Starting free cash flow: {scenario.get('starting_free_cash_flow')}")
        forecast_years = scenario.get("forecast_years", [])
        if forecast_years:
            forecast_values = ", ".join(
                f"year {forecast.get('year')} = {forecast.get('free_cash_flow')}" for forecast in forecast_years
            )
            lines.append(f"  - Forecast free cash flow: {forecast_values}")

    lines.extend(["", "#### Scenario Outputs", ""])
    for scenario_name, scenario in dcf_output.get("scenarios", {}).items():
        lines.append(f"- {scenario_name}:")
        lines.append(f"  - DCF value: {scenario.get('dcf_value')}")
        lines.append(f"  - Terminal value: {scenario.get('terminal_value')}")
        lines.append(f"  - Present value of terminal value: {scenario.get('present_value_terminal_value')}")

    lines.extend(["", "#### DCF Formulas", ""])
    for formula_name, formula in dcf_output.get("formulas", {}).items():
        lines.append(f"- {formula_name}: {formula}")

    lines.extend(["", "#### DCF Warnings", ""])
    dcf_warnings = dcf_output.get("warnings", [])
    if dcf_warnings:
        for warning in dcf_warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- No DCF warnings provided.")

    lines.extend(["", "#### DCF Source References", ""])
    source_references = dcf_output.get("source_references", [])
    if source_references:
        for source in source_references:
            lines.append(
                f"- {_metric_label(source)} ({source.get('period')}): "
                f"dated {source.get('source_date')} - {source.get('source_url')}"
            )
    else:
        lines.append("- No DCF source references provided.")

    return lines


def _fair_value_per_share_section_lines(fair_value_output: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "### Fair Value Per Share Model Calculation",
        "",
        f"- Disclaimer: {fair_value_output.get('disclaimer')}",
        f"- Currency: {fair_value_output.get('currency')}",
        "",
        "#### Scenario Calculations",
        "",
    ]

    for scenario in fair_value_output.get("scenarios", []):
        lines.append(f"- {scenario.get('scenario')}:")
        lines.append(f"  - Fair value per share: {scenario.get('fair_value_per_share')}")
        lines.append(f"  - DCF value used: {scenario.get('dcf_value_used')}")
        lines.append(f"  - Share count used: {scenario.get('share_count_used')}")
        lines.append(f"  - Share count metric ID: {scenario.get('share_count_metric_id')}")

    lines.extend(["", "#### Fair Value Per Share Formula", ""])
    for formula_name, formula in fair_value_output.get("formulas", {}).items():
        lines.append(f"- {formula_name}: {formula}")

    lines.extend(["", "#### Fair Value Per Share Warnings", ""])
    for warning in fair_value_output.get("warnings", []):
        lines.append(f"- {warning}")

    lines.extend(["", "#### Fair Value Per Share Source References", ""])
    for source in fair_value_output.get("source_references", []):
        lines.append(
            f"- {_metric_label(source)} ({source.get('period')}): "
            f"{source.get('source_type')} dated {source.get('source_date')} - {source.get('source_url')}"
        )

    return lines


def _model_rating_section_lines(model_rating_output: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "### Model Rating",
        "",
        f"- Disclaimer: {model_rating_output.get('disclaimer')}",
        f"- Rating: {model_rating_output.get('model_rating')}",
        f"- Label: {model_rating_output.get('rating_label')}",
        f"- Fair value per share used: {model_rating_output.get('fair_value_per_share_used')}",
        f"- Market price used: {model_rating_output.get('market_price_used')}",
        f"- Model gap percent: {model_rating_output.get('valuation_gap_percent')}",
        f"- Rules version: {model_rating_output.get('rules_version')}",
        "",
        "#### Model Rating Assumptions",
        "",
    ]
    for key, value in model_rating_output.get("assumptions", {}).items():
        label = "model_gap_formula" if key == "valuation_gap_formula" else key
        lines.append(f"- {label}: {value}")

    lines.extend(["", "#### Model Rating Warnings", ""])
    for warning in model_rating_output.get("warnings", []):
        lines.append(f"- {warning}")

    lines.extend(["", "#### Model Rating Source References", ""])
    for source in model_rating_output.get("source_references", []):
        lines.append(
            f"- {_metric_label(source)} ({source.get('period')}): "
            f"{source.get('source_type')} dated {source.get('source_date')} - {source.get('source_url')}"
        )
        lines.append(f"  - as_of_datetime: {source.get('as_of_datetime')}")
        lines.append(f"  - fetched_at: {source.get('fetched_at')}")

    return lines


def _model_rating_unavailable_lines(reasons: list[str]) -> list[str]:
    lines = ["", "### Model Rating", "", "- Status: unavailable"]
    if reasons:
        for reason in reasons:
            lines.append(f"- Reason: {reason}")
    return lines


def _model_confidence_section_lines(model_confidence_output: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "### Model Confidence",
        "",
        f"- Disclaimer: {model_confidence_output.get('disclaimer')}",
        f"- Confidence: {model_confidence_output.get('model_confidence')}",
        f"- Label: {model_confidence_output.get('confidence_label')}",
        f"- Score: {model_confidence_output.get('confidence_score')}",
        f"- Rules version: {model_confidence_output.get('rules_version')}",
        "",
        "#### Model Confidence Reasons",
        "",
    ]
    for reason in model_confidence_output.get("reasons", []):
        lines.append(f"- {reason}")

    lines.extend(["", "#### Model Confidence Warnings", ""])
    warnings = model_confidence_output.get("warnings", [])
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- No model confidence warnings provided.")

    lines.extend(["", "#### Model Confidence Source References", ""])
    source_references = model_confidence_output.get("source_references", [])
    if source_references:
        for source in source_references:
            lines.append(
                f"- {_metric_label(source)} ({source.get('period')}): "
                f"{source.get('source_type')} dated {source.get('source_date')} - {source.get('source_url')}"
            )
            if source.get("metric_category") == "market_price":
                lines.append(f"  - as_of_datetime: {source.get('as_of_datetime')}")
                lines.append(f"  - fetched_at: {source.get('fetched_at')}")
    else:
        lines.append("- No model confidence source references provided.")
    return lines


def _model_signal_section_lines(model_signal_output: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "### Model Signal",
        "",
        f"- Disclaimer: {model_signal_output.get('disclaimer')}",
        f"- Signal: {model_signal_output.get('model_signal')}",
        f"- Rules version: {model_signal_output.get('rules_version')}",
        "",
        "#### Model Signal Reasons",
        "",
    ]
    for reason in model_signal_output.get("reasons", []):
        lines.append(f"- {reason}")

    lines.extend(["", "#### Model Signal Blocking Reasons", ""])
    blocking_reasons = model_signal_output.get("blocking_reasons", [])
    if blocking_reasons:
        for reason in blocking_reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- No blocking reasons provided.")

    lines.extend(["", "#### Model Signal Inputs", ""])
    rating_used = model_signal_output.get("model_rating_used")
    confidence_used = model_signal_output.get("model_confidence_used")
    if isinstance(rating_used, dict):
        lines.append(f"- Model rating used: {rating_used.get('model_rating')}")
        lines.append(f"- Model gap percent used: {rating_used.get('valuation_gap_percent')}")
    else:
        lines.append("- Model rating used: unavailable")
    if isinstance(confidence_used, dict):
        lines.append(f"- Model confidence used: {confidence_used.get('model_confidence')}")
    else:
        lines.append("- Model confidence used: unavailable")

    lines.extend(["", "#### Model Signal Warnings", ""])
    warnings = model_signal_output.get("warnings", [])
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- No model signal warnings provided.")
    return lines


def _metric_label(source: dict[str, Any]) -> str:
    metric_name = source.get("metric_name")
    metric_id = source.get("metric_id")
    return f"{metric_name} [{metric_id}]" if metric_id else str(metric_name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a fact-only Markdown report for one ticker.")
    parser.add_argument("ticker")
    parser.add_argument("--validation-status-json", type=Path, required=True)
    parser.add_argument("--research-gaps-json", type=Path, required=True)
    parser.add_argument("--ratio-outputs-json", type=Path, required=True)
    parser.add_argument("--dcf-output-json", type=Path)
    parser.add_argument("--fair-value-per-share-json", type=Path)
    parser.add_argument("--model-rating-json", type=Path)
    parser.add_argument("--model-confidence-json", type=Path)
    parser.add_argument("--model-signal-json", type=Path)
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
            dcf_output=load_json(args.dcf_output_json) if args.dcf_output_json else None,
            fair_value_per_share_output=load_json(args.fair_value_per_share_json) if args.fair_value_per_share_json else None,
            model_rating_output=load_json(args.model_rating_json) if args.model_rating_json else None,
            model_confidence_output=load_json(args.model_confidence_json) if args.model_confidence_json else None,
            model_signal_output=load_json(args.model_signal_json) if args.model_signal_json else None,
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

