# v1.0.2 Release Notes

## Status

v1.0.2 is a post-v1.0.1 maintenance release focused on open-source governance,
review discipline, and maintainer workflow quality. It does not change
financial logic, DCF math, fair value logic, model rating behavior, model
confidence behavior, model signal behavior, sample company data, or generated
model calculations.

## Maintenance Summary

### PR #42: Open-Source Governance Files

- Added Apache License 2.0 licensing with copyright holder `akkbkk10`.
- Added `CONTRIBUTING.md`, `SECURITY.md`, and `CODE_OF_CONDUCT.md`.
- Linked governance files from the README.
- Documented contribution expectations around deterministic core behavior,
  source traceability, auditability, no investment advice, no price targets, no
  buy/sell/hold recommendations, and no unvalidated live fetching.

### PR #43: Issue And Pull Request Templates

- Added GitHub issue templates for bug reports, documentation improvements,
  guardrail/security reviews, and feature requests.
- Added a pull request template with changed-file, test, generated-artifact,
  and guardrail impact checklists.
- Reinforced that generated reports should not be committed and that future
  contributors must document guardrail impact.

### PR #44: Generated-Output Review Guidance

- Added `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`.
- Documented how reviewers should inspect generated fact reports, structured
  summaries, DCF outputs, fair value per share outputs, model rating outputs,
  model confidence outputs, model signal outputs, and audit logs.
- Added safe vs unsafe generated-output examples.
- Added future adapter review checks for Market Data Agent, MCP, A2A, and
  framework-evaluation work.

### PR #45: v1.0.x Patch Release Checklist

- Added `docs/V1_0_X_PATCH_RELEASE_CHECKLIST.md`.
- Documented the safe maintainer workflow for patch releases, including fresh
  `main` checkout, full test validation, v1.0 demo validation, generated-output
  review, guardrail review, release notes, annotated tags, GitHub Releases, and
  tag verification.
- Included PowerShell and platform-neutral shell examples.
- Added troubleshooting notes for common release mistakes.

### PR #46: Release Tracking Issue Template

- Added `.github/ISSUE_TEMPLATE/release_tracking.md`.
- Added checklist sections for target version, included PRs, release type,
  merged-to-main confirmation, validation, generated-output review, guardrail
  review, release notes, tag creation, tag push, GitHub Release publication,
  and tag verification.
- Added reminders not to reuse or move existing release tags, release from an
  unmerged PR branch, commit generated reports, or include unreviewed financial
  logic or live fetching.

## Test Status

The local unit suite contains 182 tests.

Required validation commands:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_0_2_release_notes_demo
```

The v1.0 demo validates the deterministic workflow for NVDA, AMD, and TSMC and
writes generated artifacts under `reports/`, which remains ignored by git.

## Upgrade Notes From v1.0.1

No data migration is required. Users can upgrade from v1.0.1 to v1.0.2 by
pulling the release tag and continuing to run the same workflow commands:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py
```

v1.0.2 improves project maintainability, contribution quality, release tracking,
and generated-output review discipline. Existing generated reports, summaries,
DCF outputs, fair value outputs, model ratings, model confidence outputs, model
signals, and audit logs remain compatible with v1.0.1.

## Explicit Non-Changes

v1.0.2 does not add or change:

- application logic
- financial logic
- DCF math
- fair value per share logic
- model rating behavior
- model confidence behavior
- model signal behavior
- generated report wording
- live data fetching
- new companies
- runtime agent code
- framework dependencies
- project naming
- package publishing
- CLI behavior
- price targets
- buy/sell/hold recommendations
- personal investment advice
- trading or portfolio logic
