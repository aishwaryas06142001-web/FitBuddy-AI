import os
os.environ["MOCK_AI"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test_fitbuddy.db"

from fastapi.testclient import TestClient
from app.main import app

def test_home():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "FitBuddy" in response.text

def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

def test_generate_and_feedback():
    with TestClient(app) as client:
        response = client.post("/generate-workout", data={
            "name":"Test User","user_id":"test001","age":"30","weight":"70",
            "goal":"muscle gain","intensity":"medium"
        })
        assert response.status_code == 200
        assert "7-Day Workout Plan" in response.text

        response = client.post("/submit-feedback", data={
            "user_id":"test001","feedback":"Add more cardio and one extra recovery day."
        })
        assert response.status_code == 200
        assert "updated" in response.text.lower()
