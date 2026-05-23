# Research Gap Agent

## Purpose

Find missing or weak evidence in company context files and create research queue items for follow-up.

## Inputs

- `config/watchlist.json`
- `data/companies/<TICKER>/context.json`

## Outputs

- Research queue entries in `research_queue.json`
- Readable queue entries in `research_queue.md`

## Rules

- Detect missing required metrics.
- Detect stale metrics using the configured `max_last_verified_age_days`.
- Detect missing source metadata.
- Detect low-confidence data.
- Create research queue entries for detected gaps.
- Do not implement valuation, DCF, ratios, memo generation, recommendations, or price targets.
- Keep facts, assumptions, and opinions separate.
- Preserve GAAP and Non-GAAP labels from source context.

