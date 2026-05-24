# Data Contract / Schema Hardening Assessment

This assessment reviews the current v1.0.9/v1.1 preparation baseline for data
contracts, schemas, validation scripts, sample data, and related tests. It is a
documentation-only assessment. It does not change schemas, sample data, runtime
logic, tests, CI, generated artifacts, or release behavior.

## Source Files Inspected

- `AGENTS.md`
- `README.md`
- `docs/V1_1_CANDIDATE_PLAN.md`
- `docs/REPORT_ARTIFACT_CONTRACT.md`
- `docs/SCHEMA_FIELD_REFERENCE.md`
- `docs/DATA_CONTRACT_REVIEW_CHECKLIST.md`
- `docs/ARCHITECTURE_GOVERNANCE_INDEX.md`
- `config/financial_metric_schema.json`
- `config/market_price_snapshot_schema.json`
- `config/source_rules.json`
- `config/dcf_assumptions_schema.json`
- `config/watchlist.json`
- `data/nvda_sample_metrics.json`
- `data/amd_sample_metrics.json`
- `data/tsmc_sample_metrics.json`
- `data/companies/<TICKER>/context.json`
- `data/companies/<TICKER>/dcf_assumptions.json`
- `scripts/validate_sources.py`
- `scripts/build_company_context.py`
- `scripts/validate_company_onboarding.py`
- `tests/test_validate_sources.py`
- `tests/test_build_company_context.py`
- `tests/test_validate_company_onboarding.py`
- `tests/test_run_v1_0_demo.py`

## Current Data-Contract Baseline

The deterministic core already has a strong fail-closed source-data baseline.
Raw financial metric records are governed by `config/financial_metric_schema.json`
and `config/source_rules.json`, then validated by `scripts/validate_sources.py`.
The schema requires `metric_id`, ticker, metric name, value, unit, period,
accounting basis, statement type, source URL, source type, source date,
last-verified date, and confidence. The validator also rejects unexpected
fields, invalid enum values, invalid date formats, non-HTTPS source URLs, stale
`last_verified` values, and conflicting values for the same ticker, metric,
period, and accounting basis.

Market price inputs are treated as stored snapshots, not live quotes.
`config/market_price_snapshot_schema.json` requires ticker, `metric_id`, value,
currency, exchange, price type, `as_of_datetime`, `fetched_at`, source URL,
source date, provider, retrieval method, confidence, and `last_verified`.
`scripts/validate_sources.py` applies the snapshot schema to records marked as
`market_price`, while downstream model rating and model confidence logic handle
snapshot freshness without turning stale market prices into a source-validation
failure.

Company context files are built by `scripts/build_company_context.py` from
validated source records. The builder preserves `metric_id`, metric name, value,
unit, period, accounting basis, statement type, optional metric category, market
price snapshot fields where present, notes, and nested source metadata. It also
validates required top-level context fields and per-metric source metadata.
This structure is documented in `docs/SCHEMA_FIELD_REFERENCE.md` as current
observed structure rather than a standalone formal schema.

DCF assumptions are governed by `config/dcf_assumptions_schema.json`, a custom
validation contract rather than a JSON Schema object. The onboarding validator
checks required assumption fields, required bear/base/bull scenarios, required
scenario fields, and source references with `metric_id`, metric name, period,
source URL, source date, and confidence.

Watchlist coverage is maintained in `config/watchlist.json` and checked during
research gap detection and company onboarding validation. The current sample
tickers are `NVDA`, `AMD`, and `TSMC`.

Generated report artifacts are now documented separately in
`docs/REPORT_ARTIFACT_CONTRACT.md`. The v1.0 demo smoke tests verify that the
shared audit log and per-ticker report/model artifacts are written under the
configured reports directory.

## Protection Map

| Data area | Current contract | Current protection |
| --- | --- | --- |
| Financial metric sample data | `config/financial_metric_schema.json`, `config/source_rules.json` | `scripts/validate_sources.py`, `tests/test_validate_sources.py`, CI source validation for NVDA/AMD/TSMC |
| Source/evidence fields | `AGENTS.md`, `config/source_rules.json` | Required evidence checks, URL/date/confidence/freshness tests |
| Market price snapshots | `config/market_price_snapshot_schema.json`, `config/source_rules.json` | Snapshot field validation tests, model rating/confidence freshness tests |
| Company context files | `scripts/build_company_context.py`, current observed structure in `docs/SCHEMA_FIELD_REFERENCE.md` | Builder validation, context preservation tests, onboarding context-generation check |
| DCF assumptions | `config/dcf_assumptions_schema.json` | Onboarding DCF assumption checks, DCF model tests |
| Watchlist config | `config/watchlist.json` | Research gap tests, onboarding watchlist check, CI JSON validation |
| Generated artifacts | `docs/REPORT_ARTIFACT_CONTRACT.md` | `tests/test_run_v1_0_demo.py` custom reports-directory artifact checks |

## Concrete Validation Gaps

No urgent source-data validation gap was found for the current sample metrics:
the raw financial metric records, source evidence fields, market price snapshot
fields, share count records, and DCF assumption inputs are already covered by
schemas or validator checks.

The concrete hardening gap identified by this assessment has been partially
addressed:

- **Company context files now have standalone schema/contract protection.**
  `config/company_context_schema.json` formalizes the current top-level context
  fields, per-metric fields, and nested source metadata fields already produced
  by `scripts/build_company_context.py`. Focused tests validate the committed
  NVDA, AMD, and TSMC context files against that contract.

This partially closes the gap because the context handoff is now protected by a
durable config file and tests. It does not attempt to formalize every generated
JSON output schema, which remains broader follow-up work.

## Nice-To-Have Improvements For Later

These are useful, but broader than the next safe PR:

- Formal schemas for generated JSON outputs such as DCF output, fair value per
  share output, model rating output, model confidence output, and model signal
  output.
- Converting `config/dcf_assumptions_schema.json` from a custom validation
  contract into a full JSON Schema object.
- Stable machine-readable error codes for validation failures.
- A generated artifact manifest file. The current report artifact contract and
  smoke tests already protect paths and required files, so this should wait
  until a concrete consumer needs it.

## Recommended Next Implementation PR

Recommend exactly one next implementation block:

**Generated output schema assessment.**

Small safe scope:

- Review the current generated JSON artifacts documented in
  `docs/REPORT_ARTIFACT_CONTRACT.md` and `docs/SCHEMA_FIELD_REFERENCE.md`.
- Identify whether one narrow generated output, such as DCF output or fair
  value per share output, needs standalone schema protection next.
- Keep the first pass assessment-only unless a specific missing guardrail is
  found.
- Do not change calculations, model behavior, generated report wording, CLI
  behavior, or adapter boundaries.

Why this should be next:

- The raw source data, market price snapshots, and company context handoff now
  have explicit contract protection.
- Generated JSON outputs are still documented mainly as current observed
  structure.
- Assessment-first keeps this from expanding into a broad output-schema rewrite.

## Not Recommended Yet

Do not build these as part of the next data-contract hardening PR:

- live market data fetching
- Market Data Agent implementation
- MCP, A2A, LangGraph, or framework adapter implementation
- new companies
- web UI
- package rename or publishing
- price targets
- buy/sell/hold recommendations
- personal investment advice
- trading, broker/order, or portfolio logic

Those areas should remain in proposal/RFC mode until the company context
contract and generated artifact review expectations are stable.
