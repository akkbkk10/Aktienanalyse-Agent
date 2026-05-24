# v1.1.0 Release Notes

## Status

v1.1.0 is a contract and schema hardening release for the deterministic
Aktienanalyse-Agent core. It formalizes artifact and data contracts that were
already part of the v1.0.x workflow. It does not add new financial behavior,
new calculations, live data fetching, adapters, framework integrations,
investment advice, or trading logic.

The deterministic workflow remains focused on NVDA, AMD, and TSMC sample data
with source validation, company context generation, research gaps, ratios,
valuation readiness, DCF, fair value per share, model rating, model confidence,
model signal, fact-only reports, structured summaries, and audit logs.

## Release Summary

### PR #74: v1.1 Candidate Plan

- Added `docs/V1_1_CANDIDATE_PLAN.md`.
- Documented the post-v1.0.9 baseline and recommended a small contract/schema
  hardening sequence.
- Kept live market data, web UI, adapters, MCP/A2A, package rename, trading,
  and portfolio logic out of scope.

### PR #75: Report Artifact Contract

- Added `docs/REPORT_ARTIFACT_CONTRACT.md`.
- Documented the current v1.0 demo artifact layout under the configured
  `reports/` directory.
- Listed required per-ticker artifacts for fact reports, analysis summaries,
  DCF outputs, fair value per share outputs, model rating outputs, model
  confidence outputs, model signal outputs, and the shared audit log.

### PR #76: Data Contract / Schema Hardening Assessment

- Added `docs/DATA_CONTRACT_SCHEMA_HARDENING_ASSESSMENT.md`.
- Mapped current source-data schemas, market price snapshot rules, company
  context behavior, DCF assumptions, watchlist config, generated artifacts, and
  existing validation coverage.
- Identified company context contract protection as the next concrete hardening
  candidate.

### PR #77: Company Context Schema / Contract

- Added `config/company_context_schema.json`.
- Added standalone validation for persistent `data/companies/<TICKER>/context.json`
  files.
- Protected the current intended company context fields without changing sample
  financial data or downstream analysis behavior.

### PR #78: Generated Output Schema Assessment

- Added `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md`.
- Assessed generated JSON artifact schema candidates.
- Recommended DCF output as the first narrow generated-output contract target.

### PR #79: DCF Output Schema / Contract

- Added `config/dcf_output_schema.json`.
- Added contract validation for generated DCF outputs, including calculated
  outputs and blocked outputs.
- Protected current DCF output fields without changing DCF math, assumptions,
  formulas, or generated report wording.

### PR #80: Fair Value Per Share Output Schema / Contract

- Added `config/fair_value_per_share_output_schema.json`.
- Added contract validation for generated fair value per share outputs.
- Protected current fair value output fields without changing fair value
  calculation logic, DCF behavior, model rating, model confidence, or model
  signal behavior.

## Durable Contracts Added

v1.1.0 adds or documents these durable contracts:

- `docs/REPORT_ARTIFACT_CONTRACT.md`
- `config/company_context_schema.json`
- `config/dcf_output_schema.json`
- `config/fair_value_per_share_output_schema.json`

The existing `docs/SCHEMA_FIELD_REFERENCE.md`,
`docs/DATA_CONTRACT_SCHEMA_HARDENING_ASSESSMENT.md`, and
`docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md` describe how these contracts fit
into the deterministic core.

## Test Status

The local unit suite contains 203 tests.

Focused validation commands:

```bash
python -m unittest tests.test_build_company_context
python -m unittest tests.test_dcf_model
python -m unittest tests.test_fair_value_per_share
python -m unittest tests.test_run_v1_0_demo
```

Full test suite command:

```bash
python -m unittest discover -s tests
```

Contract JSON validation commands:

```bash
python -m json.tool config/company_context_schema.json
python -m json.tool config/dcf_output_schema.json
python -m json.tool config/fair_value_per_share_output_schema.json
```

v1.0 demo validation command:

```bash
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_1_0_release_notes_demo
```

The demo validates the deterministic workflow for NVDA, AMD, and TSMC and
writes generated artifacts under the configured `reports/` path, which remains
ignored by git.

## Upgrade Notes From v1.0.9

No data migration is required. Existing v1.0.9 sample inputs remain compatible.
Generated reports and model artifacts continue to be written under ignored
`reports/` paths.

Users can upgrade by pulling the v1.1.0 release and running:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py
```

Maintainers should review future data-contract or generated-output changes
against the new contract files and the generated-output review guide before
merging broader schema work.

## Explicit Non-Changes

v1.1.0 does not add or change:

- financial logic
- DCF math
- fair value per share calculation logic
- model rating behavior
- model confidence behavior
- model signal behavior
- generated report wording
- CLI behavior
- CI workflow behavior
- sample company financial values
- live data fetching
- new companies
- runtime agent code
- adapters
- MCP integration
- A2A integration
- framework dependencies
- project naming
- package publishing
- price targets
- buy/sell/hold recommendations
- personal investment advice
- trading, broker/order, or portfolio logic

Model rating, model confidence, model signal, audit log, analysis summary, and
fact report schema hardening remain future work and are not part of v1.1.0.
