import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_user(email: str, role: str) -> str:
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": f"{role.capitalize()} User",
            "email": email,
            "password": "SecurePassword",
            "role": role,
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def get_user_id(token: str) -> int:
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    return response.json()["id"]


def test_mentor_can_create_and_list_career_reviews():
    mentor_token = create_user(f"mentor-career-{uuid.uuid4().hex[:8]}@example.com", "MENTOR")
    student_token = create_user(f"student-career-{uuid.uuid4().hex[:8]}@example.com", "STUDENT")
    mentor_id = get_user_id(mentor_token)
    student_id = get_user_id(student_token)

    review_payload = {
        "student_id": student_id,
        "role_id": None,
        "note": "Strong problem-solving skills, focus on resume examples.",
        "review_type": "CAREER",
    }

    create_response = client.post(
        "/api/mentor/career-reviews",
        headers={"Authorization": f"Bearer {mentor_token}"},
        json=review_payload,
    )
    assert create_response.status_code == 200
    review = create_response.json()
    assert review["mentor_id"] == mentor_id
    assert review["student_id"] == student_id
    assert review["note"] == review_payload["note"]

    list_response = client.get(
        "/api/mentor/career-reviews",
        headers={"Authorization": f"Bearer {mentor_token}"},
    )
    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == 1
    assert list_response.json()["items"][0]["note"] == review_payload["note"]


def test_mentor_can_list_career_roles_for_review():
    mentor_token = create_user(f"mentor-career-roles-{uuid.uuid4().hex[:8]}@example.com", "MENTOR")

    response = client.get(
        "/api/mentor/career-reviews/roles",
        headers={"Authorization": f"Bearer {mentor_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1
    assert all("id" in role and "name" in role for role in response.json())
