# v0.1 Release Checklist

Use this checklist before tagging or announcing a v0.1 release candidate.

## Required Controls

- Source validation passes for the demo ticker.
- Company context builds from validated source data.
- Research gap detection runs against the watchlist.
- Deterministic ratios calculate from company context.
- Valuation readiness gate runs before DCF.
- DCF runs only from explicit assumptions.
- Fact-only report is generated.
- Structured analysis summary is generated.
- Audit log entry is written.
- Generated artifacts remain ignored by git.
- Full test suite passes.

## Required Commands

```powershell
python -m unittest discover -s tests
python scripts/run_v0_1_demo.py
```

## Prohibited Outputs

- No buy/sell/hold recommendations.
- No price targets.
- No investment advice.
- No automated trading logic.
- No final investment memo.

## Demo Artifacts

The demo writes generated files under `reports/v0_1_demo/` by default. These files
are runtime artifacts and must not be committed.
