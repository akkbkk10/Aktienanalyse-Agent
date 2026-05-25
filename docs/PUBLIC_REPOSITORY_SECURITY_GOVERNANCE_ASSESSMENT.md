# Public Repository Security Governance Assessment

This assessment reviews the repository posture after
`akkbkk10/Aktienanalyse-Agent` became public. It is documentation-only and does
not implement hardening changes.

The repository is a deterministic financial analysis core for NVDA, AMD, and
TSMC. Public-repository governance should be checked before more model-output
schema work because future schema changes will be easier to review safely when
the public contribution path, security-reporting path, merge controls, and
no-investment-advice boundaries are explicit.

## 1. Executive Recommendation

The ownership/reporting documentation hardening recommended by the original
assessment has been partially implemented in repository files:

- `.github/CODEOWNERS` now routes ownership for the full repository, GitHub
  metadata, governance files, config, scripts, tests, and docs.
- `docs/SECRET_HYGIENE_CHECKLIST.md` now gives contributors one explicit
  checklist for secrets, private data, and generated artifacts.
- `SECURITY.md` and `CONTRIBUTING.md` now reference the public-repository
  reporting, owner-review, and secret-hygiene flow more clearly.
- `.github/workflows/tests.yml` now declares explicit read-only repository
  contents permission for the test-only CI workflow.
- `docs/RELEASE_AND_TAG_GOVERNANCE.md` now documents release-note PR rules, tag
  timing, tag naming, generated-artifact exclusions, and manual GitHub setting
  checks.

This assessment finds several file-based controls already present, but the most
important public-repository controls for `main` are not verifiable from
repository files. Branch protection, required checks, pull request review rules,
conversation resolution, force-push protection, branch deletion protection,
secret scanning, push protection, dependency graph, Dependabot, and private
vulnerability reporting require manual verification in GitHub.

Recommended next PR: resume generated-output schema hardening only after
maintainers verify the public repository settings that cannot be proven from
files.

## 2. Current Public-Repository Posture

File-based posture is stronger than a bare public repository:

- `README.md` documents repository layout, test command, deterministic workflow
  boundaries, and repeated no-investment-advice messaging.
- `AGENTS.md` defines evidence, implementation, and review rules, including a
  pull request expectation for every change.
- `CONTRIBUTING.md` defines contribution guardrails, expected local tests, and
  generated-artifact hygiene.
- `SECURITY.md` defines vulnerability-reporting expectations, security scope,
  and guardrail expectations.
- `CODE_OF_CONDUCT.md` defines public collaboration expectations.
- `.github/CODEOWNERS` routes owner review for the repository, GitHub metadata,
  governance files, config, scripts, tests, and docs.
- `.github/pull_request_template.md` asks for changed files, tests, generated
  artifact review, and guardrail impact.
- `.github/ISSUE_TEMPLATE/` includes templates for bugs, documentation,
  features, guardrail/security review, release tracking, and schema proposals.
- `.github/workflows/tests.yml` runs the unit suite, targeted guardrail tests,
  validation commands, workflow smoke tests, demo workflow, and JSON validation
  on pull requests with explicit read-only repository contents permission.
- `.gitignore` excludes generated reports, JSON outputs, JSONL logs, caches,
  virtual environments, and `.env` files.
- `docs/RELEASE_AND_TAG_GOVERNANCE.md` documents release-note PR expectations,
  tag timing, `vX.Y.Z` tag naming, generated-artifact exclusions, and manual
  GitHub setting checks.

Current public-repository posture still has important unknowns:

- Repository settings for branch protection and merge controls are not stored in
  the repository.
- GitHub security settings are not stored in the repository.
- `CODEOWNERS` is present, but enforcement depends on GitHub branch protection
  or ruleset settings that are not stored in repository files.
- The workflow declares `permissions: contents: read`. The repository or
  organization default Actions token permission setting still requires manual
  verification in GitHub.

## 3. File-Based Findings

