# Offline Company Data Trial Plan

This document maps the successful local UAT evidence checks to a future first
offline company-data trial. It documents readiness and boundaries only. It does
not add runtime code, schemas, config changes, tests, generated reports,
adapters, live data, provider APIs, MCP/A2A, web UI, desktop app behavior,
methodology implementation, release notes, tags, or GitHub Releases.

The current project is ready for a **manual offline company-data trial** only
when explicit local input files are prepared and validated first. It is not
ready for live data, provider-backed ingestion, adapter runtime behavior, or an
automated new-company onboarding pipeline.

## Readiness Decision

Decision: **ready for a manual offline trial with explicit local files**.

The trial may use the existing deterministic CLI path to test a new company data
package locally, but it must not treat that company as supported until the
normal onboarding review is complete.

The trial is useful for checking whether a proposed company data package can
move through the same evidence, validation, artifact, audit-log, and guardrail
surface as the current NVDA, AMD, and TSMC demo.

## Evidence Mapping From Local UAT

The current local UAT guide validates the existing supported sample flow:

- run the full unit suite
- run `scripts/run_v1_0_demo.py` for `NVDA`, `AMD`, and `TSMC`
- confirm expected generated artifacts exist under an ignored `reports/tmp_*`
  directory
- inspect reports, summaries, model outputs, source references, and audit logs
- verify no live data, advice, price targets, trading instructions, or
  portfolio automation appear
- clean up temporary generated artifacts

Automated tests already cover much of this surface:

| UAT check | Current automated coverage | Manual review still needed |
| --- | --- | --- |
| Demo completes for supported sample tickers | `tests/test_run_v1_0_demo.py` | Confirm local command output and environment. |
| Required artifact paths exist | `tests/test_run_v1_0_demo.py` | Inspect actual temporary directory when reviewing locally. |
| Generated JSON contracts validate | `tests/test_run_v1_0_demo.py` and per-output contract tests | Review changed artifact meaning if a data package changes. |
| Source-reference evidence remains visible | `tests/test_run_v1_0_demo.py`, `tests/test_run_analysis.py` | Spot-check report and summary readability. |
| Audit log envelope and evidence context exist | `tests/test_write_audit_log.py`, `tests/test_run_analysis.py` | Confirm generated JSONL is present and readable. |
| Forbidden-output phrasing is absent | `tests/test_forbidden_output_regression.py` | Inspect any new wording or unexpected warnings. |
| Generated artifacts are cleaned up | Git status check | Remove local `reports/tmp_*` trial output. |

Manual review remains necessary because a new company data package can introduce
new source names, periods, units, warnings, assumption wording, or missing-data
states that tests cannot judge semantically without a reviewed fixture.

## Required Offline Input Package

A first offline trial should use a short-lived local branch or local workspace
and explicit files only. Before running the workflow, prepare:

- `data/<ticker_lower>_sample_metrics.json`
- `data/companies/<TICKER>/dcf_assumptions.json`, if DCF is part of the trial
- a watchlist entry for `<TICKER>` in `config/watchlist.json`
- optionally, a generated context under `data/companies/<TICKER>/context.json`
  after source validation passes

Use `docs/COMPANY_ONBOARDING_GUIDE.md` as the source checklist for required
metrics, DCF assumptions, watchlist fields, and validation commands.

For the first planned ASML trial, use
`docs/ASML_OFFLINE_TRIAL_SOURCE_PACKAGE_PLAN.md` before adding any ASML data.

Every financial metric must include source metadata required by `AGENTS.md`,
`docs/DATA_CONTRACT_REVIEW_CHECKLIST.md`, and
`docs/SCHEMA_FIELD_REFERENCE.md`, including:

- `metric_id`
- source URL
- source date
- unit
- period
- confidence
- last verified date
- accounting basis and statement type where applicable

Market price records must remain stored snapshots with explicit provider,
retrieval method, `as_of_datetime`, and `fetched_at` fields. They must not be
live quotes fetched inside the deterministic core.

## Trial Commands

Run validation first:

```powershell
python scripts/validate_company_onboarding.py TICKER --metrics-path data/ticker_sample_metrics.json --dcf-assumptions-path data/companies/TICKER/dcf_assumptions.json
```

If validation passes, run a local analysis into an ignored reports directory:

```powershell
python scripts/run_analysis.py TICKER --source-data-path data/ticker_sample_metrics.json --generate-report --generate-summary --run-dcf --dcf-assumptions-path data/companies/TICKER/dcf_assumptions.json --reports-dir reports/tmp_offline_company_trial/TICKER --context-root reports/tmp_offline_company_trial/companies --audit-log-path reports/tmp_offline_company_trial/audit_log.jsonl --markdown-queue-path reports/tmp_offline_company_trial/research_queue.md --json-queue-path reports/tmp_offline_company_trial/research_queue.json
```

Use a `reports/tmp_*` directory so generated artifacts stay ignored and can be
removed after review.

If the company has no reviewed DCF assumptions yet, run without `--run-dcf` and
without the DCF assumptions argument. Missing or unavailable valuation outputs
are acceptable during an offline trial when they are explicit and visible.

## Manual Inspection Checklist

Inspect the generated output and confirm:

- source validation passed, or failures are clear and fail closed
- generated reports and summaries keep facts, assumptions, calculated outputs,
  missing data, warnings, and source references separate
- generated JSON artifacts are readable
- the audit log contains the stable envelope fields documented in
  `docs/AUDIT_LOG_EXPECTATIONS.md`
- source references preserve source URL, source date, unit, period, confidence,
  and metric identifiers where applicable
- market price evidence is a stored snapshot, not a hidden live refresh
- model rating, model confidence, and model signal remain non-personalized
  model artifacts
- generated artifacts remain under `reports/tmp_*`

Also confirm outputs do not contain or imply:

- fabricated financial data or invented source claims
- hidden live-data fetching
- provider API calls or credentials
- buy/sell/hold recommendations
- price targets
- personal investment advice
- trading instructions
- broker/order behavior
- portfolio automation

## Cleanup

After inspection, remove temporary generated artifacts:

```powershell
Remove-Item -Recurse -Force reports/tmp_offline_company_trial
git status --short
```

The final status should show only intentional source-controlled changes, if any.
Generated reports must not be committed.

## When To Promote Beyond Trial

An offline trial may become a normal onboarding PR only after:

- the source data package passes `validate_company_onboarding.py`
- the generated outputs are reviewed locally
- assumptions are clearly labeled and reviewable
- missing data and warnings are visible
- no guardrail wording issue is found
- maintainers decide the company should become a supported sample ticker

Promotion may require source-data, assumptions, watchlist, context, docs, and
tests in a dedicated onboarding PR. That is separate from this trial plan.

## Explicit Non-Goals

This plan does not authorize:

- runtime code changes
- schema or config changes outside a reviewed onboarding PR
- generated reports committed to the repository
- adapter implementation
- live market data fetching
- provider APIs or credentials
- MCP/A2A runtime integration
- web UI or desktop app behavior
- methodology implementation
- generated artifact manifest implementation
- financial logic changes
- valuation formula changes
- model rating, confidence, or signal behavior changes
- report wording changes
- buy/sell/hold advice
- price targets
- trading logic
- portfolio automation
- personal investment advice

