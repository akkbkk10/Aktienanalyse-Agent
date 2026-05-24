# v1.0.5 Release Notes

## Status

v1.0.5 is a post-v1.0.4 maintenance release focused on CLI usability and
documentation consistency. It does not change application logic, financial
logic, DCF math, fair value logic, model rating behavior, model confidence
behavior, model signal behavior, generated report wording, sample company data,
schemas, CLI behavior, or generated model calculations.

v1.0.5 does not add schema changes, live fetching, adapters, runtime agent code,
framework dependencies, project renaming, package publishing, or CLI behavior
changes.

## Maintenance Summary

### PR #59: CLI Help Text Cleanup

- Clarified help text for `scripts/run_v1_0_demo.py`,
  `scripts/run_analysis.py`, and `scripts/run_batch_analysis.py`.
- Expanded the v1.0 demo help to describe the workflow stages, supported sample
  companies, reports directory behavior, ignored generated artifacts, and
  deterministic demo output purpose.
- Preserved command behavior, defaults, and output schemas.

### PR #60: README Command Reference

- Added a compact README command reference table for the main CLI/script
  commands.
- Documented the v1.0 demo help command, a reports-dir demo example, analysis
  help, and batch help.
- Noted that generated reports and model artifacts under `reports/` are ignored
  by git and should not be committed.

### PR #61: v1.0 Demo Wording Consistency

- Aligned current-facing README and test-plan wording with the v1.0.x
  maintenance-series framing.
- Replaced stale current-facing references to the `v1.0.0 demo` and release
  candidate wording with `v1.0 demo workflow` language where clearer.
- Kept historical release notes and historical validation records intact.

## Test Status

The local unit suite contains 182 tests.

Required validation commands:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py --help
python scripts/run_analysis.py --help
python scripts/run_batch_analysis.py --help
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_0_5_release_notes_demo
```

The v1.0 demo validates the deterministic workflow for NVDA, AMD, and TSMC and
writes generated artifacts under `reports/`, which remains ignored by git.

## Upgrade Notes From v1.0.4

No data migration is required. Users can upgrade from v1.0.4 to v1.0.5 by
pulling the release tag and continuing to run the same workflow commands:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py
```

v1.0.5 improves usability through clearer CLI help text, a README command
reference, and consistent v1.0 demo / v1.0.x maintenance-series wording.
Existing generated reports, summaries, DCF outputs, fair value outputs, model
ratings, model confidence outputs, model signals, and audit logs remain
compatible with v1.0.4.

## Explicit Non-Changes

v1.0.5 does not add or change:

- application logic
- financial logic
- DCF math
- fair value per share logic
- model rating behavior
- model confidence behavior
- model signal behavior
- CLI behavior
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
