from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_chat_endpoint():
    response = client.post("/chat", json={"message": "Hello", "patient_id": "123"})
    assert response.status_code == 200
    assert response.json()["intent"] in {"general", "appointment", "billing", "insurance", "refill", "case", "timeline"}


def test_chat_endpoint_runs_agentic_workflow_response():
    response = client.post(
        "/chat",
        json={"message": "I need help with my insurance", "patient_id": "123"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "insurance"
    assert payload["reply"] == "Handled request: I need help with my insurance"


def test_patient_endpoint():
    response = client.get("/patients/123")
    assert response.status_code == 200
    assert response.json()["patient_id"] == "123"
