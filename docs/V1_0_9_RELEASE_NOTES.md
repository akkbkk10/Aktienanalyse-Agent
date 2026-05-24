# v1.0.9 Release Notes

## Status

v1.0.9 is a post-v1.0.8 maintenance release focused on CI diagnostics for
focused smoke and guardrail tests. It does not change application logic,
financial logic, DCF math, fair value logic, model rating behavior, model
confidence behavior, model signal behavior, valid CLI behavior, generated
report wording, sample company data, schemas, or generated model calculations.

v1.0.9 does not add CI workflow behavior beyond named diagnostics steps. It does
not add schema changes, output schema changes, live fetching, adapters, runtime
agent code, framework dependencies, project renaming, package publishing,
investment advice, or trading behavior.

## Maintenance Summary

### PR #70: Named v1.0 Demo Smoke Test CI Step

- Added a named GitHub Actions step for `python -m unittest tests.test_run_v1_0_demo`.
- Runs the v1.0 demo smoke tests before the full test suite for faster diagnosis
  of demo artifact and reports-directory regressions.
- Preserved the full test suite and existing workflow validation steps.

### PR #71: Named Forbidden-Output Regression CI Step

- Added a named GitHub Actions step for
  `python -m unittest tests.test_forbidden_output_regression`.
- Runs generated-output guardrail checks before the full test suite for faster
  diagnosis of prohibited wording or unsafe user-facing artifact regressions.
- Preserved the full test suite and existing workflow validation steps.

### PR #72: Named Model Confidence And Signal Guardrail CI Steps

- Added named GitHub Actions steps for `python -m unittest tests.test_model_confidence`
  and `python -m unittest tests.test_model_signal`.
- Runs assumption-quality, model confidence, and model signal guardrail tests
  before the full test suite for faster diagnosis.
- Preserved the full test suite and existing source validation, methodology
  validation, workflow smoke, v1.0 demo, and JSON validation steps.

## Test Status

The local unit suite contains 189 tests.

Focused CI-equivalent validation commands:

```bash
python -m unittest tests.test_cli_help
python -m unittest tests.test_run_v1_0_demo
python -m unittest tests.test_forbidden_output_regression
python -m unittest tests.test_model_confidence
python -m unittest tests.test_model_signal
```

Full test suite command:

```bash
python -m unittest discover -s tests
```

v1.0 demo validation command:

```bash
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_0_9_release_notes_demo
```

The v1.0 demo validates the deterministic workflow for NVDA, AMD, and TSMC and
writes generated artifacts under the configured `reports/` path, which remains
ignored by git.

## Upgrade Notes From v1.0.8

No data migration is required. Users can upgrade from v1.0.8 to v1.0.9 by
pulling the release tag and continuing to run the same workflow commands:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py
```

v1.0.9 improves maintainability by making focused smoke and guardrail checks
visible as named CI steps before the full test suite. Existing generated
reports, summaries, DCF outputs, fair value outputs, model ratings, model
confidence outputs, model signals, and audit logs remain compatible with
v1.0.8.

## Explicit Non-Changes

v1.0.9 does not add or change:

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
- tests
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
