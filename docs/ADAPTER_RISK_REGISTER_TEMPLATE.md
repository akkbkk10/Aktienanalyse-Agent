# Adapter Risk Register Template

Use this template before implementing future adapter proposals. The goal is to
make trust boundaries, failure modes, source risks, data-contract risks, and
guardrail risks explicit while the work is still easy to reshape.

Related governance docs:

- `docs/ADAPTER_PROPOSAL_CHECKLIST.md`
- `docs/DATA_CONTRACT_REVIEW_CHECKLIST.md`
- `docs/GUARDRAIL_SECURITY_TEST_PLAN.md`
- `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`

## Risk Categories

Future adapter proposals should consider these risk categories:

- external data source risk
- live data freshness/timestamp risk
- source metadata loss risk
- unit/currency/period ambiguity risk
- missing-data handling risk
- assumption-vs-fact confusion risk
- adapter moving business logic out of deterministic core
- generated-output safety risk
- audit-log traceability risk
- guardrail bypass risk
- framework/vendor lock-in risk
- security/privacy risk
- reliability/failure-mode risk

## Risk Table

Use one row per meaningful risk.

| Risk id | Risk description | Affected workflow stage | Likelihood | Impact | Mitigation | Required tests or review evidence | Owner/status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 |  |  | Low / Medium / High | Low / Medium / High |  |  |  |

Recommended status values:

- proposed
- accepted
- mitigated
- blocked
- deferred

## Example Risk Entries

These examples are illustrative. Replace them with proposal-specific risks.

| Risk id | Risk description | Affected workflow stage | Likelihood | Impact | Mitigation | Required tests or review evidence | Owner/status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MD-001 | Market Data Agent returns a live price without `as_of_datetime`, `fetched_at`, or provider metadata. | market price snapshot, model rating, model confidence, model signal | Medium | High | Require snapshot validation before model outputs can consume market price data. | Missing timestamp test, missing provider test, stale snapshot test, data contract review. | owner TBD / proposed |
| MCP-001 | MCP adapter output loses source URL or source date while translating external data into core input files. | source validation, company context, reports, audit logs | Medium | High | Treat MCP output as proposed input until schema and source validation pass. | Fixture with missing source metadata, validation failure evidence, audit-log traceability review. | owner TBD / proposed |
| A2A-001 | External agent response mixes assumptions with sourced facts. | source validation, summaries, reports, model confidence | Medium | High | Require explicit fact/assumption separation and manual-review status before downstream use. | Invalid message test, assumption labeling test, generated-output review. | owner TBD / proposed |
| FW-001 | Framework evaluation moves orchestration-time business rules into LangGraph or another runtime adapter. | orchestrator, ratios, DCF, model outputs | Low | High | Keep framework code as an adapter that calls deterministic scripts or consumes structured outputs. | Core workflow runs without framework, diff review showing no core logic moved. | owner TBD / proposed |

## Market Data Agent Risks

- Does the proposal define immutable snapshot records before any downstream
  model output consumes market prices?
- Can stale, missing, or malformed market data block only the intended model
  outputs without blocking unrelated workflow stages?
- Are provider, retrieval method, source URL/reference, `as_of_datetime`, and
  `fetched_at` preserved?
- Are tests fixed and offline, or do they depend on live network behavior?

## MCP Adapter Risks

- What MCP server, resource, or tool is trusted?
- What data crosses the MCP boundary?
- Can the adapter fail closed when the server is unavailable or returns partial
  data?
- Does the adapter preserve source metadata and audit references?
- Can existing offline tests run without the MCP server?

## A2A Adapter Risks

- What external agent or message protocol is trusted?
- Can external messages inject financial figures without source validation?
- Can external messages bypass guardrails, manual review, or audit logging?
- Are unsafe, conflicting, incomplete, or recommendation-like responses
  rejected?

## Framework Evaluation Risks

- Is the framework code clearly outside deterministic core business logic?
- Can the baseline workflow run without the framework dependency?
- Does the framework adapter preserve source traceability and auditability?
- Are dependency conflicts, version drift, disabled-adapter behavior, and
  runtime failures documented?

## Review Checklist

- [ ] Risk categories have been reviewed.
- [ ] Risk table has at least one row for every material adapter risk.
- [ ] Trust boundaries are documented.
- [ ] Data-contract risks reference `docs/DATA_CONTRACT_REVIEW_CHECKLIST.md`.
- [ ] Generated-output risks reference `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`.
- [ ] Guardrail risks reference `docs/GUARDRAIL_SECURITY_TEST_PLAN.md`.
- [ ] Required tests or review evidence are listed for each high-impact risk.
- [ ] No risk mitigation relies on moving business logic out of the
      deterministic core.
- [ ] No risk mitigation permits price targets, buy/sell/hold recommendations,
      personal investment advice, broker/order behavior, or trading logic.
