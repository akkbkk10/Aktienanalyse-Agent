# Architecture Overview

The v0.1 system is a deterministic, evidence-first stock analysis workflow. It
separates facts, assumptions, calculations, reports, summaries, and audit records.

## Workflow

```text
validation -> context -> gaps -> ratios -> readiness -> DCF -> fair value per share -> model rating -> report -> summary -> audit log
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
9. Fact-only report generation creates a Markdown report with facts, missing data, warnings, and optional DCF, fair value per share, and model rating output.
10. Analysis summary generation creates structured JSON separating facts, assumptions, calculated outputs, missing data, and risks/warnings.
11. Audit logging records the reproducible analysis run.

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

## Market Price Snapshots

Market prices are stored snapshots, not live trading data. Snapshot records must
match `config/market_price_snapshot_schema.json` and pass source validation before
they can reach company context or model rating.

No valuation or reporting module may call a live market data API directly. A
future Market Data Agent may retrieve live prices, but it must write validated
snapshot records first. Tests use fixed snapshots so reproducible workflows are
not affected by changing market data.

## Ticker Independence

Each ticker is processed independently. A missing context, stale source, research
gap, or failed assumption file for one ticker must not block another ticker in the
same batch run. Batch output records successes, failures, output paths, and
warnings by ticker so NVDA and AMD cannot cross-block each other.

## Output Safety

Model-generated reports, summaries, DCF outputs, and batch outputs are analysis
artifacts only. They are not personal investment advice and must not include model
confidence labels, model signals, price targets, buy/sell/hold
recommendations, or automated trading instructions.
