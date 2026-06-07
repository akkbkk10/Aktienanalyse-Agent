# v1.1.12 Release Notes

## Status

v1.1.12 is a small status and release-note block after PR #139, PR
#140, and the successful local ASML UAT of the new market-price readiness
boundary.

This release-note candidate documents current state only. It does not add
runtime behavior changes, schemas, ASML data, generated reports, source
material, live data, market-data adapters, provider APIs, MCP/A2A runtime
integration, web UI, trading logic, price targets, buy/sell/hold advice,
portfolio automation, or personal investment advice.

## Release Summary

### PR #139: Market Price Boundary Decision

- Documented `market_price` as a separate static stored snapshot boundary.
- Confirmed that the deterministic core must not fetch, refresh, infer, or
  silently update live market prices.
- Clarified that model rating and downstream model signal availability require
  validated market-price evidence.

### PR #140: Optional Market Price Readiness Tiers

- Added explicit onboarding support tiers:
  - `full`
  - `source_only`
  - `dcf_ready`
- Preserved `full` as the default protected behavior.
- Allowed source-only and DCF-ready onboarding checks to pass without
  `market_price` when their required lower-tier evidence is valid.
- Kept model rating and downstream model signal unavailable without a validated
  market-price snapshot.

## Local ASML UAT Result

A local ASML trial after PR #140 validated the new boundary with local-only
ASML files. ASML data remains outside the repository and is not public sample
data.

Observed local UAT results:

- `full` tier with original local ASML metrics returned `ready: true`.
- `source_only` with a temporary no-market-price metrics copy returned
  `ready: true`.
- `dcf_ready` with the temporary no-market-price metrics copy returned
  `ready: true`.
- `full` with the temporary no-market-price metrics copy correctly failed with
  the missing market-price snapshot as a blocker.
- `run_analysis.py` with the temporary no-market-price metrics copy succeeded,
  ran DCF, and kept model rating unavailable.
- The model signal artifact remained explicitly unavailable when model rating
  was unavailable.
- No active advice output was found.
- Trial outputs stayed under ignored `reports/tmp_asml_after_pr140/` paths.

## Test Status

The local unit suite contains 240 tests after PR #140.

Validation command:

```bash
python -m unittest discover -s tests
```

Result: 240 tests OK.

## ASML Next Decision

ASML should remain local-only until a separate reviewed data-package PR is
opened intentionally.

The next ASML decision must review:

- official source values
- currency boundaries
- share count, share class, and ADS boundaries
- DCF assumptions and labels
- whether any optional market-price evidence is repo-safe, static,
  timestamped, provider-labeled, sourceable, and manually verifiable

Generated ASML reports, generated contexts, audit logs, research queues,
downloaded source files, PDFs, and `source_material/` review copies must remain
uncommitted.

## Explicit Non-Changes

v1.1.12 does not add or change:

- ASML source data committed to the repository
- generated reports committed to the repository
- generated contexts committed to the repository
- downloaded source material or PDFs
- `source_material/` contents
- live data fetching
- market data adapters
- provider API integration
- external credentials
- dependencies
- MCP or A2A runtime integration
- web UI
- desktop app behavior
- schemas
- financial logic
- DCF formulas
- model rating semantics
- model signal semantics
- trading logic
- price targets
- buy/sell/hold recommendations
- portfolio automation
- personal investment advice
- release tags
- GitHub Releases

