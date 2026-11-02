# Notes for Claude

This is a learning project: the owner is building it step by step so they can understand and explain every part.

- Follow docs/PLAN.md phase by phase. Ask before adding a tool or language that isn't in the plan.
- Teach as you go: explain why before writing code, keep code short and commented, and check understanding with a quick question (multiple-choice buttons work best).
- Never commit `data/raw/` files or `.env`.
- Run checks with `.venv/bin/python -m pytest`.
- MySQL 8.4 runs locally as a Homebrew service (`brew services start mysql@8.4`). It is keg-only, so the client is at `/opt/homebrew/opt/mysql@8.4/bin/mysql`.
