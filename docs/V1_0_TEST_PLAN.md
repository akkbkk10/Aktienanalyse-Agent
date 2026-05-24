# v1.0 Test Plan

This plan freezes the current feature set for real user testing. It verifies the
deterministic sample workflow for NVDA, AMD, and TSMC without adding new
companies, live data fetching, recommendations, price targets, personal
investment advice, or trading logic.

## Automated Checks

Run the full test suite:

```powershell
python -m unittest discover -s tests
```

Run the v1.0 release-candidate demo:

```powershell
python scripts/run_v1_0_demo.py
```

The demo must complete successfully for `NVDA`, `AMD`, and `TSMC` and produce:

- fact-only Markdown report
- structured analysis summary JSON
- DCF output JSON
- fair value per share output JSON
- model rating output JSON
- model confidence output JSON
- model signal output JSON
- append-only audit log JSONL

## Manual Review Checklist

For each ticker output under `reports/v1_0_demo/`, confirm:

- Source validation status is valid.
- Research gaps are listed clearly, or the no-gap case is explicit.
- Ratios include formulas, input metric IDs, source references, periods, and
  confidence.
- DCF sections show assumptions, formulas, warnings, and source references.
- Fair value per share is labeled as calculated model output only.
- Model rating is labeled as non-personalized model output only.
- Model confidence is framed as model quality information only.
- Model signal uses only `model_positive`, `model_neutral`, `model_negative`,
  or `unavailable`.
- Market price records are stored snapshots with `as_of_datetime` and
  `fetched_at`.
- Reports separate facts, assumptions, calculated outputs, missing data, and
  warnings.
- Audit log entries include ticker, methodology version, data context path,
  source files used, validation status, ratio outputs, research gaps, and git
  commit hash when available.
- Generated artifacts are written under `reports/` and are not committed.

## Guardrail Checklist

Confirm generated outputs do not include:

- live data fetching
- new companies beyond NVDA, AMD, and TSMC
- new valuation logic
- price target language
- buy/sell/hold recommendation language
- personal investment advice
- broker/order behavior
- automated trading logic

## Release-Candidate Acceptance

The v1.0 release candidate is ready for user testing when:

- All automated tests pass.
- The v1.0 demo exits with status code `0`.
- Each ticker has all required generated artifacts.
- The manual review checklist is complete for NVDA, AMD, and TSMC.
- Guardrail review finds no prohibited behavior or language.