| Area | Status | File-based finding | Recommendation |
| --- | --- | --- | --- |
| Branch protection / rulesets for `main` | not verifiable from repository files | No branch protection or ruleset configuration is present in files. | recommended now: maintainers should verify `main` protection in GitHub before more schema work. |
| Required status checks | not verifiable from repository files | `.github/workflows/tests.yml` defines a pull-request workflow, but repository files do not prove it is required before merge. | recommended now: require the `Tests / unittest` workflow, or the current equivalent check name, for `main`. |
| Pull request review requirements | not verifiable from repository files | `AGENTS.md` requires a pull request for every change, and the PR template supports review, but repository files do not prove review approval is required. | recommended now: require at least one approving review for `main`. |
| Conversation resolution before merge | not verifiable from repository files | No repository file can prove this GitHub setting is enabled. | recommended now: enable required conversation resolution for `main`. |
| Force-push and branch deletion protection | not verifiable from repository files | No repository file can prove these protections are enabled. | recommended now: block force pushes and deletion on `main`. |
| GitHub Actions token permissions / least privilege | present in repository | `.github/workflows/tests.yml` declares `permissions: contents: read` for the pull-request test workflow. The workflow only needs checkout/read access and does not need write permissions. | recommended now: manually verify the repository or organization default Actions token permission setting in GitHub. |
| CODEOWNERS need and ownership boundaries | present in repository | `.github/CODEOWNERS` routes all files, GitHub metadata, governance files, config, scripts, tests, and docs to `@akkbkk10`. Enforcement still depends on GitHub settings. | recommended now: manually verify CODEOWNERS review enforcement for `main`. |
| `SECURITY.md` / vulnerability reporting need | present in repository | `SECURITY.md` exists and tells reporters to use GitHub private vulnerability reporting if available, with a public-issue fallback that avoids sensitive details. It now clarifies public reporting boundaries and manual settings verification. | recommended now: verify whether private vulnerability reporting is enabled. |
| `CONTRIBUTING.md` / external contribution workflow need | present in repository | `CONTRIBUTING.md` covers narrow PRs, tests, generated artifacts, guardrails, secret hygiene, and owner-review expectations. | recommended later: expand only after verifying required checks and review rules. |
| Secret hygiene documentation | present in repository | `.gitignore` excludes `.env` and `.env.*`; `CONTRIBUTING.md`, `SECURITY.md`, and `docs/SECRET_HYGIENE_CHECKLIST.md` now document secret and generated-artifact hygiene. | recommended now: manually verify secret scanning and push protection. |
| Secret scanning / push protection | not verifiable from repository files | GitHub Advanced Security or repository security settings are not represented in files. | recommended now: manually verify secret scanning and push protection for the public repo. |
| Dependabot / dependency graph | not verifiable from repository files | No `.github/dependabot.yml` is present. The project currently uses only the Python standard library, but GitHub dependency graph and Dependabot settings still require manual verification. | recommended later: add Dependabot only if package manifests or GitHub Actions update policy warrant it. |
| Release and tag governance | present in repository | `docs/RELEASE_AND_TAG_GOVERNANCE.md` documents release-note PR rules, tag timing, tag naming, generated-artifact exclusions, and manual GitHub setting checks. `docs/V1_0_X_PATCH_RELEASE_CHECKLIST.md` documents release validation, tag creation, GitHub Release creation, and remote tag caution. | recommended now: manually verify tag protection or tag rulesets for `v*`. |
| Public no-investment-advice messaging | present in repository | `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`, architecture docs, scripts, and tests repeatedly preserve the no-investment-advice boundary. | recommended later: keep this language stable as schema work continues; review public-facing wording in every generated-output PR. |

Additional file-based observations:

- The CI workflow is scoped to `pull_request` and does not currently run on
  direct pushes to `main`. That is acceptable only if `main` direct pushes are
  blocked by branch protection. Because that setting is not verifiable from
  files, it should be manually checked.
