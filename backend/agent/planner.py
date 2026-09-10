import os

from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from backend.agent.prompts import PLANNER_SYSTEM_PROMPT
from backend.models import TaskPlan


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


async def create_plan(goal: str) -> TaskPlan:
    result = await planner_agent.run(goal)
    return result.output
