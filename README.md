# Aktienanalyse Agent

Initial scaffold for an agentic stock analysis system.

The first implementation slice focuses on evidence discipline:

- Validate financial metrics before they can be used.
- Require source metadata for every financial number.
- Keep facts, assumptions, and opinions separate.
- Keep GAAP and Non-GAAP metrics explicitly labeled.

Price target, buy/sell/hold recommendation, personal investment advice, live data fetching, and automated trading logic are intentionally not implemented.

## Repository Layout

- `AGENTS.md` - mandatory rules for agents and contributors.
- `LICENSE` - Apache License 2.0.
- `CONTRIBUTING.md` - contribution workflow and project guardrails.
- `SECURITY.md` - vulnerability reporting and security scope.
- `CODE_OF_CONDUCT.md` - respectful collaboration expectations.
- `.github/` - CI workflow plus issue and pull request templates.
- `config/` - schemas and validation rules.
- `config/watchlist.json` - required research coverage by ticker.
- `agents/` - documentation/contracts for the Hub-and-Spoke supervisor and specialized worker roles.
- `docs/GUARDRAIL_SECURITY_TEST_PLAN.md` - guardrail and security checklist for core and future adapter work.
- `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md` - review guide for generated reports, summaries, model outputs, and audit logs.
- `docs/ADAPTER_PROPOSAL_CHECKLIST.md` - pre-implementation checklist for future adapter and framework proposals.
- `docs/ADAPTER_RISK_REGISTER_TEMPLATE.md` - risk register template for future adapter proposals.
- `docs/ADAPTER_DECISION_RECORD_TEMPLATE.md` - decision record template for accepted, rejected, or deferred adapter proposals.
- `docs/DATA_CONTRACT_REVIEW_CHECKLIST.md` - field-level traceability checklist for future schemas and adapter outputs.
- `scripts/` - executable helper scripts.
- `tests/` - test suite.
- `data/` - raw and intermediate input data.
- `data/companies/<TICKER>/context.json` - persistent company context files.
- `reports/` - generated reports.
- `audit_log.jsonl` - append-only audit log for reproducible analysis runs.
- `research_queue.md` - queue of research requests.
- `research_queue.json` - structured queue used for duplicate detection and automation.

## Run Tests

The project currently uses only the Python standard library.

```powershell
python -m unittest discover -s tests
```

GitHub Actions runs the same command on every pull request.

CI also runs the v1.0.0 demo:

```bash
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_ci_v1_0_demo
```

## Run v0.1 Demo

Run the complete v0.1 NVDA workflow with one command:

```powershell
python scripts/run_v0_1_demo.py
```

The demo runs validation, company context build/load, research gap detection, ratio calculation, valuation readiness, DCF, fact-only report generation, analysis summary generation, and audit logging. It prints generated file paths and writes runtime artifacts under `reports/v0_1_demo/`, which is ignored by git.

## Run v1.0.0 Demo

Run the full v1.0.0 sample-company workflow for NVDA, AMD, and TSMC with one command:

```powershell
python scripts/run_v1_0_demo.py
```

The demo generates reports, summaries, DCF outputs, fair value per share outputs,
model ratings, model confidence outputs, model signals, and an audit log under
`reports/v1_0_demo/`, which is ignored by git. Use
`docs/V1_0_TEST_PLAN.md` for the manual review checklist.

Release notes:

- `docs/V1_0_RELEASE_NOTES.md`
- `docs/V1_0_1_RELEASE_NOTES.md`
- `docs/V1_0_2_RELEASE_NOTES.md`
- `docs/V1_0_X_PATCH_RELEASE_CHECKLIST.md`

## v0.2 Batch Workflow

Run the deterministic workflow for one or more tickers:

```powershell
python scripts/run_batch_analysis.py NVDA MSFT --generate-report --generate-summary --run-dcf
```

The batch runner executes the existing per-ticker workflow: validation, context, research gaps, ratios, readiness, optional DCF, optional report, optional summary, and audit log. It returns structured JSON with tickers processed, successful runs, failed runs, output paths by ticker, and warnings by ticker.

Run the supported NVDA + AMD + TSMC sample batch:

```powershell
python scripts/run_batch_analysis.py NVDA AMD TSMC --generate-report --generate-summary --run-dcf
```

NVDA, AMD, and TSMC are currently the fully working sample tickers. Other tickers fail cleanly unless their source data and assumptions are added.

