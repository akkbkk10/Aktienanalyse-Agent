# v1.0.x Patch Release Checklist

Use this checklist for future v1.0.x maintenance releases. Patch releases should
be small, reviewable, and focused on documentation, tests, guardrails,
repository hygiene, or bug fixes that do not change financial methodology unless
explicitly reviewed.

Do not create the release tag until all validation steps pass and the release
commit on `main` is confirmed.

Use `.github/ISSUE_TEMPLATE/release_tracking.md` to track release status before
tagging.

## 1. Confirm PRs Are Merged Into Main

- Confirm all intended maintenance PRs are merged.
- Confirm no feature PR is accidentally included.
- Confirm scope exclusions still hold:
  - no price targets
  - no buy/sell/hold recommendations
  - no personal investment advice
  - no live fetching unless explicitly implemented and validated in a future
    adapter
  - no trading, broker/order, or portfolio logic

PowerShell:

```powershell
git fetch origin main --prune
git log --oneline origin/main -5
```

Shell:

```bash
git fetch origin main --prune
git log --oneline origin/main -5
```

## 2. Pull A Fresh Main Checkout

PowerShell:

```powershell
Set-Location "C:\path\to\Aktienanalyse-Agent"
git switch main
git pull --ff-only origin main
git status --short --branch
```

Shell:

```bash
cd /path/to/Aktienanalyse-Agent
git switch main
git pull --ff-only origin main
git status --short --branch
```

Expected status:

```text
## main...origin/main
```

with no modified or untracked files.

## 3. Run The Full Test Suite

PowerShell and shell:

```bash
python -m unittest discover -s tests
```

Expected result:

```text
OK
```

Record the test count in the release notes when it changes.

## 4. Run The v1.0 Demo Validation

Use an ignored `reports/tmp_*` path.

PowerShell:

```powershell
python scripts\run_v1_0_demo.py --reports-dir reports\tmp_v1_0_x_patch_validation
```

Shell:

```bash
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_0_x_patch_validation
```

Expected result:

- `demo_completed` is `true`
- NVDA, AMD, and TSMC are listed in `successful_runs`
- reports, summaries, DCF outputs, fair value per share outputs, model rating
  outputs, model confidence outputs, model signal outputs, and audit logs are
  generated under the temporary reports directory

## 5. Check Git Status After Generated Reports

PowerShell and shell:

```bash
git status --short --branch
```

Generated reports must not appear as tracked or untracked changes. If they do,
stop and inspect `.gitignore` before tagging.

## 6. Review Generated Output Diffs

Use `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md` when inspecting generated artifacts.

Confirm:

- no price target language
- no buy/sell/hold recommendations
- no personal investment advice
- no broker/order instructions
- no automated trading language
- no invented sources
- no unsourced financial figures
- no unsupported live-data claims
- assumptions remain clearly separated from facts and calculated outputs
- example/manual-review assumptions keep active model signals unavailable

Generated artifacts are review evidence only. Do not commit them.

## 7. Confirm Guardrails

Use `docs/GUARDRAIL_SECURITY_TEST_PLAN.md` for the release guardrail review.

Confirm the release does not add:

- live data fetching
- runtime agent framework dependencies
- framework-specific business logic inside the deterministic core
- price targets
- buy/sell/hold recommendations
- personal investment advice
- broker/order behavior
- automated trading logic

## 8. Prepare Release Notes

- Add or update the relevant `docs/V1_0_X_RELEASE_NOTES.md` file.
- Summarize merged PRs as maintenance, hardening, docs, or tests.
- Clearly state whether financial logic changed.
- If financial logic did not change, state that DCF math, fair value logic,
  model rating, model confidence, and model signal behavior are unchanged.
- Include validation commands and results.
- Include upgrade notes from the previous patch release.

## 9. Create An Annotated Git Tag

Replace `v1.0.x` with the exact patch version.

PowerShell and shell:

```bash
git tag -a v1.0.x -m "Release v1.0.x"
```

Verify the tag before pushing:

```bash
git show --stat v1.0.x
```

## 10. Push The Tag

PowerShell and shell:

```bash
git push origin v1.0.x
```

## 11. Create The GitHub Release

Create the release from the pushed tag in GitHub.

Checklist:

- title matches the tag, for example `v1.0.x`
- release notes link to the matching docs release notes
- summary says whether financial logic changed
- validation commands and results are included
- generated reports are not attached unless intentionally prepared as a
  separate review artifact

## 12. Verify The Tag Points To The Intended Commit

PowerShell and shell:

```bash
git fetch origin --tags
git rev-list -n 1 v1.0.x
git rev-parse origin/main
```

The two commit hashes should match for a release tagged from the latest `main`.

Optional GitHub CLI check:

```bash
gh release view v1.0.x
```

## Troubleshooting

### You Are In `C:\WINDOWS\system32`

PowerShell sometimes opens outside the repository. Move to the repository first:

```powershell
Set-Location "C:\path\to\Aktienanalyse-Agent"
git status --short --branch
```

### Path Not Found

Confirm the repository path exists:

```powershell
Test-Path "C:\path\to\Aktienanalyse-Agent"
```

Shell:

```bash
test -d /path/to/Aktienanalyse-Agent && echo "found"
```

### Not A Git Repository

Confirm you are inside the repository root:

```bash
git rev-parse --show-toplevel
```

If this fails, change into the `Aktienanalyse-Agent` directory and retry.

### Local Tag Already Exists

Inspect it before deleting anything:

```bash
git show --stat v1.0.x
```

If the local tag is wrong and has not been pushed, delete and recreate it:

```bash
git tag -d v1.0.x
git tag -a v1.0.x -m "Release v1.0.x"
```

### Remote Tag Already Exists

Do not overwrite a published release tag casually. Confirm whether the release
already exists:

```bash
git ls-remote --tags origin v1.0.x
gh release view v1.0.x
```

If the remote tag is wrong, document the issue and coordinate a maintainer
decision before deleting or replacing it.

### Generated Reports Appear In Git Status

Stop before committing. Confirm the generated files are under `reports/` or
another ignored temporary path:

```bash
git status --short
git check-ignore -v reports/tmp_v1_0_x_patch_validation
```

If generated artifacts are not ignored, update `.gitignore` in a separate small
PR or move the generated output to an ignored `reports/tmp_*` directory.
