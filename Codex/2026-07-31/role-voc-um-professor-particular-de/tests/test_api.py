from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_requires_message() -> None:
    response = client.post("/api/v1/chat", json={"message": ""})
    assert response.status_code == 422


def test_chat_returns_teaching_format() -> None:
    response = client.post("/api/v1/chat", json={"message": "O que é print?", "student_level": 1})
    assert response.status_code == 200
    assert "📚" in response.json()["reply"]
