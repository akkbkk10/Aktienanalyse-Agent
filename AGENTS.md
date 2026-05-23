# Agent Rules

This repository is for a stock analysis agentic system. All agents, scripts, and generated reports must follow these rules.

## Evidence Rules

- No financial number may be stored, reported, or used unless it includes:
  - `source_url`
  - `source_date`
  - `unit`
  - `period`
  - `confidence`
- Separate facts, assumptions, and opinions. Do not mix them in one field.
- Separate GAAP and Non-GAAP metrics. Do not compare or combine them unless the difference is explicitly labeled.
- Cite the source for every factual claim used in downstream analysis.

## Implementation Rules

- Do not implement DCF, valuation, price target, or recommendation logic before schema validation and source validation exist.
- Every script must have tests.
- Fail closed when required evidence fields are missing.
- Keep raw input data in `data/` and generated outputs in `reports/`.

## Review Rules

- Open a pull request for every change.
- The pull request must include:
  - Summary of changes
  - Test results
  - Known limitations

