# Data Contract Review Checklist

Use this checklist before changing source schemas, market data snapshot formats,
adapter outputs, or any field-level traceability contract.

Data contracts are part of the project guardrail surface. They define how facts,
assumptions, calculated outputs, missing data, unavailable outputs, warnings,
and audit evidence move through the deterministic core and any future adapter
boundary.

Related governance docs:

- `docs/ADAPTER_PROPOSAL_CHECKLIST.md`
- `docs/GUARDRAIL_SECURITY_TEST_PLAN.md`
- `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`
- `.github/ISSUE_TEMPLATE/schema_change_proposal.md`

## Required Metadata

Any future financial figure or adapter-provided data point should include these
fields unless a field is explicitly not applicable and the reason is documented:

- `ticker`
- company name, if applicable
- `metric_id`
- metric name
- value
- unit
- currency, if applicable
- period or fiscal period
- `as_of_date`, filing date, report date, or equivalent date context
- source name
- source URL or source reference
- retrieval timestamp, if applicable
- confidence
- calculation status: `sourced`, `calculated`, `missing`, or `unavailable`
- assumption status, if applicable
- manual review status, if applicable

## Required Separation

Data contracts must keep these categories separate:

- facts
- assumptions
- calculated outputs
- warnings
- missing data
- unavailable outputs

Do not merge assumptions into sourced facts. Do not present unavailable outputs
as calculated outputs. Do not hide warnings inside free-form notes when a
structured warning field is available.

## Schema Change Review Questions

Before changing a schema or adapter output contract, reviewers should ask:

- Does every financial number have source metadata?
- Does every calculated output preserve upstream input references?
- Are units and currencies explicit?
- Is period/date information unambiguous?
- Are assumptions clearly labeled and review-gated?
- Can generated reports trace back to source data?
- Can audit logs reconstruct the workflow?
- Can missing or unavailable data be represented without inventing values?
- Can stale data be identified without blocking unrelated workflow steps?
- Are field names stable enough for tests, reports, summaries, and audit logs?

## Snapshot Format Expectations

Future Market Data Agent or adapter snapshots should be immutable records of
what was observed or retrieved, not live values hidden inside calculations.

Snapshot contracts should define:

- source or provider name
- retrieval method
- retrieval timestamp
- observation timestamp, such as `as_of_datetime`
- source URL or source reference
- ticker or instrument identifier
- exchange or venue, if applicable
- currency, if applicable
- value and unit
- confidence
- freshness rules
- stale-data behavior
- validation result
- audit-log reference fields

Market price snapshots should preserve both the time the price refers to and the
time the system retrieved or stored it. A future adapter may fetch data, but the
deterministic core should consume only validated snapshots.

## Prohibited Data-Contract Shortcuts

Reject data contracts that allow:

- raw numbers without source metadata
- live price values without timestamp and source
- assumptions treated as facts
- adapter output directly changing rating or signal behavior
- business logic moved into adapters
- unsourced or invented figures
- ambiguous units or currencies
- ambiguous fiscal periods
- calculated outputs without upstream metric references
- generated reports that cannot trace back to source data
- audit logs that cannot reconstruct the workflow

## Good Data Record Example

```json
{
  "ticker": "NVDA",
  "company_name": "NVIDIA Corporation",
  "metric_id": "nvda_revenue_fy2025",
  "metric": "revenue",
  "value": 130497,
  "unit": "millions",
  "currency": "USD",
  "period": "FY2025",
  "as_of_date": "2025-01-26",
  "source_name": "NVIDIA annual report",
  "source_url": "https://investor.nvidia.com/",
  "retrieval_timestamp": "2026-05-24T00:00:00Z",
  "confidence": "high",
  "calculation_status": "sourced",
  "assumption_status": "not_applicable",
  "manual_review_status": "reviewed"
}
```

This record is reviewable because the value has a stable identifier, explicit
unit and currency, period/date context, source reference, confidence, and status
fields.

## Bad Data Record Example

```json
{
  "ticker": "NVDA",
  "metric": "revenue",
  "value": 130497
}
```

This record should be rejected because it lacks `metric_id`, unit, currency,
period/date context, source metadata, confidence, calculation status, and review
status.

## Adapter Output Review

For future adapter outputs, confirm:

- adapter data is transformed into an explicit contract before core analysis
  uses it
- source metadata is preserved from adapter input through generated artifacts
- validation failures produce errors, missing data, unavailable outputs, or
  research gaps instead of invented values
- adapter-provided records cannot directly set model rating, model confidence,
  or model signal without deterministic core logic
- audit logs include enough source and validation context to reproduce the run
- generated reports and summaries can trace facts and calculated outputs back to
  source records

## Review Evidence To Attach To PRs

Schema or adapter-output PRs should include:

- changed contract fields
- required vs optional field rationale
- sample valid record
- sample invalid record
- validation behavior for missing metadata
- stale-data behavior, if applicable
- generated-output review notes
- audit-log traceability notes
- guardrail impact summary

Generated artifacts may be reviewed locally, but must remain under ignored
`reports/tmp_*` paths and must not be committed.
