# v1.1.2 Release Notes

## Status

v1.1.2 is a generated-output contract hardening release for the deterministic
Aktienanalyse-Agent core. It completes the model confidence and model signal
output assessment and contract block that followed v1.1.1.

This release does not add new financial behavior, new calculations, live data
fetching, adapters, framework integrations, web UI, investment advice, or
trading logic.

The deterministic workflow remains focused on NVDA, AMD, and TSMC sample data
with source validation, company context generation, research gaps, ratios,
valuation readiness, DCF, fair value per share, model rating, model confidence,
model signal, fact-only reports, structured summaries, and audit logs.

## Release Summary

### PR #89: Model Confidence Output Schema Assessment

- Added `docs/MODEL_CONFIDENCE_OUTPUT_SCHEMA_ASSESSMENT.md`.
- Reviewed actual generated model confidence artifacts for NVDA, AMD, and TSMC.
- Identified stable fields for future contract protection, including top-level
  confidence fields, assumption-quality structure, source references, and the
  model-quality disclaimer.
- Identified guardrail-sensitive fields that should remain flexible, including
  reasons, warnings, labels, matched terms, and source-reference variants.
- Recommended a narrow successful-output model confidence schema/contract.

### PR #90: Model Confidence Output Schema / Contract

- Added `config/model_confidence_output_schema.json`.
- Added model confidence output validation in `scripts/model_confidence.py`.
- Protected successful generated model confidence outputs for required
  top-level fields, confidence enum values, assumption-quality fields, source
  reference metadata, and market-price reference metadata when present.
- Kept reasons, warnings, labels, matched terms, and source-reference variants
  flexible.
- Added model confidence contract tests for valid output, manual-review
  assumption quality, missing required fields, invalid field types, invalid
  confidence enum values, missing assumption-quality fields, missing source
  reference metadata, and prohibited-language boundaries.
- Extended v1.0 demo validation to check generated NVDA, AMD, and TSMC model
  confidence output artifacts against the contract.

### PR #91: Model Signal Output Schema Assessment

- Added `docs/MODEL_SIGNAL_OUTPUT_SCHEMA_ASSESSMENT.md`.
- Reviewed actual generated model signal artifacts for NVDA, AMD, and TSMC.
- Confirmed current demo signal artifacts are generated successfully but remain
  `unavailable` because manual-review assumptions block active signals.
- Documented that active `model_positive`, `model_neutral`, and
  `model_negative` states exist in tests.
- Assessed investment-advice guardrails, including current signal enum values,
  prohibited-language checks, disclaimer boundaries, and manual-review signal
  blocking.
- Recommended a narrow model signal output schema/contract.

### PR #92: Model Signal Output Schema / Contract

- Added `config/model_signal_output_schema.json`.
- Added model signal output validation in `scripts/model_signal.py`.
- Protected the normal generated model signal object for required top-level
  fields, the current signal enum, nullable upstream-output summaries,
  assumption-quality gate structure when present, and the no-investment-advice
  disclaimer.
- Kept reasons, blocking reasons, warnings, labels, and assumption-quality
  wording flexible.
- Added model signal contract tests for active `model_positive`,
  `model_neutral`, and `model_negative` outputs, unavailable outputs, nullable
  upstream summaries, missing required fields, invalid field types, invalid
  signal enum values, missing nested upstream fields, and prohibited-language
  boundaries.
- Extended v1.0 demo validation to check generated NVDA, AMD, and TSMC model
  signal output artifacts against the contract.

## Durable Files Added Or Updated

v1.1.2 adds or updates these durable generated-output contract and governance
files:

- `docs/MODEL_CONFIDENCE_OUTPUT_SCHEMA_ASSESSMENT.md`
- `config/model_confidence_output_schema.json`
- `docs/MODEL_SIGNAL_OUTPUT_SCHEMA_ASSESSMENT.md`
- `config/model_signal_output_schema.json`
- `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md`
- `docs/SCHEMA_FIELD_REFERENCE.md`
- `docs/ARCHITECTURE_GOVERNANCE_INDEX.md`
- `README.md`

## Test Status

The local unit suite contains 223 tests.

Focused validation commands:

```bash
python -m unittest tests.test_model_confidence
python -m unittest tests.test_model_signal
python -m unittest tests.test_run_v1_0_demo
python -m unittest tests.test_forbidden_output_regression
```

Full test suite command:

```bash
python -m unittest discover -s tests
```

Relevant contract JSON validation commands:

```bash
python -m json.tool config/model_confidence_output_schema.json
python -m json.tool config/model_signal_output_schema.json
python -m json.tool config/model_rating_output_schema.json
python -m json.tool config/dcf_output_schema.json
python -m json.tool config/fair_value_per_share_output_schema.json
```

v1.0 demo validation command:

```bash
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_1_2_release_notes_demo
```

The demo validates the deterministic workflow for NVDA, AMD, and TSMC and
writes generated artifacts under the configured `reports/` path, which remains
ignored by git.

## Maintainer Validation Before Tagging

Before creating the `v1.1.2` tag:

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
python -m json.tool config/model_confidence_output_schema.json
python -m json.tool config/model_signal_output_schema.json
python -m json.tool config/model_rating_output_schema.json
python -m json.tool config/dcf_output_schema.json
python -m json.tool config/fair_value_per_share_output_schema.json
```

5. Run the demo validation required by the existing release process:

```bash
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_1_2_release_validation
```

6. Confirm generated reports remain ignored and the working tree is clean.
7. Create the `v1.1.2` tag only after the release-note PR is merged to `main`
   and validation passes.

Follow `docs/RELEASE_AND_TAG_GOVERNANCE.md` and
`docs/V1_0_X_PATCH_RELEASE_CHECKLIST.md` for tag and GitHub Release handling.

## Upgrade Notes From v1.1.1

No data migration is required. Existing v1.1.1 sample inputs remain compatible.
Generated reports and model artifacts continue to be written under ignored
`reports/` paths.

Users can upgrade by pulling the v1.1.2 release and running:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py
```

Maintainers should continue future generated-output schema hardening with the
next narrow candidate only after an assessment confirms that a standalone
contract adds value beyond existing validators and tests.

## Explicit Non-Changes

v1.1.2 does not add or change:

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

Audit log schema assessment, analysis summary schema hardening, fact report
schema hardening, generated artifact manifests, adapters, live fetching, and
new companies remain future work and are not part of v1.1.2.
