# ASML Source Material Handoff Checklist

This checklist defines the manual source handoff required before creating an
ASML offline source package. It is documentation only. It does not add ASML
data files, DCF assumptions, watchlist entries, generated reports, adapters,
live data, provider APIs, schema changes, runtime behavior, financial logic, or
release artifacts.

## Current Decision

Decision: **ASML source-package creation is blocked until official source
material is manually provided and verified**.

The existing ASML plan intentionally does not assert current ASML source URLs,
financial figures, source dates, market prices, share counts, units, periods,
or accounting basis. Do not create `data/asml_sample_metrics.json` or
`data/companies/ASML/dcf_assumptions.json` from placeholders, memory, search
snippets, unofficial aggregators, or plausible-looking values.

## Required Official Source Materials

Before any ASML number is entered into project data, maintainers must provide
or explicitly identify official source material for manual review:

- official ASML annual report page URL or annual report PDF URL
- local path to the reviewed ASML annual report PDF, if the file is provided
  locally
- official ASML investor-relations page URL used to locate the annual report
- official ASML results, annual-report, or investor-relations source for any
  metric not clearly available in the annual report
- SEC filing URL only if that source is used and manually verified
- static market-price snapshot source URL or reviewed file, only if model
  rating is intended to be available

Place local review copies under:

```text
source_material/ASML/
```

This folder is local-only source material and must not be committed. Commit only
reviewed source-data records under `data/` after the values are traced to
official sources and validation passes.

Unofficial data providers, summaries, search snippets, copied tables, and
unreviewed local files are not enough for the first ASML package.

## Required Handoff Metadata

For every official source or reviewed local file, record:

- source title or file name
- official URL
- local file path, if applicable
- manual verification date
- source publication or filing date
- fiscal period covered
- accounting basis used by the source
- reported currency
- reported unit and scale
- page, table, note, or section reference when available
- reviewer notes for any transformation from source presentation to stored unit
- confidence value

If any of these fields are unclear, keep ASML blocked rather than entering a
number.

## Accounting Basis Decision

Choose one accounting basis for the initial source package and keep it
consistent across the financial-statement metrics.

- Use `IFRS` only when the official reviewed ASML source supports IFRS-reported
  financial statement figures.
- Use `Non-GAAP` only when the official source explicitly presents a non-GAAP
  measure or the project clearly documents a derived measure such as free cash
  flow from sourced cash-flow line items.
- Use `Other` only for records whose schema meaning supports it, such as a
  stored market-price snapshot.

Do not mix IFRS, Non-GAAP, and Other values without explicit labels and source
references for each record.

## Required Metric Evidence

The first ASML source package should not be created until these records can be
traced to official evidence:

| Record | Required evidence before entry |
| --- | --- |
| `Revenue` | Official value, fiscal period, source date, currency, unit/scale, accounting basis, and source URL or local reviewed file. |
| `Net income` | Official value, fiscal period, source date, currency, unit/scale, accounting basis, and source URL or local reviewed file. |
| `Free cash flow` | Official company-presented value or clearly derived value from official cash-flow line items, with derivation notes. |
| `share_count` | Share-count definition, period, unit, source date, and whether the value is ordinary shares, diluted weighted average shares, ADR-related, or another explicit measure. |
| `market_price` | Stored snapshot only: price, currency, exchange, `price_type`, `as_of_datetime`, `fetched_at`, provider, retrieval method, source URL, source date, and confidence. |

Gross profit, operating income, segment metrics, or extra fields may be added
later only if the same evidence standard is satisfied.

If the ASML trial is expected to run the full DCF path, include the prior-period
revenue needed for the existing `revenue_growth` readiness check. A single-year
ASML package may pass source/onboarding validation but still fail the full
DCF/readiness path because `revenue_growth` cannot be calculated.

Do not use a ChatGPT answer, finance homepage, search result, or unstamped quote
as the market-price source. If a static market snapshot cannot be reproduced
with source, timestamp, instrument, exchange, currency, and confidence, leave
model rating unavailable instead of committing the snapshot.

## DCF Assumption Boundary

Do not add `data/companies/ASML/dcf_assumptions.json` unless the assumptions are
separately reviewed and clearly labeled as assumptions, not facts.

At minimum, DCF assumptions would need:

- source references for starting free cash flow
- explicit bear/base/bull assumptions
- unit consistency with the source metrics
- manual-review notes explaining assumption status
- no price target, recommendation, or investment-advice wording

If assumptions are not ready, the first ASML package may use source validation
only and omit DCF.

## Validation Gate

After official source material is reviewed and ASML local files exist, validate
before analysis:

```powershell
python scripts/validate_sources.py data/asml_sample_metrics.json
```

If DCF assumptions and a watchlist entry are included, validate the full
onboarding package:

```powershell
python scripts/validate_company_onboarding.py ASML --metrics-path data/asml_sample_metrics.json --dcf-assumptions-path data/companies/ASML/dcf_assumptions.json
```

If validation fails, stop. Do not run ASML analysis with invalid or incomplete
source evidence.

## Explicit Non-Goals

This checklist does not authorize:

- ASML data entry from unverified sources
- generated ASML reports committed to the repository
- live market data fetching
- provider API usage
- adapter implementation
- MCP/A2A runtime integration
- web UI or desktop app behavior
- methodology implementation
- generated artifact manifest implementation
- financial logic or valuation formula changes
- buy/sell/hold recommendations
- price targets
- personal investment advice
- trading logic
- portfolio automation

## Smallest Safe Next Step

The next source step is a manual handoff of official ASML source materials with
the metadata above. Only after that handoff is complete should a separate,
reviewed source-package PR create ASML data files.
