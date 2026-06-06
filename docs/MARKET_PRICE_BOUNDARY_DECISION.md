# Market Price Boundary Decision

## Purpose

This document records the project boundary for `market_price` records in the
deterministic Aktienanalyse-Agent core. It clarifies when market-price evidence
is required, when it may be optional in a future PR, and what evidence is
required before any market-price snapshot can be accepted.

This is a documentation decision only. It does not change runtime behavior,
schemas, tests, source data, model rating, model signal, DCF logic, adapters,
live data fetching, or generated output semantics.

## Decision

Market price is a separate stored snapshot boundary. It is not the same data
class as annual-report, SEC, or investor-relations financial statement facts.

The deterministic core must not fetch, refresh, infer, or silently update market
prices. The core may consume only explicit market-price snapshot records that
are static, timestamped, provider-labeled, sourceable, and manually verifiable.

Current default behavior remains protected:

- `market_price` is required for full onboarding readiness.
- `market_price` is required for full model rating availability.
- `market_price` is required for downstream model signal availability whenever
  model signal depends on model rating.
- The onboarding validator reports model readiness separately from source-only
  and DCF-ready support tiers.

Optional-market-price behavior is limited to lower readiness tiers:

- `market_price` may be omitted for `source_only` onboarding checks.
- `market_price` may be omitted for `dcf_ready` onboarding checks.
- Model rating and downstream model signal remain unavailable when no validated
  market-price snapshot is present.
- No-live-data, no-advice, no-price-target, and no-trading guardrails still
  apply.

## Data Classes

### Financial Statement Facts

Financial statement facts are source-package data. They usually come from
annual reports, SEC filings, investor-relations materials, or earnings releases.
Examples include revenue, net income, free cash flow, operating income, gross
profit, and share-count facts when sourced from official reporting material.

These records must preserve source metadata, including `source_url`,
`source_date`, `unit`, `period`, `confidence`, `last_verified`, accounting
basis, statement type, and stable `metric_id` values.

### DCF Assumptions

DCF assumptions are not financial statement facts. They are explicit assumptions
stored separately from source-package facts. They must be labeled as
assumptions, must not be invented by runtime code, and must not contain
recommendation, price-target, trading, or personal-advice wording.

### Market Price Snapshots

Market price snapshots are static observations of a market price at a specific
time. They are a separate boundary because they may come from market-data
providers, exchange pages, manually reviewed files, or future adapter output.

A market-price snapshot must be reproducible enough for a reviewer to understand
what price was captured, for which instrument, from which provider or source, at
which timestamp, and when the project stored or verified it.

### Generated Outputs

Generated outputs include reports, analysis summaries, DCF outputs, fair value
per share outputs, model ratings, model confidence outputs, model signals,
audit logs, contexts, and research queues.

Generated outputs are artifacts, not source data. They must not be committed
when produced under local trial paths, and they must not be used as replacement
evidence for financial facts or market-price snapshots.

## Support Tiers

### Source-Only Onboarding

Source-only onboarding means a company source package can pass source validation
for financial statement facts and required evidence fields.

Use the onboarding validator's `source_only` support tier for this check.
`market_price` is not required for this tier, but model rating and model signal
readiness remain false without a validated market-price snapshot.

### Ratio-Ready

Ratio-ready means the project has enough validated financial statement facts to
build company context and calculate supported ratios.

Market price is not conceptually required for ratio-only workflows, because
ratios are calculated from source financial facts. Use source validation and the
`source_only` onboarding tier to validate this lower readiness layer.

### DCF-Ready

DCF-ready means the project has validated source facts, required ratios, valid
methodology configuration, explicit DCF assumptions, and readiness-gate approval
for deterministic DCF scenarios.

Market price is not conceptually required for DCF-only trials, because DCF
scenarios run from explicit assumptions and source facts. Use the onboarding
validator's `dcf_ready` support tier to validate this layer.

### Model-Rating-Ready

Model-rating-ready requires a validated market-price snapshot. Model rating
compares fair value per share output with a sourced current market price, so it
must remain unavailable when market price is missing, malformed, stale, or
unverifiable.

### Model-Signal-Ready

Model-signal-ready requires the upstream model outputs needed by the signal
rules, including model rating when the signal depends on rating. Because model
rating requires a validated market-price snapshot, model signal must remain
unavailable when the required market-price evidence is missing, stale, or
invalid.

## Required Metadata For `market_price`

A repo-safe market-price snapshot must include:

- `ticker`
- `metric_id`
- `value`
- `currency`
- `unit`
- `exchange`
- `price_type`
- `as_of_datetime`
- `fetched_at` or `captured_at`
- `provider`
- `retrieval_method`
- `source_url`
- `source_date`
- `last_verified`
- `confidence`

Current schema fields use `fetched_at`. A future schema or adapter proposal may
rename or alias this to `captured_at`, but only through a separate schema or
data-contract PR.

## What Is Not Acceptable

The following are not acceptable market-price evidence for repo-final data:

- a ChatGPT answer as the market-price source
- an unstamped homepage quote
- a non-reproducible manual snapshot
- a live fetch by deterministic core modules
- an undocumented provider or API result
- a source without timestamp, provider, exchange, instrument, currency, or
  confidence metadata
- a generated report, summary, context, or audit log used as primary market
  evidence

If the market-price source cannot be reproduced or manually verified, leave
model rating and model signal unavailable instead of committing the snapshot.

## Current Behavior Vs Future Behavior

Current behavior:

- `validate_company_onboarding.py` defaults to `full`, which requires a
  market-price snapshot.
- `validate_company_onboarding.py --support-tier source_only` can pass without
  a market-price snapshot when lower-tier source checks pass.
- `validate_company_onboarding.py --support-tier dcf_ready` can pass without a
  market-price snapshot when DCF-ready checks pass.
- `model_rating.py` requires a current market-price record and blocks model
  rating when it is missing, invalid, or stale.
- `model_signal.py` returns `unavailable` when model rating is unavailable or
  when market-price freshness checks fail.
- Core modules do not fetch live market data.

## ASML Implication

ASML can remain a successful local offline trial when local metrics,
assumptions, and watchlist entries are present and validation passes.

ASML should not be committed as repo sample data until the official source
review standard is satisfied. If model rating or model signal availability is
intended, the ASML package also needs repo-safe market-price evidence that meets
this decision: static, timestamped, provider-labeled, sourceable, and manually
verifiable.

If ASML source facts are otherwise ready but market-price evidence is not
repo-safe, a future ASML PR should either defer ASML promotion or explicitly
scope ASML to source-only, ratio-only, or DCF-only readiness.

## Explicit Non-Goals

This decision does not add:

- runtime code
- tests
- schemas
- config changes
- ASML source data
- generated reports
- generated contexts
- source-material review copies
- market data adapters
- live data fetching
- provider API integration
- dependencies
- web UI
- desktop app behavior
- MCP/A2A runtime integration
- model rating behavior changes
- model signal behavior changes
- DCF logic changes
- financial logic changes
- buy/sell/hold advice
- price targets
- trading logic
- portfolio automation
- personal investment advice
- release tags
- GitHub Releases
