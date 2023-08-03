# tests/test_main.py

from fastapi.testclient import TestClient
from main import app
from app.models import ProjectCreate

client = TestClient(app)

def test_user_signup():
    response = client.post(
        "/api/signup",
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "id" in response.json()

def test_user_login():
    response = client.post(
        "/api/login",
        data={"username": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_project():
    response = client.post(
        "/api/projects",
        json={"name": "Test Project"},
        headers={"Authorization": "Bearer <access_token>"}  # replace <access_token> with actual token
    )
    assert response.status_code == 200
    assert "id" in response.json()
    