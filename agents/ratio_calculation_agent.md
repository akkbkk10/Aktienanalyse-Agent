# Ratio Calculation Agent

## Purpose

Calculate basic deterministic financial ratios from validated company context metrics.

## Inputs

- `data/companies/<TICKER>/context.json`

## Outputs

- JSON ratio records from `scripts/calculate_ratios.py`
- Research queue entries for missing required ratio inputs

## Allowed Ratios

- `gross_margin`
- `operating_margin`
- `net_margin`
- `free_cash_flow_margin`
- `revenue_growth` only when prior-period revenue exists

## Rules

- Use only validated company context metrics.
- Every ratio must include ticker, ratio name, value, formula, input metrics used, source metric references, period, and confidence.
- Do not divide by zero revenue.
- Missing required ratio inputs must create research queue entries.
- Do not implement valuation, DCF, fair value, price targets, recommendations, memo generation, or investment advice.

