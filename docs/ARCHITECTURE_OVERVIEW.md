# Architecture Overview

The v0.1 system is a deterministic, evidence-first stock analysis workflow. It
separates facts, assumptions, calculations, reports, summaries, and audit records.

## Workflow

```text
validation -> context -> gaps -> ratios -> readiness -> DCF -> report -> summary -> audit log
```

## Stages

1. Source validation checks metric records for required evidence metadata.
2. Company context building converts validated metric records into persistent context.
3. Research gap detection compares context coverage with the watchlist.
4. Ratio calculation derives deterministic ratios from validated company context.
5. Valuation readiness checks source validity, gaps, required ratios, methodology config, audit writability, and prohibited outputs.
6. DCF calculation runs only after readiness passes and only from explicit assumptions.
7. Fact-only report generation creates a Markdown report with facts, missing data, warnings, and optional DCF calculation output.
8. Analysis summary generation creates structured JSON separating facts, assumptions, calculated outputs, missing data, and risks/warnings.
9. Audit logging records the reproducible analysis run.

## Boundary

The system does not produce buy/sell/hold recommendations, price targets,
investment advice, automated trading logic, or final investment memos.
