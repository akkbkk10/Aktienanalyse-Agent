# Report Artifact Contract

This document describes the current generated artifact layout for the
deterministic v1.0/v1.1 baseline. It documents existing behavior only. It does
not define a new schema, add new generated artifacts, or change runtime paths.

Source of truth for this contract:

- `scripts/run_v1_0_demo.py`
- `scripts/run_batch_analysis.py`
- `scripts/run_analysis.py`
- `scripts/generate_report.py`
- `tests/test_run_v1_0_demo.py`

Generated artifacts must remain under ignored `reports/` paths and must not be
committed.

## v1.0 Demo Layout

The v1.0 demo writes artifacts under the configured `--reports-dir` path. The
default path is:

```text
reports/v1_0_demo/
```

When a custom reports directory is supplied, the same layout is rooted under
that directory:

```text
<reports-dir>/
  audit_log.jsonl
  NVDA/
    NVDA_fact_report.md
    NVDA_analysis_summary.json
    NVDA_dcf_output.json
    NVDA_fair_value_per_share_output.json
    NVDA_model_rating_output.json
    NVDA_model_confidence_output.json
    NVDA_model_signal_output.json
  AMD/
    AMD_fact_report.md
    AMD_analysis_summary.json
    AMD_dcf_output.json
    AMD_fair_value_per_share_output.json
    AMD_model_rating_output.json
    AMD_model_confidence_output.json
    AMD_model_signal_output.json
  TSMC/
    TSMC_fact_report.md
    TSMC_analysis_summary.json
    TSMC_dcf_output.json
    TSMC_fair_value_per_share_output.json
    TSMC_model_rating_output.json
    TSMC_model_confidence_output.json
    TSMC_model_signal_output.json
```

The supported v1.0 demo tickers are currently `NVDA`, `AMD`, and `TSMC`.

## Stable Contract Expectations

These expectations are protected by current v1.0 demo tests:

- `run_v1_0_demo.run_demo(reports_dir=...)` writes the shared audit log to
  `<reports-dir>/audit_log.jsonl`.
- Each successful ticker has a per-ticker directory under `<reports-dir>/`.
- Each per-ticker artifact path returned by the demo exists.
- Each required per-ticker artifact path is inside that ticker's directory.
- Generated artifacts are written under the configured reports directory, not a
  machine-specific absolute path.

Required per-ticker artifact keys returned by the v1.0 demo are:

| Result key | Current path pattern | Purpose |
| --- | --- | --- |
| `report_path` | `<reports-dir>/<TICKER>/<TICKER>_fact_report.md` | Fact-only Markdown report. |
| `analysis_summary_path` | `<reports-dir>/<TICKER>/<TICKER>_analysis_summary.json` | Structured analysis summary. |
| `dcf_output_path` | `<reports-dir>/<TICKER>/<TICKER>_dcf_output.json` | Deterministic DCF scenario output. |
| `fair_value_per_share_output_path` | `<reports-dir>/<TICKER>/<TICKER>_fair_value_per_share_output.json` | Fair value per share model output. |
| `model_rating_output_path` | `<reports-dir>/<TICKER>/<TICKER>_model_rating_output.json` | Non-personalized model rating output. |
| `model_confidence_output_path` | `<reports-dir>/<TICKER>/<TICKER>_model_confidence_output.json` | Model quality confidence output. |
| `model_signal_output_path` | `<reports-dir>/<TICKER>/<TICKER>_model_signal_output.json` | Non-personalized model signal output. |
| `audit_log_path` | `<reports-dir>/audit_log.jsonl` | Shared audit log for the demo run. |

## Implementation Details

These details describe current behavior but should not be treated as additional
stable artifact requirements without a follow-up contract update:

- The v1.0 demo creates runtime company context data under
  `<reports-dir>/companies/`.
- Batch runs may create research queue files under the configured reports
  directory.
- The demo result also includes a `manual_review_checklist` path pointing to
  `docs/V1_0_TEST_PLAN.md`.
- The top-level `generated_file_paths.audit_log_path` is derived from the first
  successful ticker's audit log reference.

## Test Protection

`tests/test_run_v1_0_demo.py` protects the current contract by running the demo
with temporary reports directories and verifying:

- the demo completes for `NVDA`, `AMD`, and `TSMC`
- the shared audit log exists at the configured reports directory root
- per-ticker artifact directories exist
- fact report, analysis summary, DCF output, fair value per share output, model
  rating output, model confidence output, and model signal output exist for each
  ticker
- generated artifact paths stay inside the configured reports directory
- generated JSON artifacts preserve current source-reference evidence fields in
  DCF, fair value per share, model rating, model confidence, and analysis
  summary outputs

If this contract changes, update this document and the related tests in the
same PR. Do not change artifact names or locations through an unrelated feature
PR.

## Review Guidance

When reviewing changes that can affect generated artifacts:

- run the full tests
- run the v1.0 demo into an ignored `reports/tmp_*` directory
- confirm generated artifacts remain untracked
- inspect the fact report, structured summary, DCF output, fair value output,
  model rating output, model confidence output, model signal output, and audit
  log for affected tickers
- confirm generated outputs still follow guardrails from
  `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`