Sample data and any future live data ingestion must remain separate. Batch runs process each ticker independently, and a missing or invalid ticker must not block successful NVDA, AMD, or TSMC runs. Generated model outputs are analysis artifacts only and are not personal investment advice.

## How To Add A New Company

Use the onboarding templates and checklist before adding a new supported ticker:

- `docs/COMPANY_ONBOARDING_GUIDE.md`
- `data/company_template/sample_metrics_template.json`
- `data/company_template/dcf_assumptions_template.json`

Create sourced sample metrics, add DCF assumptions, add a watchlist entry, and
run the onboarding validator:

```bash
python scripts/validate_company_onboarding.py TICKER --metrics-path data/ticker_sample_metrics.json --dcf-assumptions-path data/companies/TICKER/dcf_assumptions.json
```

Windows PowerShell accepts backslash paths as well:

```powershell
python scripts/validate_company_onboarding.py TICKER --metrics-path data\ticker_sample_metrics.json --dcf-assumptions-path data\companies\TICKER\dcf_assumptions.json
```

TSMC was added through this workflow with sourced sample metrics in
`data/tsmc_sample_metrics.json`, a persistent context at
`data/companies/TSMC/context.json`, and example DCF assumptions at
`data/companies/TSMC/dcf_assumptions.json`.

The validator checks required financial metrics, `metric_id` presence, source
metadata, market price snapshot fields, share count availability, DCF
assumptions, watchlist entry, and company context generation. It does not fetch
live data and does not create recommendations, price targets, personal investment
advice, or trading logic.

## Setup

```powershell
git clone <repo-url>
cd Aktienanalyse-Agent
python --version
python -m unittest discover -s tests
```

Use Python 3.12 or newer for local development.

Most examples use forward-slash paths so they work in macOS, Linux, Git Bash,
and PowerShell. Existing Windows backslash examples are equivalent.

## Agent Contracts And Future Adapters

The deterministic Python scripts are the core business logic. Files under
`agents/` document the Hub-and-Spoke model: the orchestrator/supervisor
coordinates specialized worker contracts for validation, context, gaps, ratios,
readiness, DCF, reports, summaries, and audit outputs.

These agent files are not runtime framework code. Future MCP, A2A, LangChain,
CrewAI, OpenAI Agents SDK, or other framework integrations should be adapter
layers around the deterministic core, not replacements for source validation,
traceability, audit logging, or guardrails.

## Validate A Metrics File

```powershell
python scripts/validate_sources.py path\to\metrics.json
```

The input file may contain either a single JSON object or a list of objects.

## Source Validation Workflow

Validate sourced financial metrics before using them in company contexts:

```powershell
python scripts/validate_sources.py path\to\metrics.json
```

Create research queue entries for invalid, stale, missing, or conflicting source evidence:

```powershell
python scripts/validate_sources.py path\to\metrics.json --queue-errors
```

The source validation agent checks:

- allowed source types: SEC filing, investor relations, earnings release, annual report
- absolute HTTPS source URLs
- ISO `source_date` and `last_verified` values
- required confidence levels
- explicit GAAP and Non-GAAP labeling
- stale source verification
- conflicting values for the same ticker, metric, period, and accounting basis

Validation queue entries are written to `research_queue.json` and mirrored to `research_queue.md`. This workflow creates source research tasks only; it does not create valuation, DCF, ratio analysis, price targets, recommendations, investment advice, or memo output.

## Research Queue Workflow

Create a manual research request:

```powershell
python scripts/create_research_request.py --company "NVIDIA Corporation" --ticker NVDA --question "Find the latest annual report source URL."
```

Create research requests from validation errors:

```powershell
python scripts/create_research_request.py --from-validation-errors path\to\metrics.json
```

The script writes to both `research_queue.json` and `research_queue.md`. The JSON queue is the structured source for duplicate detection; the markdown queue is a readable log for review. Duplicate requests are detected by a stable request ID and are not appended twice.

Validation-generated queue items are for missing or invalid evidence only. They must not trigger valuation, DCF, ratio analysis, or memo generation.

## Sample Data

`data/nvda_sample_metrics.json` contains sourced FY2025 sample metrics for NVIDIA Corporation (`NVDA`). It exists only to exercise the evidence schema and validation flow. It must not be used for valuation, DCF, price targets, or investment recommendations.

