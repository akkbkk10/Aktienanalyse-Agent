# v1.0.4 Release Notes

## Status

v1.0.4 is a post-v1.0.3 maintenance release focused on technical reference and
documentation-navigation improvements. It does not change application logic,
financial logic, DCF math, fair value logic, model rating behavior, model
confidence behavior, model signal behavior, generated report wording, sample
company data, schemas, or generated model calculations.

v1.0.4 does not add schema changes, live fetching, adapters, runtime agent code,
framework dependencies, project renaming, package publishing, or CLI behavior
changes.

## Maintenance Summary

### PR #54: Core Baseline Inventory

- Added `docs/CORE_BASELINE_INVENTORY.md`.
- Documented the current deterministic workflow stages, module responsibilities,
  test coverage areas, generated artifacts, supported sample companies, market
  price snapshot governance, and guardrails.
- Identified possible future v1.1 improvement candidates without implementing
  them or committing to a roadmap.

### PR #55: Schema Field Reference

- Added `docs/SCHEMA_FIELD_REFERENCE.md`.
- Documented current deterministic core data contracts for financial metric
  records, market price snapshot records, company context records, DCF
  assumptions, DCF outputs, fair value per share outputs, model rating outputs,
  model confidence outputs, model signal outputs, and audit log records.
- Distinguished formal schemas from current observed output structures where no
  formal schema exists yet.

### PR #56: Architecture Governance Index

- Added `docs/ARCHITECTURE_GOVERNANCE_INDEX.md`.
- Added a navigation-only index for maintainers choosing between baseline,
  schema, guardrail, generated-output, adapter proposal, data-contract, risk
  register, decision record, and patch release workflow documents.
- Documented the recommended order for future adapter-related proposal work
  without creating new process requirements.

### PR #57: README Documentation Map

- Reorganized README documentation links into a compact Documentation Map.
- Grouped links by current baseline, validation and guardrails, data contracts
  and schemas, generated-output review, adapter and architecture governance,
  maintainer/release workflow, and open-source contribution/security.
- Preserved setup, test, demo, workflow, and release-note links while reducing
  repeated documentation lists.

## Test Status

The local unit suite contains 182 tests.

Required validation commands:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_0_4_release_notes_demo
```

The v1.0 demo validates the deterministic workflow for NVDA, AMD, and TSMC and
writes generated artifacts under `reports/`, which remains ignored by git.

## Upgrade Notes From v1.0.3

No data migration is required. Users can upgrade from v1.0.3 to v1.0.4 by
pulling the release tag and continuing to run the same workflow commands:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py
```

v1.0.4 improves maintainability through the core baseline inventory, schema
field reference, architecture governance navigation, and README documentation map
cleanup. Existing generated reports, summaries, DCF outputs, fair value outputs,
model ratings, model confidence outputs, model signals, and audit logs remain
compatible with v1.0.3.

## Explicit Non-Changes

v1.0.4 does not add or change:

- application logic
- financial logic
- DCF math
- fair value per share logic
- model rating behavior
- model confidence behavior
- model signal behavior
- generated report wording
- schemas
- live data fetching
- new companies
- runtime agent code
- adapters
- MCP integration
- A2A integration
- framework dependencies
- project naming
- package publishing
- CLI behavior
- price targets
- buy/sell/hold recommendations
- personal investment advice
- trading or portfolio logic
