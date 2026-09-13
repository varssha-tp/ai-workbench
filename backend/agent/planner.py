import os

import pandas as pd
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from backend.agent.prompts import PLANNER_SYSTEM_PROMPT
from backend.models import FileMeta, TaskPlan
from backend.services.file_service import file_store


def _build_model():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return TestModel()

    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openrouter import OpenRouterProvider

    return OpenAIChatModel(
        "openai/gpt-4o-mini",
        provider=OpenRouterProvider(api_key=api_key),
    )


planner_agent = Agent(
    _build_model(),
    output_type=TaskPlan,
    system_prompt=PLANNER_SYSTEM_PROMPT,
)


def _describe_columns(meta: FileMeta) -> str | None:
    """Best-effort real column names for a CSV/Excel file, so the planner
    knows actual column names instead of guessing from the filename (a
    repeated, reproducible source of wrong-column-name plans)."""
    if meta.file_type not in ("csv", "excel"):
        return None
    path = file_store.get_path(meta.file_id)
    if path is None:
        return None
    try:
        if meta.file_type == "csv":
            df = pd.read_csv(path, nrows=1)
        else:
            df = pd.read_excel(path, nrows=1)
        return ", ".join(str(c) for c in df.columns)
    except Exception:
        return None


def _build_prompt(goal: str, files: list[FileMeta] | None) -> str:
    if not files:
        return goal

    file_lines = []
    for f in files:
        line = f"- {f.filename} ({f.file_type}), file_id: {f.file_id}"
        columns = _describe_columns(f)
        if columns:
            line += f", columns: {columns}"
        file_lines.append(line)

    return "Files provided:\n" + "\n".join(file_lines) + f"\n\nGoal: {goal}"


async def create_plan(goal: str, files: list[FileMeta] | None = None) -> TaskPlan:
    prompt = _build_prompt(goal, files)
    result = await planner_agent.run(prompt)
    return result.output
