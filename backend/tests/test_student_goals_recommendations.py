import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_student_token():
    unique_email = f"student-goals+{uuid.uuid4().hex[:8]}@example.com"
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Student User",
            "email": unique_email,
            "password": "SecurePassword",
            "role": "STUDENT",
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def test_student_recommendations_refresh_and_list():
    token = create_student_token()
    list_response = client.get(
        "/api/student/recommendations",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    assert list_response.json()["items"] == []

    refresh_response = client.post(
        "/api/student/recommendations/refresh",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert refresh_response.status_code == 200
    assert len(refresh_response.json()["items"]) >= 1

    list_response = client.get(
        "/api/student/recommendations",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == len(refresh_response.json()["items"])


def test_student_goal_crud_lifecycle():
    token = create_student_token()
    payload = {
        "goal_type": "SOLVE_PROBLEMS",
        "title": "Solve 5 problems",
        "description": "Practice five problems this week.",
        "target_value": 5,
        "period_start": "2026-07-01",
        "period_end": "2026-07-07",
    }

    create_response = client.post(
        "/api/student/goals",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == 200
    created_goal = create_response.json()
    assert created_goal["title"] == payload["title"]
    assert created_goal["status"] == "ACTIVE"

    list_response = client.get(
        "/api/student/goals",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    assert any(goal["id"] == created_goal["id"] for goal in list_response.json())

    updated_payload = payload.copy()
    updated_payload["title"] = "Solve 10 problems"
    updated_payload["target_value"] = 10
    patch_response = client.patch(
        f"/api/student/goals/{created_goal['id']}",
        json=updated_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["title"] == "Solve 10 problems"
    assert patch_response.json()["target_value"] == 10

    delete_response = client.delete(
        f"/api/student/goals/{created_goal['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "deleted"

    list_response = client.get(
        "/api/student/goals",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    assert all(goal["id"] != created_goal["id"] for goal in list_response.json())
