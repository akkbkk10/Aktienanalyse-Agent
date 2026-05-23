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
- `agents/` - future agent definitions.
- `scripts/` - executable helper scripts.
- `tests/` - test suite.
- `data/` - raw and intermediate input data.
- `data/companies/<TICKER>/context.json` - persistent company context files.
- `reports/` - generated reports.
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
