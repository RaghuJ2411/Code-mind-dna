import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def register_and_login(email: str = "student@example.com") -> str:
    client.post(
        "/api/auth/register",
        json={"full_name": "Career Student", "email": email, "password": "SecurePassword", "role": "STUDENT"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "SecurePassword"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_career_overview_requires_authentication():
    response = client.get("/api/student/career/overview")
    assert response.status_code == 401


def test_career_overview_and_resume_project_interview_workflow():
    token = register_and_login("career_student@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    overview_response = client.get("/api/student/career/overview", headers=headers)
    assert overview_response.status_code == 200
    overview = overview_response.json()
    assert overview["resume_entry_count"] == 0
    assert overview["project_count"] == 0
    assert overview["interview_session_count"] == 0
    assert overview["top_roles"]
    assert "recommended_actions" in overview

    resume_payload = {
        "section": "Experience",
        "title": "Coding Platform Contributor",
        "content": "Built features for practice problem delivery.",
        "skills": ["Algorithms", "Python"],
    }
    resume_response = client.post("/api/student/resume", json=resume_payload, headers=headers)
    assert resume_response.status_code == 200
    resume_entry = resume_response.json()
    assert resume_entry["title"] == resume_payload["title"]

    resume_list = client.get("/api/student/resume", headers=headers)
    assert resume_list.status_code == 200
    assert any(entry["title"] == resume_payload["title"] for entry in resume_list.json())

    project_payload = {
        "title": "Learning Portal",
        "description": "Developed a portal to track student progress.",
        "technologies": ["React", "FastAPI"],
        "outcome": "Increased engagement",
        "project_url": "https://example.com/learning-portal",
    }
    project_response = client.post("/api/student/projects", json=project_payload, headers=headers)
    assert project_response.status_code == 200
    project_entry = project_response.json()
    assert project_entry["title"] == project_payload["title"]

    project_list = client.get("/api/student/projects", headers=headers)
    assert project_list.status_code == 200
    assert any(project["title"] == project_payload["title"] for project in project_list.json())

    interview_payload = {
        "role_name": "Backend Engineer",
        "question": "Describe a time you optimized a slow solution.",
        "answer": "I measured the bottleneck and refactored the loop to use batch operations, reducing runtime by 70%.",
    }
    interview_response = client.post("/api/student/interview/practice", json=interview_payload, headers=headers)
    assert interview_response.status_code == 200
    interview_result = interview_response.json()
    assert interview_result["feedback_score"] >= 20

    history_response = client.get("/api/student/interview/history", headers=headers)
    assert history_response.status_code == 200
    history = history_response.json()
    assert any(entry["question"] == interview_payload["question"] for entry in history)

    overview_response_after = client.get("/api/student/career/overview", headers=headers)
    assert overview_response_after.status_code == 200
    overview_after = overview_response_after.json()
    assert overview_after["resume_entry_count"] == 1
    assert overview_after["project_count"] == 1
    assert overview_after["interview_session_count"] == 1
