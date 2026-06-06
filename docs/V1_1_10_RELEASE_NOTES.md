# v1.1.10 Release Notes Candidate

## Status

v1.1.10 is not tagged or published yet. These release notes are prepared as a
candidate for the post-v1.1.9 architecture visualization and local user-guidance
documentation block.

This candidate covers PR #127 through PR #129. It does not add runtime behavior
changes, test changes, schema changes, config changes, generated reports,
adapter implementation, live data, provider APIs, MCP/A2A runtime integration,
web UI, desktop app behavior, methodology implementation, generated artifact
manifest implementation, financial logic changes, report wording changes,
advice, price targets, trading, or portfolio automation.

## Release Summary

### PR #127: Architecture Visual Overview

- Added `docs/ARCHITECTURE_VISUAL_OVERVIEW.md`.
- Documented the current post-v1.1.9 architecture with Mermaid diagrams for:
  - high-level layered architecture
  - data flow and evidence traceability
  - active versus deferred layers
- Clarified the stable deterministic core, governance layer, generated artifact
  surface, and deferred adapter/interface layers.
- Added navigation links from the README and architecture governance index.
- Preserved docs-only scope and did not add runtime, test, schema, config,
  generated-report, adapter, live-data, financial-logic, release, tag, or
  GitHub Release changes.

### PR #128: Mermaid Rendering Safety

- Simplified two Mermaid dotted edges in
  `docs/ARCHITECTURE_VISUAL_OVERVIEW.md` for safer GitHub rendering.
- Preserved the architecture meaning and deferred-layer explanation in prose.
- Kept the PR docs-only with no runtime, schema, config, test, generated-report,
  adapter, live-data, financial-logic, release, tag, or GitHub Release changes.

### PR #129: Local User Acceptance Guide

- Added `docs/LOCAL_USER_ACCEPTANCE_TEST.md`.
- Documented the current local CLI acceptance path:
  - open the repository locally
  - run the full unit suite
  - run the deterministic v1.0 demo into an ignored `reports/tmp_*` directory
  - inspect generated per-ticker reports, summaries, model outputs, and audit
    logs
  - verify no-advice, no-live-data, no-price-target, no-trading, and
    no-portfolio-automation guardrails
  - clean up temporary generated artifacts
- Cross-linked `docs/ARCHITECTURE_OVERVIEW.md`,
  `docs/ARCHITECTURE_VISUAL_OVERVIEW.md`, and the local acceptance guide.
- Added README and architecture governance index navigation entries.
- Clarified that the current user-facing path is local CLI execution, not a web
  UI, desktop app, adapter runtime, live data workflow, provider API workflow,
  MCP/A2A runtime integration, or financial automation.

## Documentation Block Decision

v1.1.10 is a documentation and user-guidance candidate. It bundles the
architecture visualization work with the local CLI acceptance guide so reviewers
can understand both the system shape and the current local validation path.

The block remains intentionally narrow:

- The architecture visualization explains the current stable core and deferred
  layers.
- The local acceptance guide explains how to run and inspect the existing CLI
  demo locally.
- No new runtime behavior, UI surface, adapter boundary, data source, or
  financial capability is introduced.

## Durable Files Added Or Updated

v1.1.10 would add or update these durable documentation files:

- `docs/ARCHITECTURE_VISUAL_OVERVIEW.md`
- `docs/LOCAL_USER_ACCEPTANCE_TEST.md`
- `docs/ARCHITECTURE_OVERVIEW.md`
- `docs/ARCHITECTURE_GOVERNANCE_INDEX.md`
- `README.md`
- `docs/V1_1_10_RELEASE_NOTES.md`

## Test Status

The local unit suite contains 231 tests.

Validation command:

```bash
python -m unittest discover -s tests
```

Result: 231 tests OK.

## Maintainer Validation Before Tagging

Before creating a `v1.1.10` tag, maintainers should:

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
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_1_10_release_validation
```

5. Confirm generated reports remain ignored and the working tree is clean.
6. Create the `v1.1.10` tag only after the release-note PR is merged to `main`
   and validation passes.

Follow `docs/RELEASE_AND_TAG_GOVERNANCE.md` and
`docs/V1_0_X_PATCH_RELEASE_CHECKLIST.md` for tag and GitHub Release handling.

## Explicit Non-Changes

v1.1.10 does not add or change:

- runtime analysis behavior
- tests
- schemas
- config files
- CLI behavior
- dependencies
- generated reports committed to the repository
- adapter implementation
- live data
- provider APIs
- external credentials
- MCP or A2A runtime integration
- web UI
- desktop app behavior
- methodology implementation
- generated artifact manifest implementation
- financial logic
- valuation formulas
- DCF behavior
- fair value per share behavior
- model rating behavior
- model confidence behavior
- model signal behavior
- analysis report wording
- generated report content
- buy/sell/hold advice
- price targets
- trading logic
- portfolio automation
- personal investment advice

Adapter implementation, live data, provider APIs, external credentials,
MCP/A2A, web UI, desktop app behavior, generated artifact manifest
implementation, methodology implementation, new financial logic, and new
companies remain future work and are not part of this candidate.
