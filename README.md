# Aktienanalyse Agent

Initial scaffold for an agentic stock analysis system.

The first implementation slice focuses on evidence discipline:

- Validate financial metrics before they can be used.
- Require source metadata for every financial number.
- Keep facts, assumptions, and opinions separate.
- Keep GAAP and Non-GAAP metrics explicitly labeled.

Valuation, DCF, price target, and investment recommendation logic are intentionally not implemented yet.

## Repository Layout

- `AGENTS.md` - mandatory rules for agents and contributors.
- `config/` - schemas and validation rules.
- `config/watchlist.json` - required research coverage by ticker.
- `agents/` - future agent definitions.
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

## Setup

```powershell
git clone <repo-url>
cd Aktienanalyse-Agent
python --version
python -m unittest discover -s tests
```

Use Python 3.12 or newer for local development.

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

Run the deterministic pre-valuation workflow for one ticker:

```powershell
python scripts/run_analysis.py NVDA --source-data-path data\nvda_sample_metrics.json
```

The orchestrator runs source validation, company context build/load, research gap detection, deterministic ratio calculation, and audit logging. It returns a structured JSON summary with ticker, validation status, research gap count, ratios calculated, audit log status, and warnings.

The orchestrator does not calculate DCF, fair value, intrinsic value, price targets, recommendations, investment advice, or memo output.

## Fact Report Workflow

Generate a fact-only Markdown report:

```powershell
python scripts/generate_report.py NVDA --validation-status-json path\to\validation_status.json --research-gaps-json path\to\research_gaps.json --ratio-outputs-json path\to\ratio_outputs.json --audit-log-reference audit_log.jsonl:1
```

Reports are written to `reports/` and separate facts, missing data, and warnings. They include validation status, research gaps, calculated ratios, source references, and an audit log reference.

Fact reports must not include valuation, fair value, intrinsic value, price targets, buy/sell/hold recommendations, or investment advice.
