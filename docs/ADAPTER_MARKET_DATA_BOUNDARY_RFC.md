# Adapter / Market Data Boundary RFC

This RFC documents the boundary between the deterministic core and any future
Market Data Agent, adapter, MCP, A2A, framework, or web UI layer.

It is documentation only. It does not implement an adapter, live fetching,
runtime code, schemas, tests, CLI behavior, dependencies, generated reports,
release notes, tags, or GitHub Releases.

## Executive Recommendation

Keep market data and adapter work outside the deterministic core until a future
proposal completes the existing adapter, data-contract, guardrail, risk, and
decision-record reviews.

Future adapters may fetch, import, translate, or orchestrate external data, but
the deterministic core should consume only explicit inputs, validated records, or
validated snapshots. Live fetching must not be added directly to core analysis
modules.

## Current Boundary

The current stable architecture is a deterministic, evidence-based core:

- source validation reads explicit input records
- company context, ratios, DCF, fair value per share, model rating, model
  confidence, model signal, reports, summaries, and audit logs run from explicit
  files and structured artifacts
- market prices are stored snapshots, not live trading data
- generated outputs remain analysis artifacts only, not investment advice

The core must not:

- call market data APIs
- read provider credentials for fetching market data
- refresh live prices inside calculation, rating, confidence, signal, report,
  summary, orchestrator, or batch modules
- move financial, valuation, rating, confidence, signal, reporting, summary, or
  audit business logic into an adapter or framework layer
- create price targets, buy/sell/hold recommendations, personal investment
  advice, broker/order behavior, automated trading, or portfolio automation

## Future Adapter Role

A future Market Data Agent or adapter may be considered only as a boundary layer.
Its job would be to produce reviewable inputs for the deterministic core, not to
replace the core.

A future adapter may:

- fetch or import data from an approved provider
- translate provider responses into explicit records
- write validated market data snapshots or other input files
- record retrieval and provenance metadata
- fail closed when provider data is missing, stale, malformed, rate limited, or
  unavailable

A future adapter must not:

- inject values directly into calculations
- bypass source validation, schema validation, freshness rules, or audit logging
- directly set model rating, model confidence, or model signal outcomes
- hide live values inside report, summary, DCF, fair value, rating, confidence,
  or signal modules
- require network access for the existing offline test suite

## Snapshot Expectations

Future market data snapshots should remain immutable records of what was
observed, imported, or retrieved. At a high level, a snapshot should preserve:

- source or source reference
- fetched timestamp, retrieval timestamp, or stored-at timestamp
- observation date or `as_of_datetime`
- units and currency, where applicable
- period, instrument, exchange, venue, or price type, where applicable
- provider name
- retrieval method
- source URL or equivalent source reference
- confidence or quality signal
- freshness rules and stale-data behavior
- validation status or validation evidence
- enough provenance for audit logs and generated outputs to trace the value

For market price data, the existing stored-snapshot contract in
`config/market_price_snapshot_schema.json` is the current source of truth.
Future snapshot changes should go through the schema and data-contract review
process before implementation.

## Freshness Handling

Freshness rules should be explicit and should not silently refresh values inside
core analysis modules.

Future adapter work should preserve these principles:

- a stale snapshot remains a visible state, not an implicit live refresh
- stale or missing market price snapshots should fail closed in the specific
  downstream stages that require fresh market price data
- unrelated deterministic stages should continue to run when their required
  explicit inputs are valid
- generated reports and summaries should remain clear about missing, stale, or
  unavailable market data

Current model rating, model confidence, and model signal behavior already treats
market price freshness as a controlled input. Future adapter work should not
weaken that boundary.

## Implementation Prerequisites

Before any future Market Data Agent or adapter implementation PR, maintainers
should complete:

1. `docs/ADAPTER_PROPOSAL_CHECKLIST.md`
2. `docs/DATA_CONTRACT_REVIEW_CHECKLIST.md`
3. `.github/ISSUE_TEMPLATE/schema_change_proposal.md`, if a schema,
   source-schema, snapshot-format, or adapter contract change is needed
4. `docs/ADAPTER_RISK_REGISTER_TEMPLATE.md`
5. `docs/ADAPTER_DECISION_RECORD_TEMPLATE.md`
6. guardrail review using `docs/GUARDRAIL_SECURITY_TEST_PLAN.md`
7. generated-output review planning using `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`

The proposal should define:

- the provider or external system
- the exact data crossing the adapter boundary
- required source metadata and snapshot fields
- validation behavior for missing, malformed, stale, conflicting, or low-quality
  data
- failure modes and fail-closed behavior
- secret handling and credential boundaries
- audit-log and generated-output traceability
- tests that use fixed fixtures or mocked adapter output instead of live network
  calls
- how the deterministic core continues to run without the adapter

## Later Adapter Topics

MCP, A2A, framework adapters, web UI, and live market-data ingestion remain later
adapter topics. They should wrap the deterministic core through explicit inputs
and outputs rather than becoming core business logic.

Those topics should not be treated as implementation tasks until a focused RFC,
data-contract review, risk review, and decision record are complete.

## Classification

This boundary is architecture governance, not a generated-output contract.

- Classification: Adapter / Market Data Boundary RFC
- Current recommendation: defer implementation until a concrete provider,
  consumer, or review gap justifies it
- Smallest safe future step, if needed: open a focused adapter proposal that
  defines the provider, snapshot contract impact, fixture plan, failure modes,
  and guardrail tests before any runtime code is added

## Explicitly Out Of Scope

This RFC does not add:

- adapter implementation
- Market Data Agent implementation
- live fetching
- MCP, A2A, framework, or web UI implementation
- runtime code
- tests
- schemas or validators
- CLI behavior
- generated artifact manifest implementation
- generated reports
- methodology or financial logic changes
- new companies
- investment advice, price targets, buy/sell/hold recommendations, trading
  logic, or portfolio automation
- release notes, tags, or GitHub Releases
