# Release And Tag Governance

This document defines repository-file release and tag rules for the public
repository. It complements `docs/V1_0_X_PATCH_RELEASE_CHECKLIST.md` and does not
enable or claim any GitHub UI setting.

## Release Workflow

- Release notes must be committed through a pull request before tagging.
- Release-note PRs must stay documentation-only unless the release issue
  explicitly scopes other maintenance work.
- Generated reports, summaries, DCF outputs, model outputs, audit logs, caches,
  and local artifacts must not be committed in release-note PRs.
- Tags must be created only after the release PR is merged and the intended
  release commit is present on `main`.
- Final validation must use a fresh checkout of `main`, not an unmerged release
  branch.
- `python -m unittest discover -s tests` must pass before tagging.
- The v1.0 demo validation in `docs/V1_0_X_PATCH_RELEASE_CHECKLIST.md` should
  pass before tagging, using an ignored `reports/tmp_*` path.
- Tag names must use the existing `vX.Y.Z` pattern, such as `v1.1.0`.
- Published release notes must state whether financial behavior changed. If it
  did not change, say that DCF math, fair value logic, model rating, model
  confidence, model signal, investment-advice boundaries, live fetching, and
  trading behavior are unchanged.

## Tag Rules

- Create annotated release tags only from the intended commit on `main`.
- Do not create release tags from feature branches, pull request branches, local
  worktrees with uncommitted changes, or generated-output review directories.
- Do not reuse, move, delete, or overwrite a published tag without a documented
  maintainer decision.
- Before pushing a tag, verify it points to the intended commit:

```bash
git rev-list -n 1 vX.Y.Z
git rev-parse origin/main
```

- After publishing, verify the GitHub Release points to the same tag and commit.

## Manual GitHub Settings To Verify

Repository files cannot prove these settings are enabled. Maintainers should
verify them in GitHub before relying on them as enforced controls:

- branch protection or rulesets for `main`
- required status checks
- required pull request review
- conversation resolution before merge
- force-push protection
- branch deletion protection
- CODEOWNERS review enforcement
- tag protection or tag rulesets for `v*`
- Actions default token permission setting
- secret scanning
- push protection
- private vulnerability reporting
- dependency graph
- Dependabot alerts

## Release Governance Must Not Include

Release and tag governance must not add:

- runtime code changes
- financial logic changes
- schema changes unless explicitly reviewed in a schema PR
- committed generated reports or generated model artifacts
- live market data fetching
- adapters or framework-specific business logic
- web UI
- MCP or A2A implementation
- package rename
- new companies
- investment advice
- price targets
- buy/sell/hold recommendations
- broker/order behavior
- trading or portfolio logic

