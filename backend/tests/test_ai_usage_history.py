import pytest
from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models.problem import Problem
from app.models.execution import Submission
from app.models.user import User

client = TestClient(app)


def register_student(email: str):
    response = client.post(
        "/api/auth/register",
        json={"full_name": "Student", "email": email, "password": "SecurePassword", "role": "STUDENT"},
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def create_test_submission(student_id: int) -> Submission:
    db = SessionLocal()
    problem = Problem(
        title="AI Usage Problem",
        slug="ai-usage-problem",
        description="Test problem for AI usage logging",
        difficulty="EASY",
        topic="ARRAYS",
        constraints="None",
        input_format="None",
        output_format="None",
        created_by=student_id,
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    submission = Submission(
        student_id=student_id,
        problem_id=problem.id,
        language='python',
        source_code='print(1)',
        verdict='WRONG_ANSWER',
        passed_test_cases=0,
        total_test_cases=1,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    db.close()
    return submission


def test_student_can_access_ai_usage_history():
    token = register_student("aiusage@example.com")

    response = client.get("/api/student/ai/usage-history", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    payload = response.json()
    assert "daily_summary" in payload
    assert "recent_requests" in payload
    assert payload["recent_requests"] == []

    summary = payload["daily_summary"]
    assert summary["tasks"]["CODE_REVIEW"]["total"] == 0
    assert summary["tasks"]["ERROR_EXPLANATION"]["total"] == 0
    assert summary["tasks"]["SKILL_GAP"]["total"] == 0
    assert summary["tasks"]["ROADMAP"]["total"] == 0
    assert summary["limits"]["CODE_REVIEW"] >= 0


def test_ai_usage_history_includes_logged_requests():
    token = register_student("aiusage-logged@example.com")

    # Create a user and a submission in the same DB used by the test client
    db = SessionLocal()
    user = db.query(User).filter(User.email == "aiusage-logged@example.com").first()
    assert user is not None
    problem = Problem(
        title="AI Usage Problem",
        slug="ai-usage-problem-logged",
        description="Test problem for AI usage logging",
        difficulty="EASY",
        topic="ARRAYS",
        constraints="None",
        input_format="None",
        output_format="None",
        created_by=user.id,
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    submission = Submission(
        student_id=user.id,
        problem_id=problem.id,
        language='python',
        source_code='print(1)',
        verdict='WRONG_ANSWER',
        passed_test_cases=0,
        total_test_cases=1,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    db.close()

    review_response = client.post(
        f"/api/student/ai/code-review/{submission.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert review_response.status_code == 200
    assert review_response.json()["status"] == "success"

    history_response = client.get(
        "/api/student/ai/usage-history",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert history_response.status_code == 200
    history_payload = history_response.json()
    assert len(history_payload["recent_requests"]) == 1
    logged = history_payload["recent_requests"][0]
    assert logged["task_type"] == "CODE_REVIEW"
    assert logged["status"] == "SUCCESS"


def test_non_student_cannot_access_ai_usage_history():
    response = client.post(
        "/api/auth/register",
        json={"full_name": "Admin", "email": "aiusage-admin@example.com", "password": "SecurePassword", "role": "ADMIN"},
    )
    assert response.status_code == 201
    token = response.json()["access_token"]

    response = client.get("/api/student/ai/usage-history", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
