import inspect
import re

from pydantic import BaseModel
from pydantic_ai import Agent

from backend.agent.planner import _build_model
from backend.agent.prompts import FINDINGS_SYSTEM_PROMPT
from backend.models import ChartSpec, TableSpec, TaskPlan, WorkflowResult
from backend.services.result_service import result_store
from backend.tools._common import to_records
from backend.tools.data_tools import analyse_dataset, compare_datasets
from backend.tools.document_tools import extract_structured_data, extract_text
from backend.tools.output_tools import create_table, generate_chart

TOOL_FUNCTIONS = {
    "extract_text": extract_text,
    "extract_structured_data": extract_structured_data,
    "analyse_dataset": analyse_dataset,
    "compare_datasets": compare_datasets,
    "generate_chart": generate_chart,
    "create_table": create_table,
}

STEP_REFERENCE_RE = re.compile(r"^\$result_of_step_(\d+)$")


class _Findings(BaseModel):
    summary: str
    findings: list[str]


findings_agent = Agent(
    _build_model(),
    output_type=_Findings,
    system_prompt=FINDINGS_SYSTEM_PROMPT,
)


def resolve_args(args: dict, context: dict[int, str]) -> dict:
    resolved = {}
    for key, value in args.items():
        if isinstance(value, str):
            match = STEP_REFERENCE_RE.match(value)
            if match:
                step_index = int(match.group(1))
                if step_index not in context:
                    raise ValueError(
                        f"Step reference $result_of_step_{step_index} has no result "
                        "(that step hasn't run or produced no result_id)"
                    )
                value = context[step_index]
        resolved[key] = value
    return resolved


async def run_plan(plan: TaskPlan) -> WorkflowResult:
    context: dict[int, str] = {}
    previews: list[str] = []
    text_outputs: list[str] = []
    table_spec: TableSpec | None = None
    chart_spec: ChartSpec | None = None

    for i, call in enumerate(plan.calls, start=1):
        func = TOOL_FUNCTIONS.get(call.tool)
        if func is None:
            raise ValueError(f"Unknown tool: {call.tool}")

        resolved_args = resolve_args(call.args, context)
        result = func(**resolved_args)
        if inspect.iscoroutine(result):
            result = await result

        if isinstance(result, dict) and "result_id" in result:
            context[i] = result["result_id"]

        if call.tool in ("analyse_dataset", "compare_datasets", "extract_structured_data"):
            previews.append(
                f"{call.step}: {result['row_count']} rows, preview: {result['preview']}"
            )
        elif call.tool == "extract_text":
            text_outputs.append(result)
        elif call.tool == "create_table":
            df = result_store.get(result["result_id"])
            table_spec = TableSpec(
                title=result["title"] or plan.goal,
                columns=result["columns"],
                rows=to_records(df),
            )
        elif call.tool == "generate_chart":
            df = result_store.get(result["result_id"])
            chart_spec = ChartSpec(
                chart_type=result["chart_type"],
                x_field=result["x_field"],
                y_field=result["y_field"],
                title=result["title"],
                rows=to_records(df),
            )

    context_lines = list(previews)
    for text in text_outputs:
        context_lines.append(f"Extracted document text (truncated): {text[:3000]}")

    findings_prompt = f"Goal: {plan.goal}\n\n" + "\n\n".join(context_lines)
    findings_result = await findings_agent.run(findings_prompt)
    findings = findings_result.output

    return WorkflowResult(
        goal=plan.goal,
        summary=findings.summary,
        findings=findings.findings,
        table=table_spec,
        chart=chart_spec,
    )
