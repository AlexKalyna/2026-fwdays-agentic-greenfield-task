# Agent instructions — «Неділя на вагах»

This repo uses spec-driven development (SDD) with a two-layer doc model for
context engineering.

## Before writing code

1. Read [`docs/product-overview.md`](docs/product-overview.md) — static context:
   product narrative, user flows, tone, and out-of-scope items.
2. Read [`docs/prd.md`](docs/prd.md) — authoritative spec with stable IDs
   (`FR-*`, `NFR-*`, `TC-*`, `BC-*`).

Do not expand scope beyond the PRD without updating `docs/prd.md` first.

## Project layout

Bot code lives under `nedilya-na-vagakh/` (see `TC-STACK-03`):

- Python 3.11+, `python-telegram-bot`, SQLite
- Unit tests for pure logic (parse, compare, trends, messages) — `NFR-TEST-01`
- Secrets via environment variables — `NFR-OPS-01`

## Implementation rules

- Implement against PRD requirement IDs; cite IDs in commit messages where
  practical (e.g. `feat(log): accept comma decimals (FR-LOG-03)`).
- Name tests after the behavior they verify and reference IDs in docstrings or
  test names when helpful (e.g. `test_parse_decimal_comma` → `FR-LOG-03`).
- All user-facing bot text must be Ukrainian — `NFR-I18N-01`.
- Keep tone supportive and non-judgmental — `BC-TONE-01`.
- When a requirement is implemented and verified, update its status in
  `docs/prd.md` from `proposed` → `accepted` → `shipped`.

## Verification (maker ≠ checker)

After implementing a capability:

1. Run unit tests (`pytest` from `nedilya-na-vagakh/`).
2. Map behavior back to PRD rows — confirm each `FR-*` for that capability is
   covered by code and/or tests.
3. For integration checks, exercise the bot manually or with targeted tests for
   command handlers.

Do not mark requirements `shipped` without passing tests or explicit manual
verification.

## Out of scope for v1

Do not implement items listed under "Out of scope" in `docs/prd.md` or
`docs/product-overview.md` (OCR, LLM insights, charts, multi-user access, web UI).