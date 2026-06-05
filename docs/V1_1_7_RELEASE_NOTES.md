# v1.1.7 Release Notes

## Status

v1.1.7 is a guardrail, test, and CLI-help hardening release for the
deterministic Aktienanalyse-Agent core.

This release covers PR #113 through PR #115. It does not add financial logic,
runtime analysis behavior changes beyond CLI help wording, schemas, config
changes, generated reports, adapters, live data, methodology configuration
implementation, generated artifact manifest implementation, MCP/A2A integration,
web UI, advice, price targets, trading, or portfolio automation.

## Release Summary

### PR #113: Harden Forbidden-Output Regression Coverage

- Expanded the dedicated forbidden-output regression test to scan generated
  DCF output artifacts in addition to reports, summaries, fair value per share
  outputs, model rating outputs, model confidence outputs, and model signal
  outputs.
- Added exact prohibited phrase coverage for financial-advice, trading,
  portfolio-automation, and fabricated-data wording.
- Updated `docs/GUARDRAIL_SECURITY_TEST_PLAN.md` so the documented regression
  coverage matches the test.
- Preserved generated report wording, financial calculations, schemas, config
  files, and runtime behavior.

### PR #114: Clarify CLI Guardrail Guidance

- Added explicit no-live-data, no-price-target, no-recommendation,
  no-investment-advice, and no-trading-action wording to the existing
  `run_v1_0_demo.py --help` and `run_batch_analysis.py --help` text.
- Strengthened `tests/test_cli_help.py` so CLI help smoke tests cover the
  guardrail wording consistently across demo, analysis, and batch commands.
- Normalized whitespace in the CLI help smoke helper so assertions remain
  stable when `argparse` wraps long help text.
- Preserved existing CLI options, command behavior, generated artifacts,
  financial logic, and model behavior.

### PR #115: v1.1.7 Release Notes Candidate

- Added `docs/V1_1_7_RELEASE_NOTES.md`.
- Summarized the post-v1.1.6 hardening block from PR #113 and PR #114.
- Added the v1.1.7 release-note entry to the README documentation map.
- Preserved docs-only scope and explicitly excluded runtime analysis behavior
  changes, financial logic, schemas, config changes, generated reports,
  adapters, live data, methodology implementation, manifest implementation,
  advice, price targets, trading, and portfolio automation.

## Durable Files Added Or Updated

v1.1.7 adds or updates these durable files:

- `docs/GUARDRAIL_SECURITY_TEST_PLAN.md`
- `docs/V1_1_7_RELEASE_NOTES.md`
- `README.md`
- `scripts/run_v1_0_demo.py`
- `scripts/run_batch_analysis.py`
- `tests/test_forbidden_output_regression.py`
- `tests/test_cli_help.py`

## Test Status

The local unit suite contains 229 tests.

Validation command:

```bash
python -m unittest discover -s tests
```

Result: 229 tests OK.

## Maintainer Validation Before Tagging

Before creating a `v1.1.7` tag, maintainers should:

1. Use a fresh checkout of `main` after this release-note PR is merged.
2. Confirm the working tree is clean:

```bash
git status --short --branch
```

3. Run the full unit suite:

```bash
python -m unittest discover -s tests
```

4. Run the demo validation required by the existing release process:

```bash
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_1_7_release_validation
```

5. Confirm generated reports remain ignored and the working tree is clean.
6. Create the `v1.1.7` tag only after the release-note PR is merged to `main`
   and validation passes.

Follow `docs/RELEASE_AND_TAG_GOVERNANCE.md` and
`docs/V1_0_X_PATCH_RELEASE_CHECKLIST.md` for tag and GitHub Release handling.

## Explicit Non-Changes

v1.1.7 does not add or change:

- financial logic
- valuation formulas
- DCF behavior
- fair value per share behavior
- model rating behavior
- model confidence behavior
- model signal behavior
- analysis report wording
- generated report content
- schemas
- config files
- dependencies
- generated reports committed to the repository
- adapters
- live data
- MCP or A2A integration
- web UI
- methodology configuration implementation
- generated artifact manifest implementation
- buy/sell/hold advice
- price targets
- trading logic
- portfolio automation
- personal investment advice

Generated artifact manifest implementation, adapter/live-data implementation,
methodology configuration implementation, MCP/A2A, web UI, new financial logic,
and new companies remain future work and are not part of v1.1.7.
