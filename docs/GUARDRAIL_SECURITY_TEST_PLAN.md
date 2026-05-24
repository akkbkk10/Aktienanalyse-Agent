# Guardrail And Security Test Plan

This document defines the post-v1.0 guardrail and security test plan for the
deterministic stock analysis core and any future agent or adapter layers.

The core rule is simple: business logic remains deterministic, source-traceable,
auditable, and framework-independent. Future adapters may orchestrate or connect
systems, but they must not bypass validation, invent data, fetch live data
outside an approved adapter contract, or create investment advice.

## Prohibited Behaviors

The system and any future adapter must not produce or perform:

- price targets
- buy/sell/hold recommendations
- personal investment advice
- broker/order behavior
- automated trading logic
- portfolio allocation logic
- invented sources
- unsourced financial figures
- live data fetching unless explicitly implemented and validated in a future
  adapter
- framework-specific business logic inside the deterministic core
- runtime dependencies on MCP, A2A, LangChain, LangGraph, CrewAI, OpenAI Agents
  SDK, Microsoft Agent Framework, NVIDIA NIM, RAPIDS, cuDF, NeMo, or similar
  frameworks in the core workflow

## Allowed Behaviors

The system may produce:

- deterministic calculations from explicit inputs
- sourced company context files
- research gaps and missing-data reports
- fact-only Markdown reports
- structured JSON summaries
- DCF scenario outputs from explicit assumptions
- fair value per share as calculated model output only
- model rating as non-personalized model output only
- model confidence as model quality information only
- model signal values limited to `model_positive`, `model_neutral`,
  `model_negative`, or `unavailable`
- `unavailable` model signals when assumptions are examples or require manual
  review
- audit-log records for reproducible runs

## Guardrail Map

| Guardrail | Primary modules | Tests | Output artifacts |
| --- | --- | --- | --- |
| Required source metadata for every financial number | `scripts/validate_sources.py`, `config/financial_metric_schema.json`, `config/source_rules.json` | `tests/test_validate_sources.py`, `tests/test_validate_company_onboarding.py` | validation JSON, research queue entries |
| No invented or unsourced financial figures | `scripts/validate_sources.py`, `scripts/build_company_context.py` | `tests/test_validate_sources.py`, `tests/test_build_company_context.py` | company context JSON |
| GAAP, Non-GAAP, IFRS, and Other basis separation | `scripts/validate_sources.py`, `config/financial_metric_schema.json` | `tests/test_validate_sources.py` | validation JSON, context metrics |
| Market price snapshots only, no live fetching in core | `config/market_price_snapshot_schema.json`, `scripts/model_rating.py` | `tests/test_market_price_snapshot.py`, `tests/test_model_rating.py` | model rating JSON |
| Example/manual-review assumptions reduce confidence | `scripts/model_confidence.py`, `config/model_confidence_rules.json` | `tests/test_model_confidence.py`, `tests/test_run_v1_0_demo.py` | model confidence JSON |
| Example/manual-review assumptions block active signals | `scripts/model_signal.py`, `scripts/model_confidence.py` | `tests/test_model_signal.py`, `tests/test_run_v1_0_demo.py` | model signal JSON, reports, summaries |
| No price targets or recommendation language | `scripts/generate_report.py`, `scripts/generate_analysis_summary.py`, model output scripts | `tests/test_generate_report.py`, `tests/test_generate_analysis_summary.py`, `tests/test_run_analysis.py`, `tests/test_end_to_end_analysis.py` | reports, summaries, model outputs |
| DCF only after readiness passes | `scripts/check_valuation_readiness.py`, `scripts/dcf_model.py`, `scripts/run_analysis.py` | `tests/test_check_valuation_readiness.py`, `tests/test_dcf_model.py`, `tests/test_workflow_order.py` | readiness JSON, DCF JSON |
| Audit log after workflow artifacts | `scripts/run_analysis.py`, `scripts/write_audit_log.py` | `tests/test_write_audit_log.py`, `tests/test_workflow_order.py`, `tests/test_run_v1_0_demo.py` | audit log JSONL |
| Ticker independence in batch runs | `scripts/run_batch_analysis.py` | `tests/test_run_batch_analysis.py` | batch JSON output |

## Required Validation Commands

Run these checks before merging guardrail, security, adapter, or workflow
changes:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_guardrail_security_plan_demo
```

For adapter proposals, also run any targeted tests that cover the touched module.
Generated artifacts must remain under `reports/` and must not be committed.

## Future Adapter PR Checklist

Use this checklist for Market Data Agent, MCP, A2A, or framework adapter PRs:

- The deterministic Python core remains framework-independent.
- Adapter code is isolated from core business logic.
- No adapter fetches live data unless the PR adds an explicit snapshot contract,
  validation rules, fixed tests, and docs.
- Market data is stored as validated snapshots before downstream analysis uses
  it.
- Every financial number still has `source_url`, `source_type`, `source_date`,
  `unit`, `period`, `confidence`, `last_verified`, and `metric_id` where
  applicable.
- Adapter failures fail closed and create clear errors or research gaps.
- Audit logs record source files and validation status for reproducibility.
- Reports and summaries remain fact-only and separate facts, assumptions,
  calculated outputs, missing data, and warnings.
- Model signals remain unavailable when assumptions require manual review.
- No price targets, buy/sell/hold recommendations, personal investment advice,
  broker/order behavior, automated trading logic, or portfolio logic is added.
- CI still runs the full unit suite and the v1.0 demo.

## Output Phrasing Examples

Disallowed phrasing:

- "The model sets a price target of X."
- "Buy this stock."
- "This is personal investment advice for your portfolio."
- "Submitting an order."
- "The system fetched the latest live quote directly in the DCF module."
- "Revenue is X" without source metadata.

Allowed phrasing:

- "Fair value per share is a calculated model output only, not investment
  advice."
- "Model signal is unavailable because assumptions require manual review."
- "The report lists missing data and source validation gaps."
- "Market price is a stored snapshot with `as_of_datetime` and `fetched_at`."
- "The audit log records validation status and source files used."

## Security Review Prompts

Before approving a PR, reviewers should ask:

- Can this change cause a financial number to appear without source metadata?
- Can this change bypass source validation, schema validation, or audit logging?
- Can this change produce recommendation-like wording?
- Can this change fetch or refresh live market data from inside core logic?
- Can this change move business logic into a framework adapter?
- Can this change make one ticker's failure block unrelated tickers in a batch?
- Can generated artifacts or local secrets be committed accidentally?