- The pull request template explicitly asks reviewers to confirm no financial
  logic, DCF math, fair value logic, model rating/confidence/signal behavior,
  live fetching, investment advice, trading, or framework-specific business
  logic changed.
- Release documentation says not to create a tag until validation passes and
  the release commit on `main` is confirmed.

## 4. Settings Requiring Manual GitHub Verification

The following settings cannot be proven from the repository files and should be
checked in GitHub before more model-output schema work:

| Setting | Verification question | Recommended status |
| --- | --- | --- |
| Branch protection or ruleset for `main` | Is `main` protected by a branch protection rule or repository ruleset? | recommended now |
| Required status checks | Is the pull-request test workflow required before merge? | recommended now |
| Pull request reviews | Is at least one approving review required before merge? | recommended now |
| Stale review dismissal | Are approvals dismissed when relevant commits are pushed? | recommended later |
| Conversation resolution | Must all review conversations be resolved before merge? | recommended now |
| Force pushes | Are force pushes blocked on `main`? | recommended now |
| Branch deletion | Is deletion of `main` blocked? | recommended now |
| Linear history or merge strategy | Is the expected merge strategy documented and enforced? | recommended later |
| GitHub Actions default token permissions | Are default workflow token permissions read-only unless elevated per workflow? | recommended now |
| Secret scanning | Is secret scanning enabled for the public repository? | recommended now |
| Push protection | Is push protection enabled where available? | recommended now |
| Private vulnerability reporting | Is GitHub private vulnerability reporting enabled? | recommended now |
| Dependency graph | Is the dependency graph enabled? | recommended now |
| Dependabot alerts | Are Dependabot alerts enabled? | recommended now |
| Dependabot version updates | Are version updates needed despite the standard-library Python core? | recommended later |
| Tag protection or rulesets | Are release tags protected or governed? | recommended later |

This document intentionally does not claim any of these settings are enabled.

## 5. Security And Governance Gaps

The remaining concrete gaps are:

- Public-issue fallback is documented in `SECURITY.md`, but the preferred
  vulnerability channel depends on whether GitHub private vulnerability
  reporting is enabled.
- Required checks, reviews, conversation resolution, and branch protections for
  `main` are not verifiable from files.
- Secret scanning, push protection, dependency graph, Dependabot alerts, and tag
  protection or tag rulesets are not verifiable from files.
- CODEOWNERS enforcement is not verifiable from files because it depends on
  branch protection or ruleset settings.

These gaps matter more after the repository becomes public because external
contributors can now open issues and pull requests, public branches and tags
become part of user trust, and mistakes in security reporting or financial
output wording can be copied outside the maintainer context.

## 6. Recommended Next PR

Recommended next PR: resume generated-output schema hardening only after
maintainers manually verify public repository settings that cannot be proven from
files.

Scope:

- Continue with the next narrow generated-output schema candidate.
- Keep deterministic, evidence-based, no-investment-advice boundaries intact.
- Do not use schema work to change release governance, GitHub UI settings, live
  fetching, adapters, or financial behavior.

## 7. Suggested Next 2-4 PR Sequence

1. Resume generated-output schema hardening.
   Continue with the next model-output schema candidate only after the public
   repository settings and governance docs are checked.

## 8. Items Explicitly Out Of Scope

This assessment and the follow-up repository-file hardening do not:

- change runtime code
- change tests
- change schemas
- change CI workflows
- implement branch protection or repository rulesets
- enable GitHub private vulnerability reporting
- enable GitHub secret scanning or push protection
- enable Dependabot or dependency graph settings
- add dependencies
- add release notes
- create tags
- add model confidence schema work
- add model signal schema work
- change model rating thresholds
- change DCF logic
- change fair value logic
- change confidence logic
- change signal logic
- change CLI behavior
- add live market data fetching
- add web UI
- add adapters or framework code
- add MCP or A2A implementation
- rename packages
- add new companies
- add investment advice
- add trading, broker, order, or portfolio logic

