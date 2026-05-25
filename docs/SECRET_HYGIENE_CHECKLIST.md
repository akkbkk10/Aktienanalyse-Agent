# Secret Hygiene Checklist

Use this checklist before opening public issues or pull requests. It is
repository-file guidance only; maintainers must still verify GitHub secret
scanning and push protection settings in GitHub.

## Before Opening A Pull Request

- Do not commit API keys, tokens, passwords, cookies, private URLs, private
  source material, customer data, brokerage data, portfolio data, or sensitive
  financial data.
- Do not commit `.env`, `.env.*`, virtual environments, caches, generated
  reports, summaries, DCF outputs, model outputs, audit logs, or local
  experiment artifacts.
- Keep generated artifacts under ignored `reports/tmp_*` paths unless a
  maintainer explicitly asks for a reviewed artifact.
- Inspect staged changes before pushing:

```bash
git status --short
git diff --cached
```

- If a secret or sensitive file was committed locally, stop and rotate the
  secret before asking for review. Do not post the secret in an issue, pull
  request, comment, screenshot, or generated report.

## Public Issue And Security Reporting Rules

- Use `SECURITY.md` for vulnerability reporting.
- Do not put exploit payloads, secrets, private source material, or sensitive
  financial data in public issues.
- If private vulnerability reporting is not available, open only a minimal
  public issue that names the affected area and wait for a maintainer to
  coordinate next steps.

## Project Boundary

Secret hygiene does not change the project scope. This repository remains a
deterministic, evidence-based analysis core and does not provide investment
advice, price targets, buy/sell/hold recommendations, live data fetching,
broker/order behavior, trading logic, portfolio automation, web UI, or runtime
adapter implementation.
