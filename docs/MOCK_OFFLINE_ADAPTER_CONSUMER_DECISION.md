# Mock / Offline Adapter Consumer Decision

This assessment determines whether a concrete first consumer exists for a
future mock or offline adapter after v1.1.8 and PR #123. It is documentation
only. It does not implement an adapter, runtime code, tests, schemas, config
changes, dependencies, generated reports, live data, provider APIs, MCP/A2A,
web UI, release notes, tags, or GitHub Releases.

## Executive Decision

Concrete first consumer: **no**.

The current repository is ready only for mock/offline adapter planning. The
deterministic core has strong enough source-validation, source-reference,
generated-output, and audit-log guardrails to evaluate an offline adapter
proposal later, but no concrete consumer or review gap currently requires an
adapter implementation.

Implementation should remain deferred until a proposal identifies a specific
consumer, fixture shape, validation path, audit expectation, and test plan.

## Why No Concrete Consumer Exists Yet

Current workflows already consume explicit input files:

- `scripts/run_analysis.py` accepts `--source-data-path` for one ticker and
  validates that file before rebuilding context, calculating ratios, producing
  optional artifacts, and writing the audit log.
- `scripts/run_batch_analysis.py` can process supported tickers independently
  from explicit source files or existing sample data.
- `scripts/run_v1_0_demo.py` exercises NVDA, AMD, and TSMC with deterministic
  sample data and generated artifacts under ignored `reports/` paths.
- `scripts/validate_sources.py` already validates financial metric records and
  stored market price snapshot fields.

Those paths are sufficient for current local validation, demo review,
generated-output contract coverage, and audit evidence checks. A mock/offline
adapter would currently duplicate the existing explicit-file handoff unless a
new consumer need is named.

## Candidate Consumer Paths Reviewed

| Candidate consumer | Current status | Decision |
| --- | --- | --- |
| `run_analysis.py` source-data input | Already consumes explicit source-data files and validates them before use. | Possible later, but no adapter needed now. |
| `run_batch_analysis.py` source-data mapping | Already routes explicit source files per ticker and isolates ticker failures. | Possible later, but no adapter needed now. |
| `run_v1_0_demo.py` sample workflow | Already exercises fixed NVDA, AMD, and TSMC sample data and output contracts. | Not a first adapter consumer. |
| `validate_sources.py` validation path | Already validates source records and market price snapshot fields. | Useful validation boundary, not an adapter consumer by itself. |
| External review workflow | No concrete external consumer, packaging need, or review gap is documented. | Defer. |

## Acceptable Offline / Mock Input Shape Later

If a concrete consumer appears, an offline adapter proposal may define a fixed
fixture shape that writes one of these explicit inputs:

- financial metric records compatible with `config/financial_metric_schema.json`
- stored market price snapshots compatible with
  `config/market_price_snapshot_schema.json`
- a source-data JSON file that `scripts/validate_sources.py` can validate
  before any downstream workflow consumes it

The adapter output should be treated as proposed input until source validation
passes. It should not bypass validation, mutate company contexts directly,
inject values into calculations, or set model outputs.

## Mandatory Evidence Fields

Any future offline adapter fixture or generated input file must preserve:

- `ticker`
- stable `metric_id`
- metric or snapshot name
- value
- unit
- currency, where applicable
- period, fiscal period, or observation period
- source URL or equivalent source reference
- source date, report date, filing date, `as_of_date`, or `as_of_datetime`
- provider or source identity where applicable
- retrieval method where applicable
- `fetched_at`, stored-at, or retrieval timestamp where applicable
- `last_verified`
- confidence
- validation status or validation result
- assumption or manual-review status where applicable

Market price snapshots must preserve the current stored-snapshot boundary and
must not imply live fetching.

## Required Tests Before Any Implementation

Before any adapter implementation PR, maintainers should identify focused tests
for:

- successful fixed offline fixture output
- validation failure when required source metadata is missing
- malformed value, unit, currency, period, source URL, source date, confidence,
  provider, or retrieval method
- stale or unavailable market price snapshot behavior where applicable
- proof that core workflows consume only validated files or snapshots
- audit-log traceability for adapter-fed source files
- generated-output source-reference preservation if summaries or reports are
  affected
- forbidden-output regression if any user-facing artifact changes
- full suite validation with `python -m unittest discover -s tests`
- v1.0 demo validation into an ignored `reports/tmp_*` path

If these tests require live network access, provider credentials, MCP/A2A
runtime, browser automation, or external services, the proposal is not ready.

## Smallest Safe Future PR Sequence

Use this sequence only after a concrete consumer exists:

1. **Consumer proposal**: name the consumer and explain why existing explicit
   source-file workflows are insufficient.
2. **Fixture and contract assessment**: document the offline input shape,
   required evidence fields, failure modes, audit expectations, and whether a
   schema or source-contract change is needed.
3. **Risk and decision record**: complete adapter risk and decision artifacts
   before implementation.
4. **Narrow implementation PR**: add only a mock/offline adapter with fixed
   fixtures and tests proving validation, traceability, fail-closed behavior,
   and no-advice guardrails.

## Explicitly Out Of Scope

This assessment does not add:

- runtime code
- tests
- schemas
- config files
- dependencies
- generated reports
- adapter implementation
- live data
- provider APIs
- external credentials
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

## Recommendation

Defer adapter implementation. The next adapter-related step should be a
consumer proposal only if a real user, review workflow, external system,
packaging flow, or reproducibility gap needs adapter-shaped offline input.
Without that concrete consumer, keep using explicit source-data files and the
existing deterministic validation path.
