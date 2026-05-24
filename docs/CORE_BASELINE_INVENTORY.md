# Core Baseline Inventory

This document is a technical assessment of the deterministic core after the
v1.0.0 baseline and the v1.0.1 through v1.0.3 hardening releases. It is not a
product roadmap commitment and does not approve any future feature by itself.

## Supported Sample Companies

The current deterministic sample set is:

- NVDA
- AMD
- TSMC

Each ticker has sourced sample metrics, a persistent company context, DCF
assumptions, market price snapshot inputs, report/summary support, and batch
workflow coverage.

## Deterministic Core Workflow

The current workflow is:

```text
validation -> context -> gaps -> ratios -> readiness -> DCF -> fair value per share -> model rating -> model confidence -> model signal -> report -> summary -> audit log
```

Workflow stages:

1. Source validation checks required evidence metadata and schema rules.
2. Company context creation preserves sourced metrics and source metadata.
3. Research gap detection compares company context against watchlist coverage.
4. Ratio calculation derives deterministic ratios from validated input metrics.
5. Valuation readiness checks whether valuation is allowed to proceed.
6. DCF calculation uses explicit assumptions only.
7. Fair value per share uses DCF scenario outputs and sourced share count.
8. Model rating compares fair value per share with validated market price
   snapshots.
9. Model confidence scores data quality, freshness, gaps, and assumption
   completeness.
10. Model signal maps rating, confidence, gaps, and market price freshness to
    non-personalized signal labels.
11. Fact-only report generation creates Markdown artifacts.
12. Analysis summary generation creates structured JSON artifacts.
13. Audit logging records reproducible run metadata.

## Module Responsibility Map

| Script or config | Responsibility |
| --- | --- |
| `scripts/validate_sources.py` | Validates source records, required metadata, source rules, market price snapshot fields, stale source metadata, and conflicts. |
| `scripts/create_research_request.py` | Creates structured and Markdown research queue entries with duplicate prevention. |
| `scripts/build_company_context.py` | Builds persistent company contexts while preserving metrics, source metadata, `metric_id`, and market price snapshot fields. |
| `scripts/detect_research_gaps.py` | Detects missing, stale, low-confidence, and incomplete research coverage from watchlist rules. |
| `scripts/calculate_ratios.py` | Calculates basic deterministic ratios and preserves source metric references. |
| `scripts/validate_methodology.py` | Validates methodology configuration before valuation stages. |
| `scripts/check_valuation_readiness.py` | Gates valuation based on validation, gaps, ratios, methodology, audit writability, and prohibited outputs. |
| `scripts/dcf_model.py` | Calculates deterministic DCF scenarios from explicit assumptions only. |
| `scripts/fair_value_per_share.py` | Calculates fair value per share from DCF outputs and sourced share count metrics. |
| `scripts/model_rating.py` | Calculates non-personalized model rating from fair value per share and validated market price snapshots. |
| `scripts/model_confidence.py` | Calculates A-D model quality confidence from existing validated inputs and rule config. |
| `scripts/model_signal.py` | Calculates non-personalized model signal or `unavailable` from rating, confidence, gaps, and freshness rules. |
| `scripts/generate_report.py` | Generates fact-only Markdown reports with separated facts, missing data, warnings, model outputs, and source references. |
| `scripts/generate_analysis_summary.py` | Generates structured JSON summaries separating facts, assumptions, calculations, missing data, and risks/warnings. |
| `scripts/write_audit_log.py` | Writes append-only JSONL audit records for reproducible runs. |
| `scripts/run_analysis.py` | Orchestrates one or more ticker workflows with optional DCF, report, summary, and model output stages. |
| `scripts/run_batch_analysis.py` | Runs independent per-ticker workflows and returns structured batch status. |
| `scripts/run_v1_0_demo.py` | Runs the full deterministic NVDA, AMD, and TSMC demo workflow. |
| `scripts/validate_company_onboarding.py` | Checks new-company onboarding packages for required data, context, watchlist, assumptions, and market price snapshot coverage. |
| `config/financial_metric_schema.json` | Defines the core metric record contract, including metric categories. |
| `config/market_price_snapshot_schema.json` | Defines required market price snapshot fields. |
| `config/source_rules.json` | Defines source validation rules, allowed source types, and market price snapshot freshness. |
| `config/model_rating_rules.json` | Defines rating bucket rules. |
| `config/model_confidence_rules.json` | Defines confidence scoring rules. |
| `config/model_signal_rules.json` | Defines signal rules and blocking behavior. |

