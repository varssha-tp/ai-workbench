from typing import Any, Literal

from pydantic import BaseModel, computed_field, field_validator

ToolName = Literal[
    "extract_text",
    "extract_structured_data",
    "analyse_dataset",
    "compare_datasets",
    "generate_chart",
    "create_table",
]


class ToolCall(BaseModel):
    step: str
    tool: ToolName
    args: dict[str, Any]


class TaskPlan(BaseModel):
    goal: str
    calls: list[ToolCall]

    @computed_field
    @property
    def steps(self) -> list[str]:
        return [c.step for c in self.calls]

    @computed_field
    @property
    def tools(self) -> list[str]:
        return [c.tool for c in self.calls]


class GoalRequest(BaseModel):
    goal: str
    file_ids: list[str] = []

    @field_validator("goal")
    @classmethod
    def goal_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("goal must not be empty")
        return value


class FileMeta(BaseModel):
    file_id: str
    filename: str
    file_type: str
    size_bytes: int


class TableSpec(BaseModel):
    title: str
    columns: list[str]
    rows: list[dict[str, Any]]


class ChartSpec(BaseModel):
    chart_type: Literal["bar", "line", "pie"]
    x_field: str
    y_field: str
    title: str
    rows: list[dict[str, Any]]


class WorkflowResult(BaseModel):
    goal: str
    summary: str
    findings: list[str]
    table: TableSpec | None = None
    chart: ChartSpec | None = None
