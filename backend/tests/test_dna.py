import os
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.execution import Submission, SubmissionVerdict
from app.models.problem import Problem, DifficultyLevel, TopicType
from app.models.user import User

client = TestClient(app)


def register_and_login(email: str, role: str) -> str:
    from app.main import app

    client = TestClient(app)
    response = client.post(
        "/api/auth/register",
        json={"full_name": "DNA Student", "email": email, "password": "SecurePassword", "role": role},
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def test_dna_profile_recalculate_and_history():
    token = register_and_login("dna-student@example.com", "STUDENT")

    # Create a problem and a submission for the student.
    from app.core.database import engine
    from sqlalchemy.orm import Session, sessionmaker

    TestingSessionLocal = sessionmaker(bind=engine)
    with TestingSessionLocal() as db:
        student = db.query(User).filter(User.email == "dna-student@example.com").first()
        assert student is not None

        problem = Problem(
            title="DNA Problem",
            slug="dna-problem",
            description="A test problem for DNA profile",
            difficulty=DifficultyLevel.MEDIUM,
            topic=TopicType.ARRAYS,
            constraints="None",
            input_format="None",
            output_format="None",
            time_limit_ms=1000,
            memory_limit_mb=128,
            created_by=student.id,
        )
        db.add(problem)
        db.commit()
        db.refresh(problem)

        submission = Submission(
            student_id=student.id,
            problem_id=problem.id,
            language="python",
            source_code="pass",
            verdict=SubmissionVerdict.ACCEPTED,
            passed_test_cases=5,
            total_test_cases=5,
            runtime_ms=120,
            memory_kb=2048,
            attempt_number=1,
        )
        db.add(submission)
        db.commit()

    recalc_response = client.post(
        "/api/dna/profile/recalculate",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert recalc_response.status_code == 200
    assert recalc_response.json()["success"] is True

    profile_response = client.get(
        "/api/dna/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert profile_response.status_code == 200
    data = profile_response.json()
    assert data["profile_status"] == "AVAILABLE"
    assert data["overall_score"] is not None
    assert len(data["dimensions"]) == 6

    history_response = client.get(
        "/api/dna/profile/history",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert history_response.status_code == 200
    history_data = history_response.json()
    assert history_data["total"] == 1
    assert history_data["data"][0]["scoring_version"] == "1.0"


def test_dna_profile_dimension_explanation():
    token = register_and_login("dna-student2@example.com", "STUDENT")

    from app.core.database import engine
    from sqlalchemy.orm import Session, sessionmaker

    TestingSessionLocal = sessionmaker(bind=engine)
    with TestingSessionLocal() as db:
        student = db.query(User).filter(User.email == "dna-student2@example.com").first()
        problem = Problem(
            title="DNA Explanation Problem",
            slug="dna-explanation-problem",
            description="Another test problem",
            difficulty=DifficultyLevel.EASY,
            topic=TopicType.STRINGS,
            constraints="None",
            input_format="None",
            output_format="None",
            time_limit_ms=1000,
            memory_limit_mb=128,
            created_by=student.id,
        )
        db.add(problem)
        db.commit()
        db.refresh(problem)

        submission = Submission(
            student_id=student.id,
            problem_id=problem.id,
            language="python",
            source_code="pass",
            verdict=SubmissionVerdict.ACCEPTED,
            passed_test_cases=5,
            total_test_cases=5,
            runtime_ms=90,
            memory_kb=1024,
            attempt_number=1,
        )
        db.add(submission)
        db.commit()

    client.post(
        "/api/dna/profile/recalculate",
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        "/api/dna/profile/dimension/LOGIC",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["dimension"] == "LOGIC"
    assert isinstance(payload["explanation"], str)
    assert payload["contributions"] == []
