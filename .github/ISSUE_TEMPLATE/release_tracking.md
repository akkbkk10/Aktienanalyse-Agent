---
name: Release tracking
about: Track a v1.0.x patch, minor, or major release
title: "[Release]: v"
labels: release
assignees: ""
---

## Release target

- Target version:
- Release type:
  - [ ] patch
  - [ ] minor
  - [ ] major
- Target commit on `main`:

## Included PRs

- 

## Pre-release checks

- [ ] All intended PRs are merged into `main`.
- [ ] Release is not being created from an unmerged PR branch.
- [ ] Financial logic changes are absent, or explicitly reviewed and documented.
- [ ] Live fetching is absent, or future adapter work explicitly added, tested,
      and documented it.
- [ ] Generated reports are not committed.

## Validation

- [ ] Full test suite passed:

```bash
python -m unittest discover -s tests
```

- [ ] v1.0 demo validation passed:

```bash
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_release_tracking_demo
```

- [ ] Generated-output review completed with
      `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`.
- [ ] Guardrail/security checklist completed with
      `docs/GUARDRAIL_SECURITY_TEST_PLAN.md`.
- [ ] Release notes are prepared.

## Release actions

- [ ] Annotated tag created.
- [ ] Tag pushed.
- [ ] GitHub Release published.
- [ ] Tag points to the intended `main` commit.

## Safety reminders

- Do not reuse or move existing release tags.
- Do not create a release from an unmerged PR branch.
- Do not publish generated reports as committed files.
- Do not include financial logic changes unless explicitly reviewed.
- Do not include live fetching unless future adapter work explicitly adds and
  tests it.
- Do not add price targets, buy/sell/hold recommendations, personal investment
  advice, or trading/broker/order behavior.
