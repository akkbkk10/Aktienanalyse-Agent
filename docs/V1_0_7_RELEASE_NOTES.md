# v1.0.7 Release Notes

## Status

v1.0.7 is a post-v1.0.6 maintenance release focused on CLI invalid-argument
smoke test hardening. It does not change application logic, financial logic,
DCF math, fair value logic, model rating behavior, model confidence behavior,
model signal behavior, valid CLI behavior, generated report wording, sample
company data, schemas, or generated model calculations.

v1.0.7 does not add valid CLI behavior changes, default argument changes, output
schema changes, schema changes, live fetching, adapters, runtime agent code,
framework dependencies, project renaming, package publishing, investment advice,
or trading behavior.

## Maintenance Summary

### PR #66: CLI Invalid-Argument Smoke Tests

- Extended `tests/test_cli_help.py` with invalid-option smoke tests.
- Covered invalid command-line arguments for `scripts/run_v1_0_demo.py`,
  `scripts/run_analysis.py`, and `scripts/run_batch_analysis.py`.
- Asserted that invalid CLI invocations fail with a non-zero exit code and clear
  argparse-style usage/error output.
- Kept the tests deterministic, platform-neutral, network-free, and free of
  generated report creation.
- Confirmed invalid CLI arguments fail before workflows are accidentally run.

## Test Status

The local unit suite contains 188 tests.

Required validation commands:

```bash
python -m unittest tests.test_cli_help
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py --help
python scripts/run_analysis.py --help
python scripts/run_batch_analysis.py --help
python scripts/run_v1_0_demo.py --definitely-invalid-option
python scripts/run_analysis.py --definitely-invalid-option
python scripts/run_batch_analysis.py --definitely-invalid-option
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_0_7_release_notes_demo
```

The invalid-option commands are expected to fail with non-zero exit codes and
clear argparse-style usage/error output. The v1.0 demo validates the
deterministic workflow for NVDA, AMD, and TSMC and writes generated artifacts
under `reports/`, which remains ignored by git.

## Upgrade Notes From v1.0.6

No data migration is required. Users can upgrade from v1.0.6 to v1.0.7 by
pulling the release tag and continuing to run the same workflow commands:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py
```

v1.0.7 improves maintainability by ensuring invalid CLI arguments fail clearly
and do not accidentally run workflows. Existing generated reports, summaries,
DCF outputs, fair value outputs, model ratings, model confidence outputs, model
signals, and audit logs remain compatible with v1.0.6.

## Explicit Non-Changes

v1.0.7 does not add or change:

- application logic
- financial logic
- DCF math
- fair value per share logic
- model rating behavior
- model confidence behavior
- model signal behavior
- valid CLI behavior
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
