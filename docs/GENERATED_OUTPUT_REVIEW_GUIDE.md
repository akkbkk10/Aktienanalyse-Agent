# Generated Output Review Guide

Use this guide when reviewing PRs that can change generated analysis artifacts,
especially future adapter, market data, MCP, A2A, or framework-evaluation work.

Generated artifacts should be reviewed locally, but not committed. Use an
ignored reports path such as:

```bash
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_generated_output_review
```

The current expected artifact paths and required v1.0 demo outputs are
documented in `docs/REPORT_ARTIFACT_CONTRACT.md`.

## Artifacts To Review

Inspect generated outputs for each affected ticker:

- fact reports
- structured analysis summaries
- DCF outputs
- fair value per share outputs
- model rating outputs
- model confidence outputs
- model signal outputs
- audit logs

For batch or adapter changes, review successful and failed ticker outputs
separately so one ticker's behavior does not hide another ticker's issue.

## Review Checklist

Check generated artifacts for:

- no price targets
- no buy/sell/hold recommendations
- no personal investment advice
- no broker/order instructions
- no automated trading language
- no invented sources
- no unsourced financial figures
- no unsupported live-data claims
- every financial figure has source, date, unit, period, and confidence where
  applicable
- assumptions are clearly separated from facts and calculated outputs
- example/manual-review assumptions keep active model signals unavailable
- market prices are stored snapshots with `as_of_datetime` and `fetched_at`
- audit logs include validation status and source files used

## Safe Output Changes

Safe changes preserve factual framing and traceability:

- "Model signal is unavailable because assumptions require manual review."
- "Fair value per share is a calculated model output only, not investment
  advice."
- "Revenue uses source URL, source date, unit, period, and confidence metadata."
- "Market price is a stored snapshot, not a live fetch."
- "Missing data is listed as a research gap."

## Unsafe Output Changes

Unsafe changes should block the PR until corrected:

- "The model sets a price target of X."
- "You should buy this stock."
- "This is personal investment advice."
- "Place an order."
- "The DCF module fetched the latest live quote."
- "Revenue is X" without source metadata.
- Any output that mixes assumptions with sourced facts without labeling them.

## Future Adapter Review Checklist

For Market Data Agent, MCP, A2A, or framework-adapter PRs, confirm:

- market data snapshot contract was reviewed
- source metadata is preserved from adapter input to generated output
- no live-fetching claim appears unless live fetching is implemented, validated,
  tested, and documented in the adapter
- adapter code does not move business logic out of the deterministic core
- generated artifacts were reviewed but not committed
- adapter failures fail closed with clear errors or research gaps
- forbidden-output regression tests still pass

## Suggested Review Flow

1. Run the full tests.
2. Run the v1.0 demo into a temporary `reports/tmp_*` path.
3. Inspect generated artifacts for changed tickers.
4. Compare representative report and summary diffs.
5. Confirm `tests/test_forbidden_output_regression.py` still passes.
6. Confirm generated artifacts remain untracked.
