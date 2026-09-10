import os

from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from backend.agent.prompts import PLANNER_SYSTEM_PROMPT
from backend.models import FileMeta, TaskPlan


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


def _build_prompt(goal: str, files: list[FileMeta] | None) -> str:
    if not files:
        return goal

    file_lines = "\n".join(f"- {f.filename} ({f.file_type})" for f in files)
    return f"Files provided:\n{file_lines}\n\nGoal: {goal}"


async def create_plan(goal: str, files: list[FileMeta] | None = None) -> TaskPlan:
    prompt = _build_prompt(goal, files)
    result = await planner_agent.run(prompt)
    return result.output
