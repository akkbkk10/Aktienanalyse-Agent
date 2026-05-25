# v1.1.3 Release Notes

## Status

v1.1.3 is a generated-output governance and contract hardening release for the
deterministic Aktienanalyse-Agent core. It completes the audit-log expectations
and analysis-summary output contract block that followed v1.1.2.

This release does not add new financial behavior, new calculations, live data
fetching, adapters, framework integrations, web UI, investment advice, or
trading logic.

The deterministic workflow remains focused on NVDA, AMD, and TSMC sample data
with source validation, company context generation, research gaps, ratios,
valuation readiness, DCF, fair value per share, model rating, model confidence,
model signal, fact-only reports, structured summaries, and audit logs.

## Release Summary

### PR #94: Audit Log Schema Need Assessment

- Added `docs/AUDIT_LOG_SCHEMA_NEED_ASSESSMENT.md`.
- Reviewed actual generated `audit_log.jsonl` output from the v1.0 demo.
- Identified stable top-level audit envelope fields, including `timestamp`,
  `ticker`, `methodology_version`, `data_context_path`, `source_files_used`,
  `validation_status`, `ratio_outputs`, `research_gaps_detected`, and
  `git_commit_hash`.
- Identified flexible diagnostic payloads that should not be over-constrained,
  including validation errors, ratio details, source references, research-gap
  details, platform-specific paths, timestamps, and commit hash values.
- Recommended documenting audit log expectations without standalone schema
  enforcement.

### PR #95: Audit Log Expectations

- Added `docs/AUDIT_LOG_EXPECTATIONS.md`.
- Documented `audit_log.jsonl` as a shared operational/audit artifact, not a
  per-ticker report artifact.
- Documented the stable audit log envelope already protected by existing
  `write_audit_log` validation and tests.
- Kept nested diagnostics intentionally flexible.
- Clarified when a future standalone audit log schema could become justified.

### PR #96: Analysis Summary Schema Need Assessment

- Added `docs/ANALYSIS_SUMMARY_SCHEMA_NEED_ASSESSMENT.md`.
- Reviewed actual generated `analysis_summary.json` outputs for NVDA, AMD, and
  TSMC.
- Confirmed the current report-facing envelope is stable across generated demo
  summaries: `ticker`, `generated_at`, `audit_log_reference`, `facts`,
  `assumptions`, `calculated_outputs`, `missing_data`, and `risks_warnings`.
- Identified stable section fields for future contract protection.
- Identified flexible explanatory and diagnostic fields, including embedded
  upstream output internals, source-reference details, warning text,
  research-gap details, blocker wording, timestamps, paths, and audit
  references.
- Recommended a narrow analysis summary output schema/contract.

### PR #97: Analysis Summary Output Schema / Contract

- Added `config/analysis_summary_output_schema.json`.
- Added analysis summary output validation in
  `scripts/generate_analysis_summary.py`.
- Protected the required report-facing envelope and stable section fields for
  generated `analysis_summary.json` artifacts.
- Kept embedded DCF, fair value per share, model rating, model confidence, and
  model signal internals flexible and governed by their own contracts.
- Kept warning text, research-gap details, reason/blocker wording, timestamps,
  paths, source-reference details, and audit references flexible.
- Added analysis summary contract tests for valid output, missing required
  top-level fields, invalid required top-level field types, missing required
  section fields, nullable optional upstream outputs, and generated NVDA, AMD,
  and TSMC demo summaries.

## Durable Files Added Or Updated

v1.1.3 adds or updates these durable generated-output contract and governance
files:

- `docs/AUDIT_LOG_SCHEMA_NEED_ASSESSMENT.md`
- `docs/AUDIT_LOG_EXPECTATIONS.md`
- `docs/ANALYSIS_SUMMARY_SCHEMA_NEED_ASSESSMENT.md`
- `config/analysis_summary_output_schema.json`
- `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md`
- `docs/SCHEMA_FIELD_REFERENCE.md`
- `docs/ARCHITECTURE_GOVERNANCE_INDEX.md`
- `README.md`

## Test Status

The local unit suite contains 229 tests.

Focused validation commands:

```bash
python -m unittest tests.test_generate_analysis_summary
python -m unittest tests.test_run_v1_0_demo
python -m unittest tests.test_forbidden_output_regression
```

Full test suite command:

```bash
python -m unittest discover -s tests
```

Relevant contract JSON validation commands:

```bash
python -m json.tool config/analysis_summary_output_schema.json
python -m json.tool config/model_signal_output_schema.json
python -m json.tool config/model_confidence_output_schema.json
python -m json.tool config/model_rating_output_schema.json
python -m json.tool config/dcf_output_schema.json
python -m json.tool config/fair_value_per_share_output_schema.json
```

v1.0 demo validation command:

```bash
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_1_3_release_notes_demo
```

The demo validates the deterministic workflow for NVDA, AMD, and TSMC and
writes generated artifacts under the configured `reports/` path, which remains
ignored by git.

## Maintainer Validation Before Tagging

Before creating the `v1.1.3` tag:

1. Use a fresh clone or fresh checkout of `main` after this release-note PR is
   merged.
2. Confirm the working tree is clean:

```bash
git status --short --branch
```

3. Run the full unit suite:

```bash
python -m unittest discover -s tests
```

4. Validate relevant JSON schema files:

```bash
python -m json.tool config/analysis_summary_output_schema.json
python -m json.tool config/model_signal_output_schema.json
python -m json.tool config/model_confidence_output_schema.json
python -m json.tool config/model_rating_output_schema.json
python -m json.tool config/dcf_output_schema.json
python -m json.tool config/fair_value_per_share_output_schema.json
```

5. Run the demo validation required by the existing release process:

```bash
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_1_3_release_validation
```

6. Confirm generated reports remain ignored and the working tree is clean.
7. Create the `v1.1.3` tag only after the release-note PR is merged to `main`
   and validation passes.

Follow `docs/RELEASE_AND_TAG_GOVERNANCE.md` and
`docs/V1_0_X_PATCH_RELEASE_CHECKLIST.md` for tag and GitHub Release handling.

## Upgrade Notes From v1.1.2

No data migration is required. Existing v1.1.2 sample inputs remain compatible.
Generated reports, summaries, audit logs, and model artifacts continue to be
written under ignored `reports/` paths.

Users can upgrade by pulling the v1.1.3 release and running:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py
```

Maintainers should continue future generated-output hardening with the next
narrow candidate only after an assessment confirms that a standalone contract
adds value beyond existing validators, review docs, and tests.

## Explicit Non-Changes

v1.1.3 does not add or change:

- financial logic
- DCF math
- fair value per share calculation logic
- model rating thresholds or behavior
- model confidence scoring, thresholds, labels, or generated wording
- model signal gating rules, enum values, labels, or generated wording
- generated report wording
- CLI behavior
- CI behavior
- sample company financial values
- live market data fetching
- new companies
- runtime agent code
- adapters
- MCP integration
- A2A integration
- framework dependencies
- web UI
- project naming
- package publishing
- release tags
- GitHub UI settings automation
- price targets
- buy/sell/hold recommendations
- personal investment advice
- trading, broker/order, or portfolio logic

Fact report schema assessment, audit log schema implementation, generated
artifact manifests, adapters, live fetching, and new companies remain future
work and are not part of v1.1.3.
