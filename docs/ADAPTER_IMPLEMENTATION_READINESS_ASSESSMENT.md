# Adapter Implementation Readiness Assessment

This assessment reviews whether the current post-v1.1.8 repository is ready
for a future minimal adapter implementation path. It is documentation only. It
does not implement an adapter, live data fetching, runtime code, schemas,
config changes, tests, CLI behavior, dependencies, generated reports, release
notes, tags, or GitHub Releases.

## Executive Decision

Current readiness: **ready only for mock/offline adapter planning**.

The deterministic core now has enough source-validation, schema, generated
output, audit-log, and guardrail documentation to support planning a minimal
offline adapter boundary. It is not ready for live market data, external APIs,
MCP/A2A runtime integration, web UI integration, or provider-backed fetching.

The smallest safe future adapter path is a docs-first proposal for a mock or
offline adapter that writes fixed, validated input records or stored snapshots
for review. The deterministic core should continue to consume only explicit
files, validated records, and validated snapshots.

## Current Readiness Factors

The project is ready for mock/offline adapter planning because:

- `docs/ADAPTER_MARKET_DATA_BOUNDARY_RFC.md` keeps live fetching and adapter
  work outside the deterministic core.
- `docs/DATA_CONTRACT_REVIEW_CHECKLIST.md` defines field-level traceability
  expectations for future adapter outputs.
- `docs/SCHEMA_FIELD_REFERENCE.md` documents current source, snapshot,
  context, generated-output, and audit-log fields.
- `config/financial_metric_schema.json` and
  `config/market_price_snapshot_schema.json` define the current source and
  stored market price snapshot contracts.
- Generated JSON outputs have narrow contracts for DCF, fair value per share,
  model rating, model confidence, model signal, and analysis summary.
- `docs/AUDIT_LOG_EXPECTATIONS.md` documents the stable audit envelope while
  keeping nested diagnostics flexible.
- Current tests protect generated artifact layout, source-reference evidence,
  audit-log evidence, forbidden-output language, and CLI guardrail wording.

These controls are sufficient for planning a fixed-fixture adapter boundary.
They are not sufficient to skip proposal, risk, data-contract, decision-record,
and test planning before implementation.

## Required Boundaries Before Implementation

Any future first adapter implementation PR must preserve these boundaries:

- Adapter code stays outside deterministic core calculation, rating,
  confidence, signal, report, summary, and audit logic.
- The core receives adapter output only as explicit files, validated records,
  or validated snapshots.
- Existing source validation and snapshot validation are not bypassed.
- Adapter output must not directly set model rating, model confidence, model
  signal, report wording, DCF assumptions, fair value outputs, or audit status.
- Existing offline tests must not require network access, provider credentials,
  MCP servers, A2A peers, browser runtimes, or external APIs.
- Missing, stale, malformed, conflicting, low-confidence, or unavailable
  adapter output must fail closed as validation errors, unavailable states,
  warnings, or research gaps.

## Required Evidence Fields

Future adapter-provided financial records or snapshots should preserve these
fields unless a field is explicitly not applicable and the reason is
documented:

- `ticker`
- stable `metric_id` or snapshot identifier
- metric or instrument name
- value
- unit
- currency, where applicable
- period, fiscal period, or observation period
- source URL or equivalent source reference
- source date, report date, filing date, `as_of_date`, or `as_of_datetime`
- provider or source identity
- retrieval method
- retrieval, fetched, or stored timestamp where applicable
- confidence or quality signal
- validation status
- assumption or manual-review status where applicable

For market price snapshots, the current source of truth remains
`config/market_price_snapshot_schema.json`.

## Required Tests Before Any Adapter PR

A future adapter implementation proposal should list focused tests before code
is written. At minimum, the first adapter PR should plan for:

- fixed offline fixture tests for successful adapter output
- missing required metadata tests
- malformed value, unit, currency, period, and source-reference tests
- stale or unavailable snapshot tests where applicable
- fail-closed external-system failure tests, using mocks or fixtures only
- tests proving core modules consume only validated files or snapshots
- audit-log traceability tests for adapter-fed runs
- generated-output source-reference preservation tests if reports or summaries
  are affected
- forbidden-output regression coverage when user-facing artifacts are affected
- full suite validation with `python -m unittest discover -s tests`
- v1.0 demo validation into an ignored `reports/tmp_*` directory

If any proposed test requires live network access or credentials, the adapter
proposal is not ready for implementation.

## What Must Remain Out Of Scope

The first adapter path must not include:

- live market data fetching
- external API credentials
- provider-backed runtime requests
- MCP or A2A runtime integration
- web UI
- framework-specific business logic
- runtime dependencies in the deterministic core
- methodology configuration implementation
- generated artifact manifest implementation
- financial logic changes
- valuation formula changes
- model rating, confidence, or signal behavior changes
- generated report wording changes
- price targets
- buy/sell/hold recommendations
- personal investment advice
- broker/order behavior
- trading logic
- portfolio automation

## Smallest Safe Future PR Sequence

If maintainers decide to explore an adapter path later, use this sequence:

1. **Adapter proposal PR or issue**: define the mock/offline adapter purpose,
   exact input/output boundary, affected contracts, fixed fixture shape,
   failure modes, and non-goals.
2. **Risk and decision-record PR**: complete the adapter risk register and
   decision record before implementation.
3. **Narrow mock/offline adapter PR**: add only a fixture-backed adapter that
   writes explicit records or snapshots and focused tests proving validation,
   traceability, and fail-closed behavior.

Live data, provider credentials, MCP/A2A, web UI, and external APIs should
remain deferred until the mock/offline boundary proves useful and a concrete
consumer or review gap justifies a separate RFC.

## Readiness Recommendation

Recommendation: **implement later, starting only with mock/offline adapter
planning**.

Do not implement adapter runtime code now. The next safe adapter-related step,
if one is needed, is a focused proposal that names a concrete offline adapter
consumer, fixture format, validation path, audit expectation, and test plan.
Without that concrete need, adapter implementation should remain deferred.

## Explicitly Out Of Scope

This assessment does not add:

- runtime code
- tests
- schemas
- config files
- dependencies
- CLI behavior
- generated reports
- adapter implementation
- live data
- external APIs
- MCP, A2A, framework, or web UI implementation
- methodology implementation
- generated artifact manifest implementation
- financial logic
- valuation formulas
- model rating, model confidence, or model signal behavior
- report wording changes
- buy/sell/hold advice
- price targets
- trading logic
- portfolio automation
- personal investment advice
- release notes, tags, or GitHub Releases