## Test Protection Map

| Tests | Protected workflow areas |
| --- | --- |
| `tests/test_validate_sources.py` | Source metadata, source rules, market price snapshot validation, conflict detection, sample data validation. |
| `tests/test_build_company_context.py` | Context creation, missing required inputs, source metadata preservation, `metric_id` preservation. |
| `tests/test_detect_research_gaps.py` | Missing metrics, stale metrics, low confidence, no-gap behavior. |
| `tests/test_calculate_ratios.py` | Ratio calculations, missing inputs, zero revenue protection, source traceability, no valuation output. |
| `tests/test_validate_methodology.py` | Methodology config fields, scenarios, discount rules, version presence. |
| `tests/test_check_valuation_readiness.py` | Valuation readiness blockers, stale data, high-priority gaps, invalid methodology, prohibited language. |
| `tests/test_dcf_model.py` | DCF assumptions, readiness gate, invalid rates, scenario output, no recommendation language. |
| `tests/test_fair_value_per_share.py` | Fair value per share calculation, share count traceability, invalid share count, prohibited language. |
| `tests/test_model_rating.py` | Rating buckets, market price snapshot requirements, stale snapshot blocking, no external API calls, prohibited language. |
| `tests/test_model_confidence.py` | Confidence A-D behavior, stale market price deductions, high-priority gaps, assumption quality gates. |
| `tests/test_model_signal.py` | Signal buckets, unavailable behavior, stale market price blocking, no recommendation/advice language. |
| `tests/test_generate_report.py` | Report creation, source references, DCF/model output sections, prohibited language, timestamp preservation. |
| `tests/test_generate_analysis_summary.py` | Structured summary sections, DCF/model output inclusion, missing DCF handling, timestamp preservation. |
| `tests/test_run_analysis.py` | Orchestrator modes, DCF/report/summary/model outputs, stale market price behavior, audit integration. |
| `tests/test_run_batch_analysis.py` | Single and multi-ticker batch behavior, partial failures, output structure. |
| `tests/test_end_to_end_analysis.py` | Full NVDA workflow structure. |
| `tests/test_run_v1_0_demo.py` | Full NVDA, AMD, and TSMC demo behavior. |
| `tests/test_workflow_order.py` | Required workflow ordering. |
| `tests/test_forbidden_output_regression.py` | Generated user-facing artifacts avoid recommendation, advice, order, live-data, and invented-source phrases. |
| `tests/test_validate_company_onboarding.py` | New-company package completeness, market price snapshot, share count, assumptions, watchlist, context generation. |
| `tests/test_write_audit_log.py` | Audit record required fields and append-only behavior. |

## Generated Artifacts

| Artifact | Purpose |
| --- | --- |
| `reports/<TICKER>/<TICKER>_fact_report.md` | Fact-only Markdown report with validation status, gaps, ratios, source references, optional valuation/model outputs, warnings, and audit reference. |
| `reports/<TICKER>/<TICKER>_analysis_summary.json` | Structured JSON summary separating facts, assumptions, calculated outputs, missing data, and risks/warnings. |
| `reports/<TICKER>/<TICKER>_dcf_output.json` | Deterministic DCF scenario output from explicit assumptions. |
| `reports/<TICKER>/<TICKER>_fair_value_per_share_output.json` | Fair value per share scenarios using DCF outputs and sourced share count. |
| `reports/<TICKER>/<TICKER>_model_rating_output.json` | Non-personalized model rating from fair value per share and validated market price snapshot. |
| `reports/<TICKER>/<TICKER>_model_confidence_output.json` | A-D model quality confidence with reasons, warnings, and source references. |
| `reports/<TICKER>/<TICKER>_model_signal_output.json` | Non-personalized model signal or `unavailable` with blocking reasons. |
| `reports/<run>/audit_log.jsonl` | Append-only audit records for reproducible analysis runs. |
| `research_queue.json` and `research_queue.md` | Structured and human-readable research gap queues. |

Generated runtime artifacts should remain under ignored `reports/` paths and
should not be committed.

## Market Price Snapshot Governance

Current market price support is already governed in the deterministic core:

