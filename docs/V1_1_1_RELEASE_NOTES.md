# v1.1.1 Release Notes

## Status

v1.1.1 is a maintenance and public-repository governance release for the
deterministic Aktienanalyse-Agent core. It completes the post-v1.1.0
model-rating output contract hardening block and documents the public repository
governance hardening added after the repository became public.

This release does not add new financial behavior, new calculations, live data
fetching, adapters, framework integrations, web UI, investment advice, or
trading logic.

The deterministic workflow remains focused on NVDA, AMD, and TSMC sample data
with source validation, company context generation, research gaps, ratios,
valuation readiness, DCF, fair value per share, model rating, model confidence,
model signal, fact-only reports, structured summaries, and audit logs.

## Release Summary

### PR #83: Model Rating Output Schema / Contract

- Added `config/model_rating_output_schema.json`.
- Added model rating output validation for required top-level fields,
  assumptions, market price source references, date/datetime fields, and type
  checks.
- Added model rating contract tests for valid output, missing required fields,
  invalid field types, source-reference preservation, and prohibited-language
  boundaries.
- Extended v1.0 demo validation to check generated NVDA, AMD, and TSMC model
  rating output artifacts against the contract.

### PR #84: Public Repository Security And Governance Assessment

- Added `docs/PUBLIC_REPOSITORY_SECURITY_GOVERNANCE_ASSESSMENT.md`.
- Assessed the current public-repository governance posture using repository
  files as the source of truth.
- Separated file-based findings from GitHub settings that require manual
  maintainer verification.
- Recommended a narrow public-repository governance hardening sequence before
  continuing generated-output schema work.

### PR #85: Public Repository Governance Hardening

- Added `.github/CODEOWNERS` with `@akkbkk10` ownership routing for the full
  repository, GitHub metadata, governance files, config, scripts, tests, and
  docs.
- Added `docs/SECRET_HYGIENE_CHECKLIST.md`.
- Updated `SECURITY.md` and `CONTRIBUTING.md` with public-repository reporting,
  owner-review, and secret-hygiene guidance.
- Kept branch protection, CODEOWNERS enforcement, secret scanning, push
  protection, and private vulnerability reporting as manual GitHub setting
  checks rather than repository-file claims.

### PR #86: GitHub Actions Least-Privilege Permissions

- Added explicit `permissions: contents: read` to
  `.github/workflows/tests.yml`.
- Preserved the existing pull request trigger, job, step names, validation
  commands, smoke tests, full unit suite, demo workflow, and JSON validation.
- Did not add secrets, use `pull_request_target`, add jobs, remove guardrail
  steps, or change runtime behavior.

### PR #87: Release And Tag Governance

- Added `docs/RELEASE_AND_TAG_GOVERNANCE.md`.
- Documented release-note PR expectations, tag timing after merge to `main`,
  final validation from a fresh checkout, `vX.Y.Z` tag naming, generated
  artifact exclusions, and release scope exclusions.
- Kept tag protection, tag rulesets, branch protection, required checks,
  required reviews, secret scanning, push protection, private vulnerability
  reporting, dependency graph, and Dependabot alerts as manual GitHub setting
  checks.

## Durable Files Added Or Updated

v1.1.1 adds or updates these durable contract and governance files:

- `config/model_rating_output_schema.json`
- `docs/PUBLIC_REPOSITORY_SECURITY_GOVERNANCE_ASSESSMENT.md`
- `.github/CODEOWNERS`
- `docs/SECRET_HYGIENE_CHECKLIST.md`
- `SECURITY.md`
- `CONTRIBUTING.md`
- `.github/workflows/tests.yml`
- `docs/RELEASE_AND_TAG_GOVERNANCE.md`
- `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md`
- `docs/SCHEMA_FIELD_REFERENCE.md`
- `docs/ARCHITECTURE_GOVERNANCE_INDEX.md`
- `README.md`

## Test Status

The local unit suite contains 208 tests.

Focused validation commands:

```bash
python -m unittest tests.test_model_rating
python -m unittest tests.test_run_v1_0_demo
python -m unittest tests.test_forbidden_output_regression
python -m unittest tests.test_model_confidence
python -m unittest tests.test_model_signal
```

Full test suite command:

```bash
python -m unittest discover -s tests
```

Relevant contract JSON validation commands:

```bash
python -m json.tool config/model_rating_output_schema.json
python -m json.tool config/company_context_schema.json
python -m json.tool config/dcf_output_schema.json
python -m json.tool config/fair_value_per_share_output_schema.json
python -m json.tool config/market_price_snapshot_schema.json
```

v1.0 demo validation command:

```bash
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_1_1_release_notes_demo
```

The demo validates the deterministic workflow for NVDA, AMD, and TSMC and
writes generated artifacts under the configured `reports/` path, which remains
ignored by git.

## Maintainer Validation Before Tagging

Before creating the `v1.1.1` tag:

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
python -m json.tool config/model_rating_output_schema.json
python -m json.tool config/company_context_schema.json
python -m json.tool config/dcf_output_schema.json
python -m json.tool config/fair_value_per_share_output_schema.json
python -m json.tool config/market_price_snapshot_schema.json
```

5. Run the demo validation required by the existing release process:

```bash
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_1_1_release_validation
```

6. Confirm generated reports remain ignored and the working tree is clean.
7. Create the `v1.1.1` tag only after the release-note PR is merged to `main`
   and validation passes.

Follow `docs/RELEASE_AND_TAG_GOVERNANCE.md` and
`docs/V1_0_X_PATCH_RELEASE_CHECKLIST.md` for tag and GitHub Release handling.

## Upgrade Notes From v1.1.0

No data migration is required. Existing v1.1.0 sample inputs remain compatible.
Generated reports and model artifacts continue to be written under ignored
`reports/` paths.

Users can upgrade by pulling the v1.1.1 release and running:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py
```

Maintainers should continue future generated-output schema hardening with the
next narrow candidate only after manually verifying public repository settings
that cannot be proven from repository files.

## Explicit Non-Changes

v1.1.1 does not add or change:

- financial logic
- DCF math
- fair value per share calculation logic
- model rating thresholds or behavior
- model confidence behavior
- model signal behavior
- generated report wording
- CLI behavior
- test behavior
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

Model confidence output schema, model signal output schema, audit log schema,
analysis summary schema, and fact report schema hardening remain future work and
are not part of v1.1.1.

