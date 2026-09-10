from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile

load_dotenv()

from backend.agent.planner import create_plan
from backend.models import FileMeta, GoalRequest, TaskPlan
from backend.services.file_service import file_store

app = FastAPI(title="AI Workbench")


@app.post("/upload", response_model=list[FileMeta])
async def upload(files: list[UploadFile]) -> list[FileMeta]:
    metas = []
    for upload_file in files:
        content = await upload_file.read()
        try:
            metas.append(file_store.save(upload_file.filename, content))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    return metas


@app.get("/files", response_model=list[FileMeta])
async def list_files() -> list[FileMeta]:
    return file_store.list()


@app.post("/plan", response_model=TaskPlan)
async def plan(request: GoalRequest) -> TaskPlan:
    files = []
    for file_id in request.file_ids:
        meta = file_store.get(file_id)
        if meta is None:
            raise HTTPException(status_code=404, detail=f"Unknown file_id: {file_id}")
        files.append(meta)

    return await create_plan(request.goal, files)
