# Orchestrator Agent

## Purpose

Act as the Hub-and-Spoke supervisor contract for the deterministic v1.0.0
workflow. The orchestrator coordinates specialized worker scripts for one ticker
and produces a structured summary.

## Workflow

1. Validate source data.
2. Build or load company context.
3. Detect research gaps.
4. Calculate deterministic ratios.
5. Run valuation readiness.
6. Optionally run deterministic DCF, fair value per share, and model rating.
7. Always run model confidence and model signal from existing artifacts.
8. Optionally generate fact-only reports and structured summaries.
9. Write an audit log record after workflow artifacts are produced.

## Rules

- Run only one ticker per invocation.
- Stop ratio calculation when source validation fails.
- Emit structured JSON with ticker, validation status, research gap count, ratios calculated, artifact paths, model output statuses, audit log status, and warnings.
- Keep this file as a documentation/contract artifact. Do not turn it into a runtime framework.
- Future MCP, A2A, LangChain, CrewAI, OpenAI Agents SDK, or other framework integrations belong in adapter layers around the deterministic Python core.
- Do not create price targets, buy/sell/hold recommendations, personal investment advice, broker/order behavior, automated trading logic, or portfolio logic.