The NVDA sample also includes sourced FY2024 and FY2025 inputs needed for deterministic ratio coverage: revenue, gross profit, operating income, net income, and free cash flow. Free cash flow is labeled Non-GAAP because NVIDIA presents it as a non-GAAP financial measure.

Every financial metric includes a stable `metric_id` technical identifier. Contexts,
ratio outputs, DCF source references, reports, and summaries use `metric_id` to
trace calculations back to the exact sourced metric record without relying only on
display names.

Share count inputs are supported as sourced `share_count` metric records. These
records are preserved in company context and can be used with DCF scenario output
to calculate deterministic fair value per share.

## Company Context Workflow

Build a persistent company context from validated metric records:

```powershell
python scripts/build_company_context.py data\nvda_sample_metrics.json
```

The builder writes `data/companies/<TICKER>/context.json`. A company context contains:

- `schema_version`
- `ticker`
- `company_name`
- `last_updated`
- `metrics`
- per-metric `source_metadata`

The builder validates source metadata before writing the context. Invalid or missing source metadata fails closed and does not create a valuation, DCF, ratio analysis, or memo.

## Research Gap Workflow

Detect research gaps from the watchlist and company contexts:

```powershell
python scripts/detect_research_gaps.py
```

The research gap agent compares `config/watchlist.json` with `data/companies/<TICKER>/context.json` and detects:

- missing required metrics
- stale metrics
- missing source metadata
- low-confidence data

Detected gaps are automatically written to `research_queue.json` and mirrored to `research_queue.md` through the existing queue system. Duplicate queue entries are not appended twice.

This workflow creates research follow-up tasks only. It does not create valuation, DCF, ratio analysis, price targets, recommendations, or memo output.

## Ratio Calculation Workflow

Calculate deterministic ratios from a validated company context:

```powershell
python scripts/calculate_ratios.py NVDA
```

The ratio calculation agent can calculate only:

- `gross_margin`
- `operating_margin`
- `net_margin`
- `free_cash_flow_margin`
- `revenue_growth` when prior-period revenue exists

Each ratio output includes ticker, ratio name, value, formula, input metrics used, source metric references, period, and confidence. If required input metrics are missing, the script creates research queue entries in `research_queue.json` and mirrors them to `research_queue.md`.

The bundled NVDA context contains enough sourced NVIDIA investor-relations data to calculate all supported ratios without creating missing-input queue entries.

This workflow is deterministic arithmetic only. It does not create valuation, DCF, fair value, price targets, recommendations, investment advice, or memo output.

## Methodology Configuration Workflow

Validate the inert methodology configuration:

```powershell
python scripts/validate_methodology.py
```

`config/methodology_buffett_ai.json` defines allowed future methodology settings, required ratio inputs, scenario names, discount-rate rules, margin-of-safety rules, and outputs that remain prohibited before a valuation stage exists.

This workflow validates configuration shape only. It does not calculate DCF, fair value, intrinsic value, price targets, recommendations, investment advice, or memo output.

## Audit Log Workflow

Append a reproducible analysis-run audit record:

```powershell
python scripts/write_audit_log.py --ticker NVDA --methodology-version 0.1.0 --data-context-path data\companies\NVDA\context.json --source-file data\nvda_sample_metrics.json --validation-status-json path\to\validation_status.json --ratio-outputs-json path\to\ratio_outputs.json --research-gaps-json path\to\research_gaps.json
```

Each JSONL record includes timestamp, ticker, methodology version, data context path, source files used, validation status, ratio outputs, research gaps detected, and the current git commit hash when available.

The audit log records what happened in a run. It does not calculate DCF, fair value, intrinsic value, price targets, recommendations, investment advice, or memo output.

## Orchestrator Workflow

Run the deterministic workflow for one ticker:

```powershell
python scripts/run_analysis.py NVDA --source-data-path data\nvda_sample_metrics.json
```

The orchestrator runs source validation, company context build/load, research gap detection, deterministic ratio calculation, optional valuation readiness and DCF, optional fact-only reporting, optional analysis summary generation, and audit logging. It returns a structured JSON summary with ticker, validation status, research gap count, ratios calculated, artifact paths, audit log status, and warnings.

Run the full workflow and generate a fact-only report:

```powershell
python scripts/run_analysis.py NVDA --source-data-path data\nvda_sample_metrics.json --generate-report
```

