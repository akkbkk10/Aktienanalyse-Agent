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

Recommended next PR: open one narrowly scoped public-repository governance
hardening PR that adds ownership and reporting/process documents without
changing runtime behavior.

The next PR should add or update only repository-governance files:

- add `CODEOWNERS`
- tighten `SECURITY.md` with the verified vulnerability-reporting channel after
  maintainers check GitHub settings
- tighten `CONTRIBUTING.md` with the public contribution workflow, required
  checks, and guardrail review expectations
- document secret-hygiene expectations for contributors

This assessment finds several file-based controls already present, but the most
important public-repository controls for `main` are not verifiable from
repository files. Branch protection, required checks, pull request review rules,
conversation resolution, force-push protection, branch deletion protection,
secret scanning, push protection, dependency graph, Dependabot, and private
vulnerability reporting require manual verification in GitHub.

Do not resume model-output schema hardening until maintainers have at least
verified the public repository settings for `main` and opened the narrow
governance hardening PR above.

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
- `.github/pull_request_template.md` asks for changed files, tests, generated
  artifact review, and guardrail impact.
- `.github/ISSUE_TEMPLATE/` includes templates for bugs, documentation,
  features, guardrail/security review, release tracking, and schema proposals.
- `.github/workflows/tests.yml` runs the unit suite, targeted guardrail tests,
  validation commands, workflow smoke tests, demo workflow, and JSON validation
  on pull requests.
- `.gitignore` excludes generated reports, JSON outputs, JSONL logs, caches,
  virtual environments, and `.env` files.

Current public-repository posture still has important unknowns:

- Repository settings for branch protection and merge controls are not stored in
  the repository.
- GitHub security settings are not stored in the repository.
- `CODEOWNERS` is not present, so ownership boundaries are not enforceable from
  files.
- The workflow does not declare top-level or job-level `permissions:`, so the
  default `GITHUB_TOKEN` permission posture depends on repository or
  organization settings.

## 3. File-Based Findings

| Area | Status | File-based finding | Recommendation |
| --- | --- | --- | --- |
| Branch protection / rulesets for `main` | not verifiable from repository files | No branch protection or ruleset configuration is present in files. | recommended now: maintainers should verify `main` protection in GitHub before more schema work. |
| Required status checks | not verifiable from repository files | `.github/workflows/tests.yml` defines a pull-request workflow, but repository files do not prove it is required before merge. | recommended now: require the `Tests / unittest` workflow, or the current equivalent check name, for `main`. |
| Pull request review requirements | not verifiable from repository files | `AGENTS.md` requires a pull request for every change, and the PR template supports review, but repository files do not prove review approval is required. | recommended now: require at least one approving review for `main`. |
| Conversation resolution before merge | not verifiable from repository files | No repository file can prove this GitHub setting is enabled. | recommended now: enable required conversation resolution for `main`. |
| Force-push and branch deletion protection | not verifiable from repository files | No repository file can prove these protections are enabled. | recommended now: block force pushes and deletion on `main`. |
| GitHub Actions token permissions / least privilege | missing from repository | `.github/workflows/tests.yml` has no explicit `permissions:` block. The workflow appears read/test-only and does not need write access. | recommended now: in a later CI hardening PR, set least-privilege permissions such as read-only contents access. |
| CODEOWNERS need and ownership boundaries | missing from repository | No `CODEOWNERS` file is present. Ownership is implied by docs but not enforceable by GitHub review routing. | recommended now: add CODEOWNERS covering core scripts, config schemas, docs/governance, tests, and GitHub metadata. |
| `SECURITY.md` / vulnerability reporting need | present in repository | `SECURITY.md` exists and tells reporters to use GitHub private vulnerability reporting if available, with a public-issue fallback that avoids sensitive details. | recommended now: verify whether private vulnerability reporting is enabled and then make the reporting path more explicit. |
| `CONTRIBUTING.md` / external contribution workflow need | present in repository | `CONTRIBUTING.md` exists and covers narrow PRs, tests, generated artifacts, and guardrails. | recommended now: expand public workflow details only after verifying required checks and review rules. |
| Secret hygiene documentation | present in repository | `.gitignore` excludes `.env` and `.env.*`; `CONTRIBUTING.md` says not to commit generated artifacts or local environment files; `SECURITY.md` warns against posting secrets. | recommended now: add a short explicit section describing secrets, tokens, private source material, and what to do after accidental exposure. |
| Secret scanning / push protection | not verifiable from repository files | GitHub Advanced Security or repository security settings are not represented in files. | recommended now: manually verify secret scanning and push protection for the public repo. |
| Dependabot / dependency graph | not verifiable from repository files | No `.github/dependabot.yml` is present. The project currently uses only the Python standard library, but GitHub dependency graph and Dependabot settings still require manual verification. | recommended later: add Dependabot only if package manifests or GitHub Actions update policy warrant it. |
| Release and tag governance | present in repository | `docs/V1_0_X_PATCH_RELEASE_CHECKLIST.md` documents release validation, tag creation, GitHub Release creation, and remote tag caution. | recommended later: after branch protection is verified, document who may tag releases and whether tags are protected. |
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

