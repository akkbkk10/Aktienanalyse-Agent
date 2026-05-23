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
- `reports/` - generated reports.
- `research_queue.md` - queue of research requests.

## Run Tests

```powershell
python -m unittest discover -s tests
```

## Validate A Metrics File

```powershell
python scripts/validate_sources.py path\to\metrics.json
```

The input file may contain either a single JSON object or a list of objects.
