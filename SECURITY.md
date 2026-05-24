# Security Policy

Aktienanalyse Agent is a deterministic analysis core. Security reports are most
useful when they explain how a change could bypass validation, source
traceability, audit logging, output guardrails, or repository hygiene.

## Reporting A Vulnerability

Use GitHub private vulnerability reporting if it is available for this
repository.

If private vulnerability reporting is not available, open a minimal public issue
without sensitive details. Include only enough information for maintainers to
understand the affected area, then wait for a maintainer to coordinate next
steps.

Do not post secrets, tokens, private source material, exploit payloads, or
sensitive financial data in public issues.

## In Scope

- Validation bypasses that allow unsourced financial figures.
- Ways to invent or alter source metadata without detection.
- Paths that skip audit-log creation for successful analysis runs.
- Generated outputs that create price targets, recommendations, personal
  investment advice, broker/order behavior, or automated trading language.
- Future adapter proposals that fetch live data without a validated snapshot
  contract.
- Accidental commit risk for generated reports, local environment files, or
  sensitive local artifacts.

## Out Of Scope

- Requests for personal investment advice.
- Disagreement with deterministic sample assumptions or model outputs.
- Live market data freshness requests when no live adapter exists.
- Issues requiring broker, order, portfolio, or trading behavior.

## Guardrail Expectations

Security fixes must preserve deterministic core behavior, source traceability,
auditability, and the no-investment-advice boundary. Framework-specific business
logic must not be moved into the deterministic core.
