# v1.0 Release Notes

## Status

v1.0 is a release candidate for real user testing of the deterministic stock
analysis workflow.

## Supported Sample Companies

- NVDA
- AMD
- TSMC

## Included Workflow

The v1.0 demo runs the existing batch workflow for all supported sample
companies:

1. Source validation
2. Company context build/load
3. Research gap detection
4. Ratio calculation
5. Valuation readiness check
6. DCF calculation from explicit assumptions
7. Fair value per share calculation from DCF output and sourced share count
8. Model rating from fair value per share and validated market price snapshot
9. Model confidence from deterministic quality rules
10. Model signal from deterministic rating/confidence rules
11. Fact-only report generation
12. Structured analysis summary generation
13. Audit log writing

## Generated Artifacts

`python scripts/run_v1_0_demo.py` writes generated artifacts under
`reports/v1_0_demo/`, including:

- ticker-level reports
- ticker-level summaries
- ticker-level DCF outputs
- ticker-level fair value per share outputs
- ticker-level model rating outputs
- ticker-level model confidence outputs
- ticker-level model signal outputs
- shared audit log

Generated artifacts under `reports/` are ignored by git.

## Known Boundaries

This release candidate does not include:

- live data fetching
- new companies beyond NVDA, AMD, and TSMC
- new valuation logic beyond the existing deterministic modules
- price targets
- buy/sell/hold recommendations
- personal investment advice
- broker/order behavior
- automated trading logic

## User Testing Focus

Reviewers should focus on:

- source traceability and `metric_id` preservation
- clarity of fact, assumption, calculated output, missing data, and warning
  separation
- audit log reproducibility
- deterministic batch behavior across independent tickers
- absence of prohibited recommendation, advice, live-fetching, and trading
  behavior
