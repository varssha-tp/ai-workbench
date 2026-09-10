from pydantic import BaseModel


class TaskPlan(BaseModel):
    goal: str
    steps: list[str]
    tools: list[str]


class GoalRequest(BaseModel):
    goal: str
