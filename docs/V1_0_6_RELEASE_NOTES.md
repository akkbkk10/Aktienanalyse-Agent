# v1.0.6 Release Notes

## Status

v1.0.6 is a post-v1.0.5 maintenance release focused on CLI test hardening and
CI diagnostics. It does not change application logic, financial logic, DCF math,
fair value logic, model rating behavior, model confidence behavior, model signal
behavior, CLI behavior, generated report wording, sample company data, schemas,
or generated model calculations.

v1.0.6 does not add CLI behavior changes, default argument changes, schema
changes, live fetching, adapters, runtime agent code, framework dependencies,
project renaming, package publishing, or trading behavior.

## Maintenance Summary

### PR #63: CLI Help Smoke Tests

- Added `tests/test_cli_help.py`.
- Covered help output for `scripts/run_v1_0_demo.py`,
  `scripts/run_analysis.py`, and `scripts/run_batch_analysis.py`.
- Asserted useful discoverability terms such as `usage`, `reports-dir`,
  supported sample tickers, `ticker`, `batch`, `generate-report`, and `run-dcf`.
- Kept the tests deterministic, platform-neutral, network-free, and free of
  generated report creation.

### PR #64: Named CI Diagnostics For CLI Help

- Added a named GitHub Actions step for `python -m unittest tests.test_cli_help`.
- Runs the CLI help smoke tests before the full test suite for faster diagnosis
  when command discoverability regresses.
- Preserved the existing full test suite, source validation, methodology
  validation, workflow smoke tests, v1.0 demo validation, and JSON validation
  steps.

## Test Status

The local unit suite contains 185 tests.

Required validation commands:

```bash
python -m unittest tests.test_cli_help
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py --help
python scripts/run_analysis.py --help
python scripts/run_batch_analysis.py --help
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_0_6_release_notes_demo
```

The v1.0 demo validates the deterministic workflow for NVDA, AMD, and TSMC and
writes generated artifacts under `reports/`, which remains ignored by git.

## Upgrade Notes From v1.0.5

No data migration is required. Users can upgrade from v1.0.5 to v1.0.6 by
pulling the release tag and continuing to run the same workflow commands:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py
```

v1.0.6 improves maintainability through automated CLI help smoke tests and a
named CI diagnostics step for CLI discoverability regressions. Existing
generated reports, summaries, DCF outputs, fair value outputs, model ratings,
model confidence outputs, model signals, and audit logs remain compatible with
v1.0.5.

## Explicit Non-Changes

v1.0.6 does not add or change:

- application logic
- financial logic
- DCF math
- fair value per share logic
- model rating behavior
- model confidence behavior
- model signal behavior
- CLI behavior
- CLI help text
- default arguments
- output schemas
- generated report wording
- schemas
- live data fetching
- new companies
- runtime agent code
- adapters
- MCP integration
- A2A integration
- framework dependencies
- project naming
- package publishing
- price targets
- buy/sell/hold recommendations
- personal investment advice
- trading or portfolio logic
