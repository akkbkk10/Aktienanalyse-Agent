# Architecture Overview

The v1.0.0 system is a deterministic, evidence-first stock analysis workflow. It
separates facts, assumptions, calculations, reports, summaries, and audit records.

For a visual map of the current architecture, use
`docs/ARCHITECTURE_VISUAL_OVERVIEW.md`. For a local CLI acceptance check, use
`docs/LOCAL_USER_ACCEPTANCE_TEST.md`.

The architecture uses Hub-and-Spoke coordination: the orchestrator/supervisor
coordinates specialized worker scripts, while the deterministic Python core
remains framework-independent.

## Workflow

```text
validation -> context -> gaps -> ratios -> readiness -> DCF -> fair value per share -> model rating -> model confidence -> model signal -> report -> summary -> audit log
```

## Stages

1. Source validation checks metric records for required evidence metadata.
2. Company context building converts validated metric records into persistent context.
3. Research gap detection compares context coverage with the watchlist.
4. Ratio calculation derives deterministic ratios from validated company context.
5. Valuation readiness checks source validity, gaps, required ratios, methodology config, audit writability, and prohibited outputs.
6. DCF calculation runs only after readiness passes and only from explicit assumptions.
7. Fair value per share calculation divides existing DCF scenario values by sourced diluted share count metrics with `metric_id` traceability.
8. Model rating maps fair value per share versus sourced current market price to documented rating buckets.
9. Model confidence maps data quality, source freshness, research gaps, and assumption completeness to documented A-D quality grades.
10. Model signal maps existing model rating, model confidence, model gap, research gaps, and market price freshness to documented non-personalized signal labels.
11. Fact-only report generation creates a Markdown report with facts, missing data, warnings, and optional DCF, fair value per share, model rating, model confidence, and model signal output.
12. Analysis summary generation creates structured JSON separating facts, assumptions, calculated outputs, missing data, and risks/warnings.
13. Audit logging records the reproducible analysis run.

## Boundary

The system does not produce buy/sell/hold recommendations, price targets,
investment advice, automated trading logic, or final investment memos.

## Data Separation

Sample data lives under `data/` and `data/companies/<TICKER>/` for deterministic
tests and demos. Future live data ingestion must remain separate from sample data
so reproducible tests are not changed by current market or filing updates.

## Metric Traceability

Every sourced financial metric has a stable `metric_id`. Company contexts preserve
that identifier, ratio outputs list the input `metric_id` values used, and DCF
outputs include source-linked `metric_id` references where applicable. This keeps
technical traceability stable even when metric display names or report formatting
change.

Share count inputs use the same evidence model with `metric_category:
share_count`. They are loaded into company context as sourced facts and are used
only to calculate fair value per share from existing DCF scenario outputs.

Current market price inputs use `metric_category: market_price` and must include
the same source metadata fields as every other financial number. Model ratings
use these sourced market prices together with fair value per share outputs and
documented rules.

Model confidence uses `config/model_confidence_rules.json` to score existing
validated inputs only: source validation status, research gaps, stale data flags,
source confidence fields, DCF assumption completeness, and market price snapshot
freshness. It is model quality information, not a model signal.

Model signal uses `config/model_signal_rules.json` and existing model outputs
only. It can output `model_positive`, `model_neutral`, `model_negative`, or
`unavailable`. It becomes unavailable when model confidence is `D`, model rating
is unavailable, high-priority research gaps remain, or market price freshness
does not pass. It also becomes unavailable when assumption quality requires
manual review. It does not fetch live data or create broker/order actions.

## Market Price Snapshots

Market prices are stored snapshots, not live trading data. `as_of_datetime`
records the timestamp the price refers to, while `fetched_at` records when this
system stored or retrieved the snapshot. Validation enforces the snapshot
contract in `config/market_price_snapshot_schema.json`.

Snapshot freshness is checked only by `model_rating.py`. A stale or unavailable
market price makes model rating unavailable with reasons, but does not block
source validation, ratios, DCF, reports, summaries, or audit logging. Future live
fetching must be implemented through a separate Market Data Agent that writes
validated snapshots before downstream analysis runs.

## Ticker Independence

Each ticker is processed independently. A missing context, stale source, research
gap, or failed assumption file for one ticker must not block another ticker in the
same batch run. Batch output records successes, failures, output paths, and
warnings by ticker so NVDA, AMD, and TSMC cannot cross-block each other.

## Agent Contracts And Adapter Boundary

Files under `agents/` are documentation and role contracts for the
Hub-and-Spoke workflow. They are not runtime framework code. Future MCP, A2A,
LangChain, CrewAI, OpenAI Agents SDK, or other framework integrations belong in
adapter layers around the deterministic Python core. Adapter layers must
preserve source traceability, auditability, and all output guardrails.

## Output Safety

Model-generated reports, summaries, DCF outputs, and batch outputs are analysis
artifacts only. They are not personal investment advice and must not include
price targets, buy/sell/hold recommendations, or automated trading instructions.
Model confidence grades and model signal labels are allowed only as
non-personalized model outputs.