- Market price records use `metric_category: market_price`.
- `config/market_price_snapshot_schema.json` requires ticker, `metric_id`,
  value, currency, exchange, price type, `as_of_datetime`, `fetched_at`, source
  URL, source date, provider, retrieval method, confidence, and `last_verified`.
- `config/source_rules.json` defines `market_price_snapshot_max_age_days`.
- `scripts/validate_sources.py` validates snapshot shape and required fields.
- `scripts/build_company_context.py` preserves snapshot fields in company
  context.
- `scripts/model_rating.py` requires validated snapshot fields and blocks model
  rating when market price is missing, invalid, or stale.
- `scripts/model_confidence.py` lowers confidence for missing or stale market
  price snapshots.
- `scripts/model_signal.py` returns `unavailable` when market price freshness
  blocks signal interpretation.
- `scripts/generate_report.py` and `scripts/generate_analysis_summary.py`
  preserve market price timestamp references where model outputs use them.

Primary test coverage:

- `tests/test_validate_sources.py`
- `tests/test_model_rating.py`
- `tests/test_model_confidence.py`
- `tests/test_model_signal.py`
- `tests/test_generate_report.py`
- `tests/test_generate_analysis_summary.py`
- `tests/test_run_analysis.py`
- `tests/test_validate_company_onboarding.py`

No valuation, rating, report, summary, or orchestrator module may fetch live
market data directly. Future live fetching belongs in a separate Market Data
Agent adapter that writes validated snapshot records before the deterministic
core consumes them.

## Guardrails

Current guardrails prohibit:

- price targets
- buy/sell/hold recommendations
- personal investment advice
- broker/order behavior
- automated trading or portfolio logic
- invented sources
- unsourced financial figures
- unvalidated live data fetching
- framework-specific business logic inside the deterministic core

Primary guardrail docs and tests:

- `AGENTS.md`
- `docs/GUARDRAIL_SECURITY_TEST_PLAN.md`
- `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`
- `tests/test_forbidden_output_regression.py`
- prohibited-language checks in report, summary, DCF, fair value, rating,
  confidence, signal, readiness, orchestrator, and demo tests

## v1.1 Readiness Gaps And Improvement Candidates

These are possible improvement areas for future review. They are not roadmap
commitments.

### Core Reliability

- Add a compact machine-readable workflow manifest so orchestrator outputs can
  be compared against expected stage order without duplicating expectations.
- Add focused regression tests for generated audit-log references in batch runs.
- Consider smoke tests for each sample ticker as independent named test cases,
  while preserving the existing full demo test.

### CLI Usability

- Add clearer `--help` examples for common commands if command-line ergonomics
  becomes a priority.
- Consider consistent output paths and status messages across scripts.
- Consider a single validation command that wraps source, config, and sample
  data checks without changing core behavior.

### Data-Contract/Schema Hardening

- Review whether schema files should include documented examples or companion
  fixtures for every metric category.
- Consider a non-runtime schema documentation table that maps required fields
  by category: financial metric, share count, and market price.
- Review whether validation error output should include stable error codes for
  easier automation.

### Documentation Cleanup

- Add a governance index that explains when to use each architecture-governance
  document and issue template.
- Review README length and decide whether advanced workflows should move into
  dedicated docs.
- Align release-note links and maintainer docs into one release section.

### Future Adapter Preparation

- Use `docs/ADAPTER_PROPOSAL_CHECKLIST.md`,
  `docs/ADAPTER_RISK_REGISTER_TEMPLATE.md`,
  `docs/ADAPTER_DECISION_RECORD_TEMPLATE.md`, and
  `docs/DATA_CONTRACT_REVIEW_CHECKLIST.md` before any adapter implementation.
- Keep future Market Data Agent work outside the deterministic core until it
  writes validated snapshot records.
- Require fixed offline fixtures for any adapter tests.

## Recommended Small PR Candidates

1. Add `docs/ARCHITECTURE_GOVERNANCE_INDEX.md` to explain when maintainers
   should use each governance checklist, template, and issue workflow.
2. Add docs-only schema field tables for financial metrics, share counts, and
   market price snapshots, derived from the existing schema expectations.
3. Add a small CLI help cleanup PR for command examples, with no behavior
   changes.

These candidates should each remain small, independently reviewable, and bound
by the existing guardrails.
