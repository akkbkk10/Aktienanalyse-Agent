# Adapter Decision Record Template

Use this template after an adapter proposal is reviewed and before
implementation begins. It records whether a future Market Data Agent, MCP, A2A,
framework, or tooling integration proposal is accepted, rejected, deferred, or
superseded.

Related governance docs:

- `docs/ADAPTER_PROPOSAL_CHECKLIST.md`
- `docs/ADAPTER_RISK_REGISTER_TEMPLATE.md`
- `docs/DATA_CONTRACT_REVIEW_CHECKLIST.md`
- `docs/GUARDRAIL_SECURITY_TEST_PLAN.md`
- `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`

## Decision Title


## Decision Status

- [ ] accepted
- [ ] rejected
- [ ] deferred
- [ ] superseded

## Date


## Proposal Link


## Related Issue Or PR Links

-

## Summary Of Proposed Adapter Or Integration

Describe the external system, data source, protocol, framework, or tooling being
considered. Include the intended boundary between the adapter and the
deterministic core.


## Decision

State the decision in one or two paragraphs.


## Rationale

Explain why this decision was made. Include maintainability, traceability,
security, guardrail, and testing considerations.


## Alternatives Considered

- 

## Risk Register Link

Link to the completed risk register or proposal issue section based on
`docs/ADAPTER_RISK_REGISTER_TEMPLATE.md`.


## Data Contract Review Outcome

Summarize the outcome of the data contract review.

- [ ] Required metadata is preserved.
- [ ] Source/date/unit/period/currency/confidence handling is clear.
- [ ] Assumptions remain separate from facts.
- [ ] Missing and unavailable data are represented without invented values.
- [ ] Audit logs can reconstruct the workflow.

## Guardrail And Security Review Outcome

Summarize the outcome of the guardrail and security review.

- [ ] No price targets.
- [ ] No buy/sell/hold recommendations.
- [ ] No personal investment advice.
- [ ] No broker/order behavior.
- [ ] No trading or portfolio logic.
- [ ] No unvalidated live fetching.
- [ ] No framework-specific business logic in the deterministic core.

## Generated-Output Review Expectations

List generated artifacts reviewers must inspect if implementation proceeds.

- [ ] fact reports
- [ ] structured analysis summaries
- [ ] DCF outputs
- [ ] fair value per share outputs
- [ ] model rating outputs
- [ ] model confidence outputs
- [ ] model signal outputs
- [ ] audit logs
- [ ] not applicable

## Required Tests Before Implementation

- [ ] unit tests for the adapter boundary
- [ ] source/schema validation tests
- [ ] missing metadata tests
- [ ] stale or unavailable data tests, if applicable
- [ ] failure-mode tests
- [ ] audit-log traceability tests
- [ ] generated-output forbidden-language tests, if generated artifacts change
- [ ] full suite: `python -m unittest discover -s tests`
- [ ] v1.0 demo: `python scripts/run_v1_0_demo.py --reports-dir reports/tmp_adapter_decision_demo`

## Implementation Boundaries

Describe what implementation work is allowed.

- 

## Explicit Non-Goals

Accepted adapter work must not:

- move business logic out of the deterministic core
- bypass source metadata requirements
- treat assumptions as facts
- change rating or signal behavior through adapter output
- add price targets
- add buy/sell/hold recommendations
- add personal investment advice
- add broker/order behavior
- add trading or portfolio logic

Add any proposal-specific non-goals:

-

## Follow-Up PRs

List the expected follow-up PRs if the decision is accepted or deferred.

-
