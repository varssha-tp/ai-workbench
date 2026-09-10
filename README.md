# AI Workbench

AI Workbench turns uploaded files (PDF, CSV, Excel) and a plain-language goal into a useful result — a summary, analysis, table, chart, or finding — by planning and executing the necessary steps automatically. Built for GIBC V2, Track 03 (Open).

This repo is at an early stage: the AI planner pipeline (goal → structured plan) is working; file upload, tool execution, and the frontend are not yet built.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env          # optional: add OPENROUTER_API_KEY to use a real model
```

Without an `OPENROUTER_API_KEY`, the planner runs against Pydantic AI's `TestModel`, which returns schema-valid stub output with no network call — useful for development without an API key.

## Run

```bash
uvicorn backend.main:app --reload
```

Open `http://127.0.0.1:8000/docs` and try `POST /plan` with a body like:

```json
{"goal": "Find products whose sales dropped by more than 20%"}
```

## Test

```bash
pytest
```

## AI usage disclosure

Built with assistance from Claude Code (Anthropic). This section will be expanded as the project grows to note which parts were AI-assisted, per the GIBC V2 disclosure requirement.
