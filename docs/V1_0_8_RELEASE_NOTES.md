# v1.0.8 Release Notes

## Status

v1.0.8 is a post-v1.0.7 maintenance release focused on v1.0 demo
reports-directory behavior test hardening. It does not change application
logic, financial logic, DCF math, fair value logic, model rating behavior,
model confidence behavior, model signal behavior, valid CLI behavior, generated
report wording, sample company data, schemas, or generated model calculations.

v1.0.8 does not add valid CLI behavior changes, default argument changes, output
schema changes, schema changes, live fetching, adapters, runtime agent code,
framework dependencies, project renaming, package publishing, investment advice,
or trading behavior.

## Maintenance Summary

### PR #68: v1.0 Demo Reports-Directory Smoke Test

- Extended `tests/test_run_v1_0_demo.py` with a custom reports-directory smoke
  test.
- Verified the v1.0 demo helper writes the shared audit log under the configured
  reports directory.
- Verified NVDA, AMD, and TSMC generated artifacts are written under their
  per-ticker directories inside the configured reports directory.
- Covered the per-ticker fact report, analysis summary, DCF output, fair value
  per share output, model rating output, model confidence output, and model
  signal output.
- Kept the test deterministic, platform-neutral, network-free, and based on
  temporary directories.

## Test Status

The local unit suite contains 189 tests.

Required validation commands:

```bash
python -m unittest tests.test_run_v1_0_demo
python -m unittest tests.test_cli_help
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_0_8_release_notes_demo
```

The v1.0 demo validates the deterministic workflow for NVDA, AMD, and TSMC and
writes generated artifacts under the configured `reports/` path, which remains
ignored by git.

## Upgrade Notes From v1.0.7

No data migration is required. Users can upgrade from v1.0.7 to v1.0.8 by
pulling the release tag and continuing to run the same workflow commands:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py
```

v1.0.8 improves maintainability by ensuring generated v1.0 demo artifacts are
written under the configured reports directory. Existing generated reports,
summaries, DCF outputs, fair value outputs, model ratings, model confidence
outputs, model signals, and audit logs remain compatible with v1.0.7.

## Explicit Non-Changes

v1.0.8 does not add or change:

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
