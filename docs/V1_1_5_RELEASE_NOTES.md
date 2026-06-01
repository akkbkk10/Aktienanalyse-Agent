# v1.1.5 Release Notes

## Status

v1.1.5 is a generated-output governance and demo-stability maintenance
release for the deterministic Aktienanalyse-Agent core. It documents the
generated artifact manifest assessment and the v1.0 demo freshness-date
stabilization merged in PR #102.

Publication status: v1.1.5 has been tagged and published from commit
`a3f702e`.

This release does not add a generated artifact manifest, manifest schema,
manifest validator, CLI option, or committed generated reports.

The deterministic workflow remains focused on NVDA, AMD, and TSMC sample data
with source validation, company context generation, research gaps, ratios,
valuation readiness, DCF, fair value per share, model rating, model confidence,
model signal, fact-only reports, structured summaries, and audit logs.

## Release Summary

### PR #102: Generated Artifact Manifest Assessment

- Added `docs/GENERATED_ARTIFACT_MANIFEST_ASSESSMENT.md`.
- Assessed whether the project should introduce a persisted generated artifact
  manifest for report bundles.
- Documented the current state: no persisted manifest exists, while
  `run_analysis`, `run_batch_analysis`, and `run_v1_0_demo` already expose
  generated artifact path metadata.
- Documented possible manifest purpose, benefits, risks, candidate artifacts,
  possible stable fields, flexible fields, lifecycle, and ownership.
- Classified a possible manifest as **Run Metadata / Operational Artifact**,
  not as a Report Contract and not as an audit log replacement.
- Recommended **defer**. A manifest should wait until a concrete consumer,
  review workflow, adapter, packaging workflow, or release validation gap
  requires persisted run metadata.
- Updated `README.md`, `docs/ARCHITECTURE_GOVERNANCE_INDEX.md`, and
  `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md` to reference the completed
  assessment and deferral decision.

### PR #102: v1.0 Demo Freshness-Date Stabilization

- Stabilized the v1.0 demo smoke path after sample market price snapshots
  became stale relative to the current calendar date.
- Added an optional internal `today` reference-date parameter through the
  orchestration path so tests and the deterministic demo can use the sample
  data's fixed reference date.
- Set the v1.0 demo reference date to `2026-05-24`, matching the sample market
  price freshness context.
- Preserved normal analysis and batch CLI behavior: ordinary CLI runs still use
  the current date for market price freshness unless an internal caller passes
  a reference date.
- Kept model rating, model confidence, model signal, DCF, fair value per share,
  report wording, and no-investment-advice behavior unchanged.

## Durable Files Added Or Updated

v1.1.5 adds or updates these durable files:

- `docs/GENERATED_ARTIFACT_MANIFEST_ASSESSMENT.md`
- `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md`
- `docs/ARCHITECTURE_GOVERNANCE_INDEX.md`
- `docs/V1_1_5_RELEASE_NOTES.md`
- `README.md`
- `scripts/run_analysis.py`
- `scripts/run_batch_analysis.py`
- `scripts/run_v1_0_demo.py`
- `tests/test_run_analysis.py`
- `tests/test_run_batch_analysis.py`

## Test Status

The local unit suite contains 229 tests.

Post-PR #102 validation on fresh `main`:

```bash
python -m unittest discover -s tests
```

Result: 229 passed.

v1.0 demo validation command:

```bash
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_post_pr102_validation
```

Result: `demo_completed` was `true`.

Working tree validation:

```bash
git status --short
```

Result: clean.

## Maintainer Validation Before Tagging

Before creating the `v1.1.5` tag:

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
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_1_5_release_validation
```

6. Confirm generated reports remain ignored and the working tree is clean.
7. Create the `v1.1.5` tag only after the release-note PR is merged to `main`
   and validation passes.

Follow `docs/RELEASE_AND_TAG_GOVERNANCE.md` and
`docs/V1_0_X_PATCH_RELEASE_CHECKLIST.md` for tag and GitHub Release handling.

## Upgrade Notes From v1.1.4

No data migration is required. Existing v1.1.4 sample inputs remain compatible.
Generated reports, summaries, audit logs, and model artifacts continue to be
written under ignored `reports/` paths.

Users can upgrade by pulling the v1.1.5 release and running:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py
```

Maintainers should continue generated-output governance only when a future
assessment identifies a concrete consumer or review gap that justifies the next
small implementation step.

## Explicit Non-Changes

v1.1.5 does not add or change:

- generated artifact manifest implementation
- manifest schema
- manifest validator
- CLI options or CLI contract
- financial logic
- DCF math
- fair value per share calculation logic
- model rating thresholds or rating rules
- model confidence scoring, thresholds, labels, or generated wording
- model signal gating rules, enum values, labels, or generated wording
- generated report wording
- analysis summary schema behavior
- audit log schema behavior
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
- generated reports committed to the repository
- GitHub UI settings automation
- price targets
- buy/sell/hold recommendations
- personal investment advice
- trading, broker/order, or portfolio logic

Generated artifact manifest implementation, fact report parser/schema/validator
work, audit log schema implementation, adapters, live fetching, and new
companies remain future work and are not part of v1.1.5.
