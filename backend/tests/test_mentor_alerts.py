import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_mentor_token():
    unique_email = f"mentor-alerts+{uuid.uuid4().hex[:8]}@example.com"
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Mentor User",
            "email": unique_email,
            "password": "SecurePassword",
            "role": "MENTOR",
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def create_student_token():
    unique_email = f"student-alerts+{uuid.uuid4().hex[:8]}@example.com"
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


def get_user_id(token: str) -> int:
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    return response.json()["id"]


def test_mentor_alert_list_and_status_update():
    token = create_mentor_token()
    mentor_id = get_user_id(token)

    response = client.get(
        "/api/mentor/alerts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["items"] == []

    from app.core.database import SessionLocal
    from app.models.mentor_alert import MentorRiskAlert

    db = SessionLocal()
    alert = MentorRiskAlert(
        mentor_id=mentor_id,
        student_id=None,
        alert_type="ENGAGEMENT_DROP",
        severity="HIGH",
        message="Student has low recent activity.",
        status="OPEN",
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    db.close()

    list_response = client.get(
        "/api/mentor/alerts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == 1

    alert_id = list_response.json()["items"][0]["id"]
    ack_response = client.post(
        f"/api/mentor/alerts/{alert_id}/acknowledge",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ack_response.status_code == 200
    assert ack_response.json()["status"] == "ACKNOWLEDGED"

    res_response = client.post(
        f"/api/mentor/alerts/{alert_id}/resolve",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_response.status_code == 200
    assert res_response.json()["status"] == "RESOLVED"


def test_mentor_alert_creation():
    token = create_mentor_token()

    response = client.post(
        "/api/mentor/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "student_id": None,
            "alert_type": "ATTENDANCE_ISSUE",
            "severity": "MEDIUM",
            "message": "Student is missing sessions frequently.",
        },
    )

    assert response.status_code == 200
    alert = response.json()
    assert alert["mentor_id"] is not None
    assert alert["alert_type"] == "ATTENDANCE_ISSUE"
    assert alert["severity"] == "MEDIUM"
    assert alert["message"] == "Student is missing sessions frequently."
    assert alert["status"] == "OPEN"


def test_mentor_alert_generation_is_idempotent():
    mentor_token = create_mentor_token()
    student_token = create_student_token()
    student_id = get_user_id(student_token)

    first_response = client.post(
        f"/api/mentor/alerts/generate?student_id={student_id}",
        headers={"Authorization": f"Bearer {mentor_token}"},
    )
    assert first_response.status_code == 200
    assert len(first_response.json()["items"]) == 1

    second_response = client.post(
        f"/api/mentor/alerts/generate?student_id={student_id}",
        headers={"Authorization": f"Bearer {mentor_token}"},
    )
    assert second_response.status_code == 200
    assert len(second_response.json()["items"]) == 0
