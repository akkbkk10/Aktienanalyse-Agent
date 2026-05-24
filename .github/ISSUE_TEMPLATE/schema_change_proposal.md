---
name: Schema change proposal
about: Propose a source schema, snapshot format, or adapter data-contract change before implementation
title: "[Schema]: "
labels: architecture, governance
assignees: ""
---

## Proposal

Describe the proposed schema or data-contract change before implementation.


## Affected files or schemas

-

## Affected workflow stage

- [ ] source validation
- [ ] company context
- [ ] research gaps
- [ ] ratios
- [ ] valuation readiness
- [ ] DCF
- [ ] fair value per share
- [ ] model rating
- [ ] model confidence
- [ ] model signal
- [ ] reports
- [ ] summaries
- [ ] audit logs
- [ ] adapter boundary
- [ ] other:

## Affected generated artifacts

- [ ] fact reports
- [ ] structured analysis summaries
- [ ] DCF outputs
- [ ] fair value per share outputs
- [ ] model rating outputs
- [ ] model confidence outputs
- [ ] model signal outputs
- [ ] audit logs
- [ ] none expected

## Required metadata fields

Confirm how the proposal handles required metadata from
`docs/DATA_CONTRACT_REVIEW_CHECKLIST.md`.

- [ ] ticker
- [ ] company name, if applicable
- [ ] metric_id
- [ ] metric name
- [ ] value
- [ ] unit
- [ ] currency, if applicable
- [ ] period or fiscal period
- [ ] as_of_date, filing/report date, or equivalent date context
- [ ] source name
- [ ] source URL or source reference
- [ ] retrieval timestamp, if applicable
- [ ] confidence
- [ ] calculation status
- [ ] assumption status, if applicable
- [ ] manual review status, if applicable

## Source, date, unit, period, currency, and confidence handling

Describe how source metadata, date context, unit, period, currency, and
confidence are captured and validated.


## Assumption and manual-review handling

Describe how assumptions are labeled, separated from facts, and review-gated.


## Backward compatibility

Describe compatibility impact for existing NVDA, AMD, and TSMC data, contexts,
reports, summaries, model outputs, and audit logs.


## Migration or fixture update needs

List any required fixture, sample data, context, or documentation updates.


## Audit-log impact

Describe how audit logs can still reconstruct the workflow after this change.


## Generated-output review impact

Describe which generated artifacts reviewers should inspect with
`docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`.


## Guardrail and security impact

Describe guardrail implications using `docs/GUARDRAIL_SECURITY_TEST_PLAN.md`.


## Required references

- [ ] Reviewed `docs/DATA_CONTRACT_REVIEW_CHECKLIST.md`.
- [ ] Reviewed `docs/GUARDRAIL_SECURITY_TEST_PLAN.md`.
- [ ] Reviewed `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`.
- [ ] If adapter-related, reviewed `docs/ADAPTER_PROPOSAL_CHECKLIST.md`.

## Tests required before implementation

- [ ] source/schema validation tests
- [ ] missing metadata tests
- [ ] stale or unavailable data tests, if applicable
- [ ] calculated-output traceability tests, if applicable
- [ ] audit-log traceability tests
- [ ] generated-output forbidden-language tests, if generated artifacts change
- [ ] `python -m unittest discover -s tests`
- [ ] `python scripts/run_v1_0_demo.py --reports-dir reports/tmp_schema_change_proposal_demo`

## Explicit reminders

- Do not treat assumptions as facts.
- Do not add raw numbers without source metadata.
- Do not add live price values without timestamp and source.
- Do not move business logic into adapters.
- Do not change rating or signal behavior through adapter output.
- Do not add price targets.
- Do not add buy/sell/hold recommendations.
- Do not add personal investment advice.
- Do not add broker/order behavior.
- Do not add trading logic.
