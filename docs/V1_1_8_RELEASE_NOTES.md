# v1.1.8 Release Notes Candidate

## Status

v1.1.8 release notes are prepared, but v1.1.8 has not been tagged or
published yet. The latest published release remains v1.1.7 until maintainers
tag and publish v1.1.8 after final validation.

v1.1.8 is an evidence, source-reference, audit-log, and guardrail
documentation hardening candidate for the deterministic Aktienanalyse-Agent
core.

This candidate covers PR #118 through PR #120. It does not add runtime code,
financial logic, valuation formula changes, model behavior changes, schemas,
config changes, generated reports, adapters, live data, methodology
configuration implementation, generated artifact manifest implementation,
MCP/A2A integration, web UI, advice, price targets, trading, or portfolio
automation.

## Release Summary

### PR #118: Harden Demo Source Reference Coverage

- Expanded v1.0 demo regression coverage so generated NVDA, AMD, and TSMC
  artifacts preserve current source-reference evidence fields.
- Covered source-reference evidence in generated DCF output, fair value per
  share output, model rating output, model confidence output, and analysis
  summary JSON artifacts.
- Protected existing evidence fields such as metric identifiers, metric names,
  periods, units, source URLs, source types, source dates, last-verified dates,
  confidence values, and market price snapshot fields where applicable.
- Preserved runtime behavior, generated wording, schemas, config files,
  financial calculations, model behavior, and report artifacts.

### PR #119: Harden Audit Log Evidence Coverage

- Added orchestrator audit-log regression coverage for source files used,
  data context path, validation status, and nested ratio source-reference
  evidence.
- Verified that audit records preserve `source_metric_references` fields for
  ratio outputs without adding a standalone audit log schema.
- Kept audit-log nested diagnostics intentionally flexible, consistent with
  `docs/AUDIT_LOG_EXPECTATIONS.md`.
- Preserved runtime behavior, audit-log generation behavior, schemas, config
  files, financial calculations, and generated reports.

### PR #120: Sync Evidence Coverage Documentation

- Updated guardrail, generated-output, report-artifact, and audit-log
  documentation so documented evidence coverage matches PR #118 and PR #119.
- Corrected stale test-map wording that referenced nonexistent market-price
  source-reference coverage.
- Clarified that current evidence hardening covers generated JSON artifacts and
  audit-log evidence visibility without implementing live data, adapters,
  generated artifact manifests, methodology configuration behavior, schemas, or
  runtime changes.
- Preserved docs-only scope.

## Durable Files Added Or Updated

v1.1.8 adds or updates these durable files:

- `docs/V1_1_8_RELEASE_NOTES.md`
- `README.md`
- `docs/GUARDRAIL_SECURITY_TEST_PLAN.md`
- `docs/AUDIT_LOG_EXPECTATIONS.md`
- `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md`
- `docs/REPORT_ARTIFACT_CONTRACT.md`
- `tests/test_run_v1_0_demo.py`
- `tests/test_run_analysis.py`

## Test Status

The local unit suite contains 231 tests.

Validation command:

```bash
python -m unittest discover -s tests
```

Result: 231 tests OK.

## Maintainer Validation Before Tagging

Before creating a `v1.1.8` tag, maintainers should:

1. Use a fresh checkout of `main` after this release-note PR is merged.
2. Confirm the working tree is clean:

```bash
git status --short --branch
```

3. Run the full unit suite:

```bash
python -m unittest discover -s tests
```

4. Run the demo validation required by the existing release process:

```bash
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_1_8_release_validation
```

5. Confirm generated reports remain ignored and the working tree is clean.
6. Create the `v1.1.8` tag only after the release-note PR is merged to `main`
   and validation passes.

Follow `docs/RELEASE_AND_TAG_GOVERNANCE.md` and
`docs/V1_0_X_PATCH_RELEASE_CHECKLIST.md` for tag and GitHub Release handling.

## Explicit Non-Changes

v1.1.8 does not add or change:

- runtime analysis behavior
- financial logic
- valuation formulas
- DCF behavior
- fair value per share behavior
- model rating behavior
- model confidence behavior
- model signal behavior
- analysis report wording
- generated report content
- schemas
- config files
- dependencies
- generated reports committed to the repository
- adapters
- live data
- MCP or A2A integration
- web UI
- methodology configuration implementation
- generated artifact manifest implementation
- buy/sell/hold advice
- price targets
- trading logic
- portfolio automation
- personal investment advice

Generated artifact manifest implementation, adapter/live-data implementation,
methodology configuration implementation, MCP/A2A, web UI, new financial logic,
and new companies remain future work and are not part of v1.1.8.
