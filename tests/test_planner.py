from fastapi.testclient import TestClient

from backend.agent.planner import _build_prompt
from backend.main import app
from backend.models import FileMeta

client = TestClient(app)


def test_plan_endpoint_returns_task_plan():
    response = client.post(
        "/plan",
        json={"goal": "Find products whose sales dropped by more than 20%"},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["goal"]
    assert isinstance(body["steps"], list) and len(body["steps"]) > 0
    assert isinstance(body["tools"], list) and len(body["tools"]) > 0


def test_plan_endpoint_resolves_uploaded_files():
    upload_response = client.post(
        "/upload",
        files=[("files", ("January.xlsx", b"fake xlsx bytes", "application/octet-stream"))],
    )
    file_id = upload_response.json()[0]["file_id"]

    response = client.post(
        "/plan",
        json={"goal": "Summarise this file", "file_ids": [file_id]},
    )
    assert response.status_code == 200


def test_plan_endpoint_rejects_unknown_file_id():
    response = client.post(
        "/plan",
        json={"goal": "Summarise this file", "file_ids": ["does-not-exist"]},
    )
    assert response.status_code == 404


def test_plan_endpoint_rejects_empty_goal():
    response = client.post("/plan", json={"goal": ""})
    assert response.status_code == 422


def test_plan_endpoint_rejects_whitespace_only_goal():
    response = client.post("/plan", json={"goal": "   "})
    assert response.status_code == 422


def test_execute_endpoint_rejects_empty_goal():
    response = client.post("/execute", json={"goal": ""})
    assert response.status_code == 422


def test_build_prompt_includes_filenames_deterministically():
    files = [FileMeta(file_id="abc-123", filename="January.xlsx", file_type="excel", size_bytes=10)]
    prompt = _build_prompt("Find the sales trend", files)
    assert "January.xlsx" in prompt
    assert "excel" in prompt
    assert "abc-123" in prompt
    assert "Find the sales trend" in prompt


def test_build_prompt_without_files_is_just_the_goal():
    assert _build_prompt("Find the sales trend", None) == "Find the sales trend"
