# v1.1.6 Release Notes

## Status

v1.1.6 is a documentation and governance release for the deterministic
Aktienanalyse-Agent core. It finalizes the post-v1.1.5 roadmap/status cleanup,
adapter boundary, methodology configuration boundary, and release-note
preparation block.

This release covers PR #106 through PR #111. It does not add
runtime code, schemas, CLI behavior, config changes, generated reports,
adapters, live data, methodology configuration implementation, generated
artifact manifest implementation, financial logic, valuation formula changes,
model behavior changes, report wording changes, advice, price targets, trading,
or portfolio automation.

## Release Summary

### PR #106: Post-v1.1.5 Roadmap And Status Cleanup

- Cleaned up stale post-v1.1.5 roadmap and generated-output status language.
- Marked older v1.1.x candidate planning as historical or superseded where
  appropriate.
- Updated generated-output schema assessment language to distinguish
  implemented contracts, expectations-only artifacts, and deferred artifacts.
- Preserved the long-term stable-core-first roadmap while removing stale
  active next-step wording.

### PR #107: Adapter / Market Data Boundary RFC

- Added `docs/ADAPTER_MARKET_DATA_BOUNDARY_RFC.md`.
- Clarified the boundary between the deterministic core and any future Market
  Data Agent, adapter, MCP, A2A, framework, or web UI layer.
- Documented that live fetching must not be added directly to core analysis
  modules.
- Defined high-level future snapshot expectations and implementation
  prerequisites.
- Kept adapter, live-data, MCP/A2A, framework, and web UI work deferred until a
  focused proposal, data-contract review, risk review, and decision record
  justify implementation.

### PR #108: Methodology Configuration Boundary Assessment

- Added `docs/METHODOLOGY_CONFIGURATION_BOUNDARY_ASSESSMENT.md`.
- Clarified that the current methodology configuration remains inert and
  validation-only.
- Documented what future methodology configuration may and may not control.
- Distinguished safe configuration boundaries from financial logic changes.
- Defined prerequisites before any future methodology configuration
  implementation PR.
- Preserved explicit-input, assumption-review, generated-output, and
  no-investment-advice guardrails.

### PR #109: Historical v1.1.x Planning Status Clarification

- Clarified that the v1.1.0 baseline section in
  `docs/V1_1_X_NEXT_CANDIDATE_PLAN.md` is historical.
- Marked the old candidate-block timing column as preserved historical context,
  not current implementation guidance.
- Kept the current roadmap aligned with the completed v1.1.x contract,
  expectations, governance, and deferral work.

### PR #110: v1.1.6 Release Notes Candidate

- Added `docs/V1_1_6_RELEASE_NOTES.md`.
- Summarized the completed docs/governance block from PR #106 through PR #109.
- Added the v1.1.6 release-note entry to the README documentation map.
- Preserved docs-only scope and explicitly excluded runtime, schema, config,
  CLI, generated report, adapter, live-data, methodology implementation,
  manifest implementation, financial logic, model behavior, report wording,
  advice, price target, trading, and portfolio changes.

### PR #111: Finalize v1.1.6 Release Notes

- Promoted the release notes from candidate wording to final release wording.
- Added PR #110 to the release summary.
- Updated the README documentation map entry from release-note candidate to
  release notes.
- Preserved docs-only scope before tagging and publishing v1.1.6.

## Durable Files Added Or Updated

v1.1.6 adds or updates these durable docs/governance files:

- `README.md`
- `docs/ARCHITECTURE_GOVERNANCE_INDEX.md`
- `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md`
- `docs/V1_1_X_NEXT_CANDIDATE_PLAN.md`
- `docs/ADAPTER_MARKET_DATA_BOUNDARY_RFC.md`
- `docs/METHODOLOGY_CONFIGURATION_BOUNDARY_ASSESSMENT.md`
- `docs/V1_1_6_RELEASE_NOTES.md`

## Test Status

The local unit suite contains 229 tests.

Preflight and release validation command:

```bash
python -m unittest discover -s tests
```

Result: 229 tests OK.

## Maintainer Validation Before Tagging

Before creating a `v1.1.6` tag, maintainers should:

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
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_1_6_release_validation
```

5. Confirm generated reports remain ignored and the working tree is clean.
6. Create the `v1.1.6` tag only after the release-note PR is merged to `main`
   and validation passes.

Follow `docs/RELEASE_AND_TAG_GOVERNANCE.md` and
`docs/V1_0_X_PATCH_RELEASE_CHECKLIST.md` for tag and GitHub Release handling.

## Explicit Non-Changes

v1.1.6 does not add or change:

- runtime code
- tests
- schemas
- config files
- CLI behavior
- dependencies
- generated reports
- GitHub Releases
- tags
- publishing
- adapters
- live data
- MCP or A2A integration
- web UI
- methodology configuration implementation
- generated artifact manifest implementation
- financial logic
- valuation formulas
- DCF math
- fair value per share calculation logic
- model rating thresholds, labels, or behavior
- model confidence scoring, thresholds, labels, or generated wording
- model signal gating rules, enum values, labels, or generated wording
- report wording
- buy/sell/hold advice
- price targets
- trading logic
- portfolio automation
- personal investment advice

Generated artifact manifest implementation, adapter/live-data implementation,
methodology configuration implementation, MCP/A2A, web UI, new financial logic,
and new companies remain future work and are not part of v1.1.6.
