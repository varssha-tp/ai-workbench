from pydantic import BaseModel


class TaskPlan(BaseModel):
    goal: str
    steps: list[str]
    tools: list[str]


class GoalRequest(BaseModel):
    goal: str
    file_ids: list[str] = []


class FileMeta(BaseModel):
    file_id: str
    filename: str
    file_type: str
    size_bytes: int
