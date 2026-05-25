# v1.1.4 Release Notes

## Status

v1.1.4 is a generated-output governance documentation release for the
deterministic Aktienanalyse-Agent core. It completes the fact report Markdown
assessment and expectations documentation block that followed v1.1.3.

This release does not add new financial behavior, new calculations, report
wording changes, live data fetching, adapters, framework integrations, web UI,
investment advice, or trading logic.

The deterministic workflow remains focused on NVDA, AMD, and TSMC sample data
with source validation, company context generation, research gaps, ratios,
valuation readiness, DCF, fair value per share, model rating, model confidence,
model signal, fact-only reports, structured summaries, and audit logs.

## Release Summary

### PR #99: Fact Report Contract Need Assessment

- Added `docs/FACT_REPORT_CONTRACT_NEED_ASSESSMENT.md`.
- Reviewed actual generated `fact_report.md` outputs for NVDA, AMD, and TSMC.
- Documented the current generated Markdown heading structure.
- Identified stable report sections suitable for expectations documentation,
  including report title, run metadata, facts, validation status, calculated
  ratios, source references, optional calculation/model sections, missing data,
  warnings, and boundary.
- Identified flexible content that should not be over-constrained, including
  exact prose, source-reference details, warning text, reason and blocker
  wording, timestamps, paths, financial values, research-gap wording, and
  embedded upstream output details.
- Confirmed the fact report guardrails for no buy/sell/hold recommendations,
  no price targets, no investment advice, visible assumptions, visible missing
  data, visible warnings, and boundary language.
- Recommended a narrow fact report expectations document instead of a Markdown
  parser, schema, or validator.

### PR #100: Fact Report Expectations

- Added `docs/FACT_REPORT_EXPECTATIONS.md`.
- Documented the generated fact report as a user-facing Markdown artifact.
- Documented expected stable sections:
  - report title
  - run metadata
  - facts
  - validation status
  - calculated ratios
  - source references
  - optional DCF, fair value per share, model rating, model confidence, and
    model signal sections
  - missing data
  - warnings
  - boundary / no-investment-advice framing
- Documented intentionally flexible content, including exact prose,
  source-reference details, warning text, reasons, blockers, timestamps, paths,
  financial values, research-gap wording, and embedded upstream output details.
- Documented guardrails against buy/sell/hold recommendations, price targets,
  personal investment advice, broker/order instructions, automated trading
  language, portfolio automation guidance, invented sources, and unsupported
  live-fetching claims.
- Documented why no Markdown parser, schema, or validator is added yet.
- Documented when a future heading or section-level contract could become
  justified.

## Durable Files Added Or Updated

v1.1.4 adds or updates these durable generated-output governance files:

- `docs/FACT_REPORT_CONTRACT_NEED_ASSESSMENT.md`
- `docs/FACT_REPORT_EXPECTATIONS.md`
- `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md`
- `docs/ARCHITECTURE_GOVERNANCE_INDEX.md`
- `README.md`

## Test Status

The local unit suite contains 229 tests.

Focused validation commands:

```bash
python -m unittest tests.test_generate_report
python -m unittest tests.test_forbidden_output_regression
python -m unittest tests.test_run_v1_0_demo
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
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_1_4_release_notes_demo
```

The demo validates the deterministic workflow for NVDA, AMD, and TSMC and
writes generated artifacts under the configured `reports/` path, which remains
ignored by git.

## Maintainer Validation Before Tagging

Before creating the `v1.1.4` tag:

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
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_1_4_release_validation
```

6. Confirm generated reports remain ignored and the working tree is clean.
7. Create the `v1.1.4` tag only after the release-note PR is merged to `main`
   and validation passes.

Follow `docs/RELEASE_AND_TAG_GOVERNANCE.md` and
`docs/V1_0_X_PATCH_RELEASE_CHECKLIST.md` for tag and GitHub Release handling.

## Upgrade Notes From v1.1.3

No data migration is required. Existing v1.1.3 sample inputs remain compatible.
Generated reports, summaries, audit logs, and model artifacts continue to be
written under ignored `reports/` paths.

Users can upgrade by pulling the v1.1.4 release and running:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py
```

Maintainers should continue generated-output governance with the next narrow
candidate only after an assessment confirms that implementation adds value
beyond existing validators, review docs, expectations, and tests.

## Explicit Non-Changes

v1.1.4 does not add or change:

- financial logic
- DCF math
- fair value per share calculation logic
- model rating thresholds or behavior
- model confidence scoring, thresholds, labels, or generated wording
- model signal gating rules, enum values, labels, or generated wording
- generated report wording
- Markdown parser behavior
- schema behavior
- validator behavior
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

Generated artifact manifest assessment, fact report parser/schema/validator
work, audit log schema implementation, adapters, live fetching, and new
companies remain future work and are not part of v1.1.4.
