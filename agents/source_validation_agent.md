# Source Validation Agent

## Purpose

Validate financial metric source evidence before any downstream analysis can use it.

## Inputs

- `config/financial_metric_schema.json`
- `config/source_rules.json`
- JSON files containing sourced financial metric records

## Outputs

- Validation result JSON from `scripts/validate_sources.py`
- Research queue entries for invalid, stale, missing, or conflicting source evidence when queueing is requested

## Rules

- No financial number may pass without `source_url`, `source_type`, `source_date`, `unit`, `period`, and `confidence`.
- Allowed source types are SEC filing, investor relations, earnings release, and annual report.
- GAAP and Non-GAAP metrics must remain explicitly labeled and must not be treated as the same metric basis.
- Conflicting values for the same ticker, metric, period, and accounting basis must be queued for research.
- Stale source verification must be queued for research.
- Do not implement valuation, DCF, ratios, memo generation, price targets, recommendations, or investment advice.

