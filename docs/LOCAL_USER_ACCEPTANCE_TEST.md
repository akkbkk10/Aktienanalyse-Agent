# Local User Acceptance Test

This guide gives maintainers and reviewers a local, end-to-end acceptance check
for the current deterministic CLI workflow. It documents current behavior only.
It does not add runtime code, tests, schemas, config changes, generated reports,
adapters, live data, MCP/A2A, web UI, desktop app behavior, release notes, tags,
or GitHub Releases.

The current user-facing path is local command-line execution. There is no web
UI, desktop app, installed Windows app, adapter runtime, live market data
fetching, provider API integration, MCP/A2A runtime integration, broker/order
execution, trading logic, portfolio automation, price target output,
buy/sell/hold recommendation, or personal investment advice.

## Purpose

Use this guide when a reviewer wants to confirm that a fresh checkout can run
the deterministic sample workflow and produce inspectable local artifacts. This
guide complements automated tests; it does not replace the test suite or release
validation checklists.

## Open The Project Locally

From a fresh checkout or local workspace, open a shell in the repository root:

```powershell
cd Aktienanalyse-Agent
python --version
git status --short
```

Expected result:

- Python is available.
- The working tree is clean before the acceptance run.
- The current workflow is CLI-only.

## Run The Test Suite

Run the full unit suite:

```powershell
python -m unittest discover -s tests
```

Expected result:

- The suite passes.
- At the time this guide was added, the suite contains 231 tests.

If tests fail before local acceptance review, stop and investigate the failure
before inspecting generated artifacts.

## Run The Deterministic Demo

Run the current v1.0 sample-company demo into an ignored temporary reports
directory:

```powershell
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_local_user_acceptance
```

Expected result:

- The command completes successfully.
- Output artifacts are written under `reports/tmp_local_user_acceptance/`.
- Generated artifacts remain ignored by git and must not be committed.

The demo covers the supported sample tickers `NVDA`, `AMD`, and `TSMC` using
stored sample data and explicit assumptions. It does not fetch live data.

## Inspect Generated Artifacts

Inspect the generated reports directory:

```powershell
Get-ChildItem -Recurse reports/tmp_local_user_acceptance
```

Expected top-level artifact:

- `reports/tmp_local_user_acceptance/audit_log.jsonl`

Expected per-ticker artifacts under `NVDA/`, `AMD/`, and `TSMC/`:

- `<TICKER>_fact_report.md`
- `<TICKER>_analysis_summary.json`
- `<TICKER>_dcf_output.json`
- `<TICKER>_fair_value_per_share_output.json`
- `<TICKER>_model_rating_output.json`
- `<TICKER>_model_confidence_output.json`
- `<TICKER>_model_signal_output.json`

Use `docs/REPORT_ARTIFACT_CONTRACT.md` for the durable artifact layout and
`docs/ARCHITECTURE_VISUAL_OVERVIEW.md` for the current architecture map.

For a future manual trial with a new explicit local company-data package, use
`docs/OFFLINE_COMPANY_DATA_TRIAL_PLAN.md`. The local UAT guide validates the
current supported demo path; the offline trial plan documents the additional
input-package and manual-review checks needed before a new company can be
considered for onboarding.

## Review Output Boundaries

For each ticker, inspect the fact report and structured summary:

```powershell
Get-Content reports/tmp_local_user_acceptance/NVDA/NVDA_fact_report.md
Get-Content reports/tmp_local_user_acceptance/NVDA/NVDA_analysis_summary.json
```

Repeat for `AMD` and `TSMC` as needed.

Confirm that generated artifacts:

- separate facts, assumptions, calculated outputs, missing data, warnings, and
  source references
- expose missing data and warnings instead of hiding them
- preserve source references and metric identifiers where applicable
- show model rating, model confidence, and model signal only as
  non-personalized model artifacts
- keep generated reports and summaries under the ignored reports directory

## Guardrails To Verify

Acceptance review should confirm that generated artifacts do not contain or
imply:

- fabricated financial data or invented source claims
- hidden live-data fetching
- automatic market-price refreshes inside core modules
- buy/sell/hold recommendations
- price targets
- personal investment advice
- trading instructions
- broker/order behavior
- portfolio automation

If a generated artifact appears to violate one of these guardrails, stop and
record the exact file, section, and wording for review. Do not fix generated
wording through this guide.

## Deferred Items To Keep Out Of Scope

The following remain deferred and should not be treated as part of local user
acceptance:

- web UI
- desktop app
- adapter implementation
- live market data fetching
- provider APIs or credentials
- MCP or A2A runtime integration
- methodology implementation
- generated artifact manifest implementation
- new financial logic
- new companies

`docs/ADAPTER_IMPLEMENTATION_READINESS_ASSESSMENT.md` records that adapter work
is ready only for mock/offline adapter planning. `docs/MOCK_OFFLINE_ADAPTER_CONSUMER_DECISION.md`
records that no concrete first mock/offline adapter consumer exists yet.

## Cleanup

Generated reports are ignored by git, but reviewers can remove the temporary
acceptance directory after inspection:

```powershell
Remove-Item -Recurse -Force reports/tmp_local_user_acceptance
```

Before opening or merging a PR, confirm the working tree contains only intended
source-controlled changes:

```powershell
git status --short
```

Generated artifacts under `reports/tmp_*` must remain uncommitted.
