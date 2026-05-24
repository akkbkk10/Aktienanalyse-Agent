# v1.0.1 Release Notes

## Status

v1.0.1 is a post-v1.0.0 maintenance and hardening release. It does not change
financial logic, DCF math, fair value logic, model rating behavior, model
confidence behavior, model signal behavior, sample company data, or generated
model calculations.

## Maintenance Summary

### PR #38: Repository Hygiene And CI Hardening

- Refreshed agent documentation/contracts for the v1.0.0 Hub-and-Spoke workflow.
- Clarified that `agents/` files are documentation/contracts, not runtime
  framework code.
- Added future adapter-layer wording for MCP, A2A, and framework integrations.
- Updated README examples with more platform-neutral path guidance.
- Extended CI coverage to validate TSMC sample data and run the v1.0 demo.
- Added local environment file ignores while keeping generated reports ignored.

### PR #39: Guardrail And Security Test Plan

- Added `docs/GUARDRAIL_SECURITY_TEST_PLAN.md`.
- Documented prohibited behaviors, including price targets, buy/sell/hold
  recommendations, personal investment advice, broker/order behavior,
  automated trading logic, invented sources, unsourced financial figures, and
  unvalidated live data fetching.
- Documented allowed behaviors, including deterministic calculations from
  explicit inputs, fact-only reports, missing-data reporting, manual-review
  assumptions, unavailable model signals, and audit-log writing.
- Mapped guardrails to existing modules, tests, docs, and generated artifacts.
- Added a checklist for future Market Data Agent, MCP, A2A, and framework
  adapter PRs.

### PR #40: Forbidden-Output Regression Tests

- Added generated-output regression tests for fact reports, structured
  summaries, fair value per share outputs, model rating outputs, model
  confidence outputs, and model signal outputs.
- Asserted generated user-facing artifacts do not contain explicit forbidden
  recommendation, advice, order, live-data, or invented-source phrases.
- Confirmed example/manual-review assumptions keep model confidence below `A`.
- Confirmed model signals remain `unavailable` when assumptions require manual
  review.
- Made one wording-only report boundary update to avoid forbidden-output
  phrasing in generated reports.

## Test Status

After PR #40, the local unit suite contains 182 tests.

Required validation commands:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_0_1_release_notes_demo
```

The v1.0 demo validates the deterministic workflow for NVDA, AMD, and TSMC and
writes generated artifacts under `reports/`, which remains ignored by git.

## Upgrade Notes From v1.0.0

No data migration is required. Users can upgrade from v1.0.0 to v1.0.1 by
pulling the release tag and continuing to run the same commands:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py
```

Generated reports, summaries, DCF outputs, fair value outputs, model ratings,
model confidence outputs, model signals, and audit logs remain compatible with
the v1.0.0 workflow.

## Explicit Non-Changes

v1.0.1 does not add or change:

- financial logic
- DCF math
- fair value per share logic
- model rating behavior
- model confidence behavior
- model signal behavior
- live data fetching
- new companies
- runtime agent code
- framework dependencies
- project naming
- price targets
- buy/sell/hold recommendations
- personal investment advice
- trading or portfolio logic
