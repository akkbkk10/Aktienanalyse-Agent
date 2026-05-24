# Adapter Proposal Checklist

Use this checklist before implementing future adapter, market data, MCP, A2A,
LangGraph, or framework-evaluation work.

Adapters are future boundary layers. They may connect external systems,
translate data formats, or orchestrate tools, but they must not move business
logic out of the deterministic Python core. Source validation, schema
validation, research gap detection, ratio calculation, valuation readiness,
DCF, fair value per share, model rating, model confidence, model signal,
reports, summaries, and audit logs must remain source-traceable, auditable, and
framework-independent.

Related governance docs:

- `docs/GUARDRAIL_SECURITY_TEST_PLAN.md`
- `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`
- `docs/V1_0_X_PATCH_RELEASE_CHECKLIST.md`

## Proposal Summary

Every adapter proposal should answer these questions before implementation:

- What external system, data source, framework, or tool is being connected?
- What problem does the adapter solve that the deterministic core should not
  solve directly?
- What data contract, snapshot format, or file format is required?
- What source metadata must be preserved from input to output?
- How are source, date, unit, period, URL, confidence, and metric identifiers
  captured?
- How is live-fetching behavior isolated from deterministic calculations?
- How are generated outputs reviewed before merge?
- How are existing guardrails preserved?
- How are audit logs extended without breaking existing traceability?
- What tests are required before implementation?
- What failure modes must be documented?

## Non-Negotiable Boundaries

Future adapters must not:

- move financial, valuation, rating, confidence, signal, report, or summary
  business logic out of the deterministic core
- bypass source validation, schema validation, or audit logging
- invent financial numbers, sources, assumptions, or market data
- produce price targets
- produce buy/sell/hold recommendations
- produce personal investment advice
- perform broker/order behavior
- perform automated trading or portfolio logic
- claim live fetching unless a future adapter explicitly implements,
  validates, tests, and documents it

## Shared Review Checklist

- [ ] The adapter boundary is documented.
- [ ] The deterministic core remains framework-independent.
- [ ] Data enters the core through explicit files, records, or validated
      snapshots.
- [ ] Every financial figure preserves source URL, source date, unit, period,
      confidence, and metric identifier where applicable.
- [ ] Market prices remain stored snapshots with `as_of_datetime` and
      `fetched_at`.
- [ ] Adapter failures fail closed with clear errors, validation failures, or
      research gaps.
- [ ] Generated outputs are reviewed using
      `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`.
- [ ] Guardrails are reviewed using `docs/GUARDRAIL_SECURITY_TEST_PLAN.md`.
- [ ] Audit logs continue to record validation status, source files used, and
      generated artifact paths where applicable.
- [ ] Tests cover success, validation failure, missing metadata, stale data,
      external-system failure, and forbidden-output behavior.
- [ ] Generated artifacts remain under ignored `reports/tmp_*` paths and are
      not committed.

## Market Data Agent Proposal

Use this section for future market data snapshot work.

- [ ] Identify the provider or data source.
- [ ] Define the snapshot schema before any fetching code is added.
- [ ] Preserve `ticker`, `metric_id`, `value`, `currency`, `exchange`,
      `price_type`, `as_of_datetime`, `fetched_at`, `source_url`,
      `source_date`, `provider`, `retrieval_method`, `confidence`, and
      `last_verified`.
- [ ] Document freshness rules and stale-data behavior.
- [ ] Confirm stale or missing market price blocks only model rating,
      confidence, and signal behavior where intended, not ratios, DCF, reports,
      summaries, or audit logging.
- [ ] Confirm the deterministic core does not fetch live data directly.
- [ ] Add fixed tests that do not require network access.
- [ ] Document provider failure, rate limit, malformed response, stale
      snapshot, missing field, and confidence downgrade behavior.

## MCP Adapter Proposal

Use this section for future Model Context Protocol adapter work.

- [ ] Identify the MCP server and exact resources or tools needed.
- [ ] Document what data crosses the MCP boundary.
- [ ] Confirm MCP output is converted into deterministic input files or
      validated records before core analysis uses it.
- [ ] Confirm source metadata and audit references survive the MCP boundary.
- [ ] Confirm MCP availability is not required for existing offline tests.
- [ ] Add tests with fixed fixtures or mocked adapter output.
- [ ] Document unavailable server, malformed response, permission failure, and
      partial-data failure modes.

## A2A Adapter Proposal

Use this section for future agent-to-agent adapter work.

- [ ] Identify the external agent, message protocol, and trust boundary.
- [ ] Document allowed message types and rejected message types.
- [ ] Confirm no external agent can inject financial numbers without validation.
- [ ] Confirm no external agent can bypass guardrails or audit logging.
- [ ] Confirm external agent output is treated as proposed input, not verified
      fact, until source validation passes.
- [ ] Add tests for invalid messages, missing metadata, conflicting values, and
      blocked recommendation language.
- [ ] Document timeout, unavailable agent, conflicting response, and unsafe
      response behavior.

## LangGraph Or Other Framework Evaluation Proposal

Use this section for LangGraph, LangChain, CrewAI, OpenAI Agents SDK, Microsoft
Agent Framework, or similar framework evaluations.

- [ ] State whether the work is documentation-only, prototype-only, or intended
      for runtime integration.
- [ ] Confirm no framework dependency is added to the deterministic core.
- [ ] Confirm framework code does not own source validation, calculations,
      ratings, confidence, signals, reporting, summaries, or audit logs.
- [ ] Keep framework orchestration in an adapter layer that calls the existing
      scripts or consumes existing structured outputs.
- [ ] Add tests proving the core workflow still runs without the framework.
- [ ] Document framework failure, dependency conflict, version drift, and
      adapter-disabled behavior.

## NVIDIA Or GPU/Tooling Evaluation Proposal

Use this section for NVIDIA NIM, RAPIDS, cuDF, NeMo, GPU acceleration, or other
tooling evaluations.

- [ ] Identify the tool and the exact workflow step being evaluated.
- [ ] Confirm deterministic numerical outputs remain identical or differences
      are explicitly explained and reviewed.
- [ ] Confirm GPU/tooling dependencies are not required for the baseline core
      workflow.
- [ ] Confirm no generated output claims improved investment accuracy,
      predictive certainty, or advice quality.
- [ ] Add tests or comparison fixtures for deterministic parity where
      applicable.
- [ ] Document unavailable hardware, unsupported platform, dependency failure,
      numerical drift, and fallback behavior.

## Required Tests Before Implementation

Before implementation begins, the proposal should list the tests that will be
added or updated. At minimum, future adapter PRs should plan for:

- unit tests for the adapter boundary
- validation tests for required metadata
- stale or missing data tests
- failure-mode tests
- generated-output forbidden-language tests
- audit-log traceability tests
- offline tests that do not require network access
- full suite validation:

```bash
python -m unittest discover -s tests
```

- v1.0 demo validation into an ignored reports path:

```bash
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_adapter_proposal_demo
```

## Required Review Artifacts

Adapter proposals should identify review evidence before coding begins:

- data contract or schema draft
- sample fixed input fixture
- expected validation result
- expected generated-output behavior
- expected audit-log fields
- failure-mode table
- guardrail impact summary
- generated-output review plan

Generated reports, summaries, model outputs, and audit logs may be generated for
review, but must not be committed.
