# «Неділя на вагах» — Telegram bot

Private Ukrainian-language bot for tracking body-composition weigh-ins.
Product context: [`../docs/product-overview.md`](../docs/product-overview.md).
Requirements: [`../docs/prd.md`](../docs/prd.md).

## Requirements

- Python **3.11+** (`TC-STACK-01`) — `.python-version` pins `3.11` for pyenv
- Telegram bot token and allowlisted user IDs in `.env` (copy from `.env.example`)

Install Python 3.11 if needed:

```bash
brew install python@3.11    # Homebrew
# or: pyenv install 3.11 && pyenv local 3.11
```

## Setup

One command creates a Python 3.11 virtualenv, installs dependencies, and registers git hooks:

```bash
make dev-install
source .venv/bin/activate
```

Manual venv (equivalent):

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

## Run the bot

```bash
source .venv/bin/activate
cp .env.example .env   # fill in BOT_TOKEN and ALLOWED_USER_IDS
python -m bot
```

## Development

| When | What runs |
|------|-----------|
| `git commit` | Ruff lint/format, mypy, file hygiene |
| `git push` | Full `pytest` suite |
| Manual | `make check` — lint + mypy + pytest (same as CI) |

### Commands

```bash
make lint       # ruff check
make format     # auto-fix lint + format
make typecheck  # mypy bot
make test       # pytest
make check      # all of the above (use before /opsx:archive)
```

All `make` targets use `.venv/bin/python` when present, otherwise `python3.11`.

### CI

GitHub Actions (`.github/workflows/ci.yml`) runs the same checks on Python 3.11 and
3.12 for every push and pull request.

## License

MIT — see [LICENSE](LICENSE).
