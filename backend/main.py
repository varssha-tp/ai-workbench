from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from backend.agent.planner import create_plan
from backend.models import GoalRequest, TaskPlan

app = FastAPI(title="AI Workbench")


@app.post("/plan", response_model=TaskPlan)
async def plan(request: GoalRequest) -> TaskPlan:
    return await create_plan(request.goal)