When `--generate-report` is used, the JSON summary includes `report_path`.

Run the workflow and generate a structured analysis summary:

```powershell
python scripts/run_analysis.py NVDA --source-data-path data\nvda_sample_metrics.json --generate-summary
```

When `--generate-summary` is used, the JSON summary includes `analysis_summary_path`.

Run the full workflow with deterministic DCF scenarios:

```powershell
python scripts/run_analysis.py NVDA --source-data-path data\nvda_sample_metrics.json --run-dcf --dcf-assumptions-path data\companies\NVDA\dcf_assumptions.json
```

When `--run-dcf` is used, the orchestrator runs source validation, research gap detection, ratio calculation, and the valuation readiness gate before DCF. If readiness passes, it writes structured DCF JSON under `reports/` and includes `dcf_run`, `dcf_scenarios_calculated`, `dcf_output_path`, and `dcf_warnings` in the summary.

Run the full workflow with DCF included in the fact-only report:

```powershell
python scripts/run_analysis.py NVDA --source-data-path data\nvda_sample_metrics.json --run-dcf --dcf-assumptions-path data\companies\NVDA\dcf_assumptions.json --generate-report
```

Run the complete workflow with DCF, report, and structured summary:

```powershell
python scripts/run_analysis.py NVDA --source-data-path data\nvda_sample_metrics.json --run-dcf --dcf-assumptions-path data\companies\NVDA\dcf_assumptions.json --generate-report --generate-summary
```

Full workflow order: validation -> context -> gaps -> ratios -> readiness -> optional DCF -> optional fair value per share -> optional model rating -> model confidence -> model signal -> optional report -> analysis summary -> audit log. When DCF and report flags are used together, the report includes DCF, fair value per share, model rating, model confidence, and model signal sections with assumptions used, bear/base/bull scenario outputs, formulas, reasons, warnings, and source references. When summary generation is enabled, the JSON summary includes `analysis_summary_path`.

The orchestrator does not create price targets, buy/sell/hold recommendations, personal investment advice, live market data fetching, broker/order functionality, automated trading logic, or final investment memo output.

## Fact Report Workflow

Generate a fact-only Markdown report:

```powershell
python scripts/generate_report.py NVDA --validation-status-json path\to\validation_status.json --research-gaps-json path\to\research_gaps.json --ratio-outputs-json path\to\ratio_outputs.json --audit-log-reference audit_log.jsonl:1
```

Reports are written to `reports/` and separate facts, missing data, and warnings. They include validation status, research gaps, calculated ratios, source references, and an audit log reference.

Fact reports may include fair value per share and model rating only as calculated model outputs when the required structured inputs are available. They may also include model confidence as model quality information and model signal as non-personalized model output based only on rating, confidence, model gap, research gaps, and market price freshness.

When a DCF output JSON is provided, the fact report can include a DCF calculation section with assumptions, scenario outputs, formulas, warnings, and source references. This section remains calculation output only and does not include price targets, buy/sell/hold recommendations, investment advice, or final investment memo content.

## Analysis Summary Workflow

Generate a structured JSON analysis summary from validated run artifacts:

```powershell
python scripts/generate_analysis_summary.py NVDA --validation-status-json path\to\validation_status.json --research-gaps-json path\to\research_gaps.json --ratio-outputs-json path\to\ratio_outputs.json --dcf-output-json reports\NVDA_dcf_output.json --audit-log-reference audit_log.jsonl:1
```

The summary is written under `reports/` and separates facts, assumptions, calculated outputs, missing data, and risks/warnings. DCF scenario outputs, fair value per share calculations, model ratings, model confidence, and model signal are included only when their structured JSON outputs are available.

This workflow does not create buy/sell/hold recommendations, price targets, investment advice, automated trading logic, or final investment memo content.

## Valuation Readiness Workflow

Check whether one ticker has passed all pre-valuation controls:

```powershell
python scripts/check_valuation_readiness.py NVDA --source-data-path data\nvda_sample_metrics.json
```

The readiness gate checks:

- source validation is valid
- no high-priority research gaps exist
- required ratios are available
- methodology config is valid
- an audit log probe can be written
- prohibited valuation-stage outputs are absent

The script returns structured JSON with ticker, readiness status, blocking reasons, warnings, and required next actions. A passing result only means the pre-valuation controls are ready for a future stage. It does not calculate DCF, fair value, intrinsic value, price targets, recommendations, buy/sell/hold output, or investment advice.

