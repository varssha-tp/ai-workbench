from fastapi.testclient import TestClient

from backend.main import app

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
