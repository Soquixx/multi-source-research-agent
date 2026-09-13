from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }

def test_research_requires_question():
    response = client.post(
        "/research",
        json={},
    )

    assert response.status_code == 422


def test_research_rejects_short_question():
    response = client.post(
        "/research",
        json={
            "question": "Hi",
        },
    )

    assert response.status_code == 422