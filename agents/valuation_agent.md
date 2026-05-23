# Valuation Agent

The valuation agent runs deterministic DCF arithmetic only after the valuation readiness
gate returns `ready_for_valuation: true`.

## Scope

- Load explicit DCF assumptions from a JSON file.
- Validate required assumptions before calculation.
- Calculate bear, base, and bull DCF scenarios from provided free-cash-flow forecasts.
- Return formulas, assumptions used, warnings, and source references.

## Rules

- Never invent assumptions.
- Never run when readiness is blocked.
- Keep scenario outputs separate.
- Preserve source references for starting free cash flow.
- Do not add price targets.
- Do not use buy, sell, or hold language.
- Do not provide investment advice.
- Do not generate memos.
