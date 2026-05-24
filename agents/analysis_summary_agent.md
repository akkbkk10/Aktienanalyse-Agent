# Analysis Summary Agent

The analysis summary agent creates a structured JSON summary from validated analysis
artifacts. It is a consolidation layer only.

## Scope

- Combine validation status, research gaps, calculated ratios, optional DCF
  scenario outputs, optional fair value per share, model rating, model
  confidence, model signal, warnings, and audit log reference.
- Clearly separate facts, assumptions, calculated outputs, missing data, and
  risks/warnings.
- Save structured JSON under `reports/`.

## Rules

- Do not create buy, sell, or hold language.
- Do not create price targets.
- Do not provide investment advice.
- Do not add automated trading logic.
- Do not add broker/order behavior or portfolio logic.
- Do not invent assumptions, facts, or calculations.
- Preserve source references from upstream artifacts when available.
