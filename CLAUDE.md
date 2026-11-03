# Notes for Claude

This is a learning project: the owner is building it step by step so they can understand and explain every part.

- Follow docs/PLAN.md phase by phase. Ask before adding a tool or language that isn't in the plan.
- Teach as you go: explain why before writing code and keep code short and commented. Quizzes are optional: offer one quick check at the end of a step, but never let a quiz block the work.
- Never commit `data/raw/` files or `.env`.
- Run checks with `.venv/bin/python -m pytest`.
- Pipeline: `python -m salevora.load_data`, then `python -m salevora.forecast`. App: `streamlit run app/Home.py`. API: `uvicorn api.main:app`.
- MySQL 8.4 runs locally as a Homebrew service (`brew services start mysql@8.4`). It is keg-only, so the client is at `/opt/homebrew/opt/mysql@8.4/bin/mysql`.