## DCF Workflow

Run deterministic DCF scenarios from explicit assumptions:

```powershell
python scripts/dcf_model.py NVDA --assumptions-path data\companies\NVDA\dcf_assumptions.json --source-data-path data\nvda_sample_metrics.json
```

The DCF module first calls the valuation readiness gate. If readiness does not pass, no DCF scenarios are calculated.

DCF assumptions are stored separately from facts in `data/companies/<TICKER>/dcf_assumptions.json` and validated against `config/dcf_assumptions_schema.json`. The model requires discount rate, terminal growth rate, explicit forecast years, and starting free cash flow for each bear, base, and bull scenario. It never invents missing assumptions.

The output is structured JSON with formulas, assumptions used, warnings, source references, and scenario calculations. It does not add price targets, buy/sell/hold recommendations, investment advice, or memo generation.

## Fair Value Per Share Workflow

Calculate fair value per share from existing DCF output and sourced diluted share count metrics:

```powershell
python scripts/fair_value_per_share.py NVDA --dcf-output-path reports\NVDA_dcf_output.json
```

The calculation requires a `share_count` metric with a stable `metric_id` in the company context. It never invents share counts or assumptions. Output is structured JSON for bear/base/bull scenarios and remains calculated model output only, not investment advice.

## Model Rating Workflow

Calculate a non-personalized model rating from fair value per share and sourced current market price:

```powershell
python scripts/model_rating.py NVDA --fair-value-per-share-json reports\NVDA_fair_value_per_share_output.json
```

The rating requires a sourced `market_price` metric with `metric_id`, source URL,
source date, confidence, last verified date, unit, `as_of_datetime`, and
`fetched_at`. The rule file `config/model_rating_rules.json` maps fair value
versus market price gaps to ratings 1-5. Output is rule-based model
classification only, not investment advice.

## Model Confidence Workflow

Calculate non-personalized model confidence from validated data quality inputs:

```powershell
python scripts/model_confidence.py NVDA --validation-status-json path\to\validation_status.json --research-gaps-json path\to\research_gaps.json
```

`config/model_confidence_rules.json` maps source validation status, research gaps,
stale data flags, metric confidence fields, DCF assumption completeness, and
market price snapshot freshness to confidence grades A-D. Output is model quality
information only, not a model signal, recommendation, price target, or investment
advice.

## Model Signal Workflow

Calculate a non-personalized model signal from existing model outputs:

```powershell
python scripts/model_signal.py NVDA --model-rating-json reports\NVDA_model_rating_output.json --model-confidence-json reports\NVDA_model_confidence_output.json --research-gaps-json path\to\research_gaps.json
```

`config/model_signal_rules.json` allows only `model_positive`, `model_neutral`,
`model_negative`, or `unavailable`. The signal is unavailable when model
confidence is `D`, model rating is unavailable, a high-priority research gap is
open, or the market price snapshot is stale or missing. This output is
non-personalized model output only; it is not a buy/sell/hold recommendation, a
price target, personal investment advice, live data fetching, broker/order
functionality, or automated trading logic.

## Market Price Snapshot Governance

Market price is a stored snapshot, not live trading data. `as_of_datetime` is the
time the price refers to. `fetched_at` is the time this system stored or retrieved
the snapshot. `config/market_price_snapshot_schema.json` defines the required
snapshot contract.

Source validation checks snapshot shape and required fields. Snapshot freshness
is enforced only by `model_rating.py`; stale market prices make model rating
unavailable but do not block source validation, ratios, DCF, report generation,
summary generation, or audit logging.

No valuation, fair value per share, model rating, report, summary, or orchestrator
module may fetch live market data directly. Future live fetching must go through
a separate Market Data Agent that writes validated snapshot records. Tests use
fixed sample snapshots only.

## Run full NVDA demo

Run the complete deterministic NVDA workflow:

```powershell
python scripts/run_analysis.py NVDA --source-data-path data\nvda_sample_metrics.json --generate-report
```

This validates source data, rebuilds the company context, detects research gaps, calculates deterministic ratios, writes an audit log entry, and generates a fact-only report under `reports/`.

The demo does not create price targets, buy/sell/hold recommendations, personal investment advice, live data fetching, broker/order functionality, or automated trading logic.