The concrete gaps are:

- No `CODEOWNERS` file exists, so public review routing and ownership boundaries
  are not defined in a GitHub-enforceable way.
- `.github/workflows/tests.yml` does not declare explicit least-privilege
  `permissions:`.
- Public-issue fallback is documented in `SECURITY.md`, but the preferred
  vulnerability channel depends on whether GitHub private vulnerability
  reporting is enabled.
- Secret hygiene exists across `.gitignore`, `CONTRIBUTING.md`, and
  `SECURITY.md`, but there is no single explicit contributor-facing secret
  hygiene checklist.
- Required checks, reviews, conversation resolution, and branch protections for
  `main` are not verifiable from files.
- Secret scanning, push protection, dependency graph, Dependabot alerts, and
  tag protections are not verifiable from files.

These gaps matter more after the repository becomes public because external
contributors can now open issues and pull requests, public branches and tags
become part of user trust, and mistakes in security reporting or financial
output wording can be copied outside the maintainer context.

## 6. Recommended Next PR

Recommended next PR: add public repository governance ownership and reporting
hardening.

Scope:

- Add `CODEOWNERS` for repository governance, GitHub metadata, deterministic
  core scripts, config schemas, tests, docs, and data samples.
- Update `SECURITY.md` only after maintainers verify whether private
  vulnerability reporting is enabled.
- Update `CONTRIBUTING.md` with public contribution expectations, required
  checks once verified, and explicit secret-hygiene instructions.
- Keep the PR documentation/governance-only.

Do not include workflow permission edits in this next PR. Keep CI hardening as a
separate follow-up so review stays narrow and no workflow behavior changes are
mixed with ownership/reporting documentation.

## 7. Suggested Next 2-4 PR Sequence

1. Public repository governance ownership and reporting hardening.
   Add `CODEOWNERS`; update `SECURITY.md` and `CONTRIBUTING.md`; document secret
   hygiene. No runtime, schema, test, or CI changes.

2. GitHub Actions least-privilege hardening.
   Add explicit workflow `permissions:` and keep CI behavior otherwise
   unchanged. Verify the same test count and workflow behavior.

3. Release and tag governance documentation.
   Document who can create release tags, whether tag protection or rulesets are
   expected, and how release notes should state no financial behavior changes.

4. Resume generated-output schema hardening.
   Continue with the next model-output schema candidate only after the public
   repository settings and governance docs are checked.

## 8. Items Explicitly Out Of Scope

This assessment does not:

- change runtime code
- change tests
- change schemas
- change CI workflows
- add `CODEOWNERS`
- add `SECURITY.md`
- add `CONTRIBUTING.md`
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

