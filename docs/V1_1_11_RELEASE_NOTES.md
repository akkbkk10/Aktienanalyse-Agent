# v1.1.11 Release Notes

## Status

v1.1.11 is a project status and local offline-trial documentation block for the
deterministic Aktienanalyse-Agent core after PR #131 through PR #137.

This release-note candidate documents current state only. It does not add
runtime behavior changes, tests, schemas, config changes, ASML data files,
generated reports, source material, adapter implementation, live data, provider
APIs, MCP/A2A runtime integration, web UI, desktop app behavior, release tags,
GitHub Releases, methodology implementation, financial logic, report wording
semantics, advice, price targets, trading, or portfolio automation.

## Release Summary

### PR #131: v1.1.10 Release Notes Finalization

- Finalized the v1.1.10 documentation-release notes.
- Preserved the architecture visualization and local user-acceptance guide as a
  docs-only block.

### PR #132: Offline Company Data Trial Plan

- Added the project-level manual offline company-data trial plan.
- Clarified that explicit local files can be used for trial runs only after
  validation.
- Kept live data, adapters, provider APIs, UI, generated reports, and new
  company promotion out of scope.

### PR #133: ASML Offline Trial Source Package Plan

- Added ASML-specific offline source-package planning.
- Defined ASML as a future manual offline source-package trial, not committed
  public sample data.
- Documented ASML-specific risks around source review, IFRS labels, currency,
  share count, market-price snapshots, and assumptions.

### PR #134: ASML Source Material Handoff Checklist

- Added a manual official-source handoff checklist for ASML.
- Required official source materials and metadata before ASML data files may be
  prepared for a reviewed source-package PR.
- Clarified that unverified source snippets, unofficial summaries, and generated
  local files are not enough for repo-final ASML data.

### PR #135: Local Source Material Boundary

- Added `source_material/` to `.gitignore`.
- Documented `source_material/ASML/` as a local-only review-copy location.
- Preserved the rule that reviewed source-data records under `data/` require a
  separate PR and must not be inferred from local source-material copies alone.

### PR #136: DCF Readiness Warning Wording

- Changed the blocked-run warning from valuation-stage wording to:
  `DCF readiness gate blocked DCF run.`
- Kept the guardrail strict while avoiding report-generation self-blocking from
  prohibited valuation wording.

### PR #137: Standalone Prohibited-Language Matching

- Added phrase-aware prohibited-language matching for generated reports and
  analysis summaries.
- Fixed the false positive where `hold` matched inside `ASML Holding N.V.`.
- Preserved blocking for standalone prohibited advice terms and phrases such as
  `hold`, `buy`, `sell`, `price target`, `trading`, `portfolio automation`, and
  `investment advice`.

## ASML Local Trial Status

ASML has been used as a local offline trial case after PR #137. The local ASML
package can validate through the onboarding validator, and a full local
report/summary/DCF workflow can run when the local ASML metrics, assumptions,
and watchlist entry are present.

This does not make ASML committed public sample data. ASML remains local-only
until a separate reviewed source-package PR intentionally adds reviewed ASML
source metrics, any DCF assumptions, watchlist changes, and related docs or
tests. Generated ASML reports, generated contexts, audit logs, research queues,
downloaded source files, PDFs, and `source_material/` review copies must not be
committed.

## Safer Local Trial Guidance

Local offline trials should direct generated outputs away from repository-root
operational files. Prefer ignored `reports/tmp_*` paths for reports, contexts,
audit logs, and research queues, for example:

```powershell
python scripts/run_analysis.py TICKER --source-data-path data/ticker_sample_metrics.json --generate-report --generate-summary --run-dcf --dcf-assumptions-path data/companies/TICKER/dcf_assumptions.json --reports-dir reports/tmp_offline_company_trial/TICKER --context-root reports/tmp_offline_company_trial/companies --audit-log-path reports/tmp_offline_company_trial/audit_log.jsonl --markdown-queue-path reports/tmp_offline_company_trial/research_queue.md --json-queue-path reports/tmp_offline_company_trial/research_queue.json
```

This avoids polluting root `audit_log.jsonl`, `research_queue.md`, and
`research_queue.json` during local trial runs.

## Market Price Boundary Status

Market price remains a stored snapshot boundary, not live data fetching. Core
modules must not fetch or refresh market prices directly.

Current behavior requires a validated `market_price` snapshot for full model
rating availability and downstream model signal availability. A future PR may
decide whether `market_price` should be optional for source-only onboarding,
ratio-only workflows, and DCF-only trials, with model rating and signal clearly
unavailable when no validated snapshot is present. That boundary decision is
pending and should remain separate from ASML data promotion or adapter work.

## Test Status

The local unit suite contains 235 tests.

Validation command:

```bash
python -m unittest discover -s tests
```

Result: 235 tests OK.

## Maintainer Validation Before Tagging

Before creating a `v1.1.11` tag, maintainers should:

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
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_1_11_release_validation
```

5. Confirm generated reports remain ignored and the working tree is clean.
6. Create the `v1.1.11` tag only after this release-note PR is merged to `main`
   and validation passes.

Follow `docs/RELEASE_AND_TAG_GOVERNANCE.md` and
`docs/V1_0_X_PATCH_RELEASE_CHECKLIST.md` for tag and GitHub Release handling.

## Explicit Non-Changes

v1.1.11 does not add or change:

- runtime analysis behavior
- tests
- schemas
- config files
- ASML source data
- generated reports committed to the repository
- generated contexts committed to the repository
- downloaded source material or PDFs
- source-material review copies
- dependencies
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
- model rating behavior
- model confidence behavior
- model signal behavior
- report or summary output semantics
- buy/sell/hold advice
- price targets
- trading logic
- portfolio automation
- personal investment advice
- release tags
- GitHub Releases
