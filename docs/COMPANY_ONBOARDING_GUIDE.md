# Company Onboarding Guide

Use this checklist when adding a new supported ticker such as TSMC, ASML, MSFT,
or AAPL. Do not add live fetching, price targets, personal investment advice, or
trading logic as part of company onboarding.

## Files To Add

Create:

- `data/<ticker_lower>_sample_metrics.json`
- `data/companies/<TICKER>/dcf_assumptions.json`
- `data/companies/<TICKER>/context.json`

Update:

- `config/watchlist.json`

Templates are available in:

- `data/company_template/sample_metrics_template.json`
- `data/company_template/dcf_assumptions_template.json`

## Required Source Data

Every metric record must include:

- `metric_id`
- `ticker`
- `company`
- `metric_name`
- `metric_category`
- `value`
- `unit`
- `period`
- `source_type`
- `source_url`
- `source_date`
- `confidence`
- `last_verified`
- `accounting_basis`
- `statement_type`

Required onboarding metrics:

- `Revenue`
- `Net income`
- `Free cash flow`
- a `share_count` metric
- a `market_price` snapshot metric

Market price snapshots must include:

- `currency`
- `exchange`
- `price_type`
- `as_of_datetime`
- `fetched_at`
- `provider`
- `retrieval_method`

## DCF Assumptions

Add `data/companies/<TICKER>/dcf_assumptions.json` with:

- `schema_version`
- `ticker`
- `unit`
- `source_references`
- `bear`, `base`, and `bull` scenarios
- `discount_rate`, `terminal_growth_rate`, `starting_free_cash_flow`, and
  `forecast_years` for each scenario

Assumptions must be explicit example assumptions. They must not be invented by an
agent during validation.

## Watchlist

Add the ticker to `config/watchlist.json` with:

- `company_name`
- `required_metrics`
- `max_last_verified_age_days`
- `minimum_confidence`

## Validate The Package

Run:

```powershell
python scripts\validate_company_onboarding.py TICKER --metrics-path data\ticker_sample_metrics.json --dcf-assumptions-path data\companies\TICKER\dcf_assumptions.json
```

The validator checks source validation, required metrics, `metric_id` presence,
source metadata, market price snapshot fields, share count availability, DCF
assumptions, watchlist entry, and company context generation.

After it passes, rebuild context:

```powershell
python scripts\build_company_context.py data\ticker_sample_metrics.json
```

Then run the existing workflow for the ticker:

```powershell
python scripts\run_analysis.py TICKER --generate-report --generate-summary --run-dcf
```
