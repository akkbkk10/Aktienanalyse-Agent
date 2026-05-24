# v1.0.3 Release Notes

## Status

v1.0.3 is a post-v1.0.2 maintenance release focused on
architecture-governance and adapter-readiness documentation. It does not change
application logic, financial logic, DCF math, fair value logic, model rating
behavior, model confidence behavior, model signal behavior, sample company
data, schemas, or generated model calculations.

v1.0.3 does not add any adapter, MCP integration, A2A integration, framework
dependency, live fetching, runtime agent code, project rename, package
publishing, or CLI behavior.

## Maintenance Summary

### PR #48: Adapter Proposal Checklist

- Added `docs/ADAPTER_PROPOSAL_CHECKLIST.md`.
- Documented pre-implementation review questions for future Market Data Agent,
  MCP, A2A, LangGraph/framework, and NVIDIA/GPU tooling proposals.
- Reinforced that adapters are boundary layers and must not move business logic
  out of the deterministic core.
- Linked adapter proposals to guardrail, generated-output, release, and review
  workflows.

### PR #49: Data Contract Review Checklist

- Added `docs/DATA_CONTRACT_REVIEW_CHECKLIST.md`.
- Documented required metadata, field-level traceability, snapshot expectations,
  and prohibited data-contract shortcuts.
- Added examples of acceptable and unacceptable data records.
- Reinforced that future financial figures and adapter-provided data points
  must preserve source, date, unit, period, currency, confidence, and status
  metadata where applicable.

### PR #50: Schema Change Proposal Template

- Added `.github/ISSUE_TEMPLATE/schema_change_proposal.md`.
- Added a proposal workflow for future schema, source-schema, snapshot-format,
  and adapter data-contract changes before implementation.
- Required proposal authors to document affected workflow stages, generated
  artifacts, metadata handling, assumptions, backward compatibility, audit-log
  impact, generated-output review impact, guardrail impact, and required tests.

### PR #51: Adapter Risk Register Template

- Added `docs/ADAPTER_RISK_REGISTER_TEMPLATE.md`.
- Documented risk categories for future adapter proposals, including external
  data source risk, live data freshness risk, source metadata loss risk,
  generated-output safety risk, audit-log traceability risk, guardrail bypass
  risk, framework/vendor lock-in risk, security/privacy risk, and reliability
  risk.
- Added example risks for Market Data Agent, MCP adapter, A2A adapter, and
  framework evaluation proposals.

### PR #52: Adapter Decision Record Template

- Added `docs/ADAPTER_DECISION_RECORD_TEMPLATE.md`.
- Documented how accepted, rejected, deferred, or superseded adapter proposals
  should record decision status, rationale, alternatives, risk review,
  data-contract review, guardrail/security review, generated-output review
  expectations, required tests, implementation boundaries, non-goals, and
  follow-up PRs.
- Reinforced that accepted adapter work must not bypass metadata requirements,
  treat assumptions as facts, alter rating/signal behavior through adapter
  output, or add recommendation, advice, broker/order, or trading behavior.

## Test Status

The local unit suite contains 182 tests.

Required validation commands:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_v1_0_3_release_notes_demo
```

The v1.0 demo validates the deterministic workflow for NVDA, AMD, and TSMC and
writes generated artifacts under `reports/`, which remains ignored by git.

## Upgrade Notes From v1.0.2

No data migration is required. Users can upgrade from v1.0.2 to v1.0.3 by
pulling the release tag and continuing to run the same workflow commands:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py
```

v1.0.3 improves future adapter proposal discipline, data-contract review,
schema-change review, risk tracking, and decision documentation. Existing
generated reports, summaries, DCF outputs, fair value outputs, model ratings,
model confidence outputs, model signals, and audit logs remain compatible with
v1.0.2.

## Explicit Non-Changes

v1.0.3 does not add or change:

- application logic
- financial logic
- DCF math
- fair value per share logic
- model rating behavior
- model confidence behavior
- model signal behavior
- generated report wording
- schemas
- live data fetching
- new companies
- runtime agent code
- MCP integration
- A2A integration
- framework dependencies
- project naming
- package publishing
- CLI behavior
- price targets
- buy/sell/hold recommendations
- personal investment advice
- trading or portfolio logic
