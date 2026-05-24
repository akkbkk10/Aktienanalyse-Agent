# Architecture Governance Index

This index helps maintainers find the right governance document or template for
common project decisions. It is navigation only and does not create new process
requirements.

## If You Want To...

| If you want to... | Use this document or template | Why |
| --- | --- | --- |
| Understand the current deterministic core baseline | `docs/CORE_BASELINE_INVENTORY.md` | Maps workflow stages, modules, tests, artifacts, guardrails, and v1.1 readiness gaps. |
| Check current data fields and output structures | `docs/SCHEMA_FIELD_REFERENCE.md` | Lists current schema fields and observed output structures. |
| Check generated artifact paths and required files | `docs/REPORT_ARTIFACT_CONTRACT.md` | Documents the current reports directory layout, shared audit log, and required per-ticker v1.0 demo artifacts. |
| Assess generated JSON schema priorities | `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md` | Compares generated artifact schema candidates and recommends the next narrow hardening target. |
| Assess data-contract hardening priorities | `docs/DATA_CONTRACT_SCHEMA_HARDENING_ASSESSMENT.md` | Reviews current schema protections and identifies the next small data-contract hardening candidate. |
| Validate company context contract expectations | `config/company_context_schema.json` | Defines the standalone contract for persistent `data/companies/<TICKER>/context.json` files. |
| Review generated output before merging | `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md` | Helps inspect reports, summaries, model outputs, and audit logs for unsafe wording or traceability issues. |
| Confirm guardrails for core or adapter work | `docs/GUARDRAIL_SECURITY_TEST_PLAN.md` | Defines prohibited behaviors, allowed behaviors, module/test mappings, and security review prompts. |
| Propose a future adapter or framework evaluation | `docs/ADAPTER_PROPOSAL_CHECKLIST.md` | Frames adapter boundaries, required questions, tests, and review artifacts before implementation. |
| Review field-level data contract expectations | `docs/DATA_CONTRACT_REVIEW_CHECKLIST.md` | Covers required metadata, separation of facts/assumptions/calculations, snapshot expectations, and prohibited shortcuts. |
| Propose a schema, source-schema, snapshot, or adapter contract change | `.github/ISSUE_TEMPLATE/schema_change_proposal.md` | Captures the proposal before implementation, including affected stages, metadata, audit impact, and required tests. |
| Track adapter risks | `docs/ADAPTER_RISK_REGISTER_TEMPLATE.md` | Documents risk categories, mitigations, tests, and review evidence. |
| Record an adapter decision | `docs/ADAPTER_DECISION_RECORD_TEMPLATE.md` | Records accepted, rejected, deferred, or superseded adapter proposals and their rationale. |
| Prepare a v1.0.x patch release | `docs/V1_0_X_PATCH_RELEASE_CHECKLIST.md` | Provides release validation, generated-artifact, tag, GitHub Release, and troubleshooting steps. |

## Future Adapter Work Order

For Market Data Agent, MCP, A2A, LangGraph/framework, NVIDIA/GPU tooling, or
similar adapter proposals, use this order:

1. Start with `docs/ADAPTER_PROPOSAL_CHECKLIST.md`.
2. Review data contracts with `docs/DATA_CONTRACT_REVIEW_CHECKLIST.md`.
3. Open `.github/ISSUE_TEMPLATE/schema_change_proposal.md` if schema,
   source-schema, snapshot-format, or adapter data-contract changes are needed.
4. Fill out `docs/ADAPTER_RISK_REGISTER_TEMPLATE.md`.
5. Record the decision with `docs/ADAPTER_DECISION_RECORD_TEMPLATE.md`.
6. Open an implementation PR only after the proposal is reviewed and approved.

Adapter implementation remains out of scope until a proposal, data-contract
review, risk review, and decision record are complete.

## Core Guardrail Reminders

The deterministic core must remain source-traceable, auditable, and
framework-independent. Future work must not add:

- price targets
- buy/sell/hold recommendations
- personal investment advice
- broker/order behavior
- automated trading or portfolio logic
- live data fetching inside deterministic core modules
- framework-specific business logic inside the core

Generated artifacts may be created for review, but must remain under ignored
`reports/tmp_*` paths and must not be committed.
