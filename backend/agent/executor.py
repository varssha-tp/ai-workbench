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
TEXT_OUTPUT_CHAR_LIMIT = 12_000


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

    # Safety net: if the plan computed structured data (via analyse_dataset,
    # compare_datasets, or extract_structured_data) but never explicitly
    # surfaced it with create_table/generate_chart, show it anyway — a
    # computed result the user can't see is worse than an unrequested table,
    # and the model doesn't reliably remember this extra step (verified: a
    # reasonable-sounding goal produced no table 3/8 times in testing).
    if table_spec is None and chart_spec is None and context:
        last_result_id = context[max(context.keys())]
        df = result_store.get(last_result_id)
        if df is not None:
            table_spec = TableSpec(title=plan.goal, columns=list(df.columns), rows=to_records(df))

    context_lines = list(previews)
    for text in text_outputs:
        # extract_text itself caps at 20k chars; this second cap just keeps
        # the findings prompt bounded — 3k was cutting off later sections of
        # real multi-part documents (e.g. a form's later reflection
        # paragraphs), causing summaries to lean on whatever metadata
        # appeared early and skip substantive content that came later.
        context_lines.append(f"Extracted document text (truncated): {text[:TEXT_OUTPUT_CHAR_LIMIT]}")

    # Tell the findings model explicitly when a table/chart is ALSO being
    # shown directly to the user — otherwise it tends to just transcribe
    # every row as a "finding" (verified: reproduced this exact behaviour
    # in testing), which is pure duplication since the user can already see
    # the table right below.
    if table_spec is not None:
        context_lines.append(
            f"Note: the full table '{table_spec.title}' ({len(table_spec.rows)} rows, "
            f"columns: {table_spec.columns}) is ALSO shown directly to the user, right "
            "below your summary. Do not restate its rows as findings — that would just "
            "duplicate what they can already see. Findings should add something the "
            "table alone doesn't make obvious (a pattern, an extreme, a total, an "
            "exception), or can be omitted if there's nothing beyond the table itself."
        )
    if chart_spec is not None:
        context_lines.append(
            f"Note: a {chart_spec.chart_type} chart '{chart_spec.title}' is ALSO shown "
            "directly to the user. Don't just describe every point on it — call out "
            "what the trend/shape actually means."
        )

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
