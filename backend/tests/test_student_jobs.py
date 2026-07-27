import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db_tables():
    from app.core.database import Base, engine

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def register_user(email: str, role: str = "STUDENT") -> str:
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": email.split("@")[0].title(),
            "email": email,
            "password": "SecurePassword",
            "role": role,
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def test_student_can_list_jobs_and_apply():
    # Register a recruiter to create a job posting first
    recruiter_token = register_user("recruiter@example.com", role="RECRUITER")

    # Create a job posting
    job_create_response = client.post(
        "/api/recruiter/jobs",
        json={
            "title": "Software Engineer",
            "description": "Test job description",
            "company": "Test Corp",
            "location": "Remote",
            "seniority_level": "MID",
        },
        headers={"Authorization": f"Bearer {recruiter_token}"},
    )
    assert job_create_response.status_code == 201

    # Register the student user
    student_token = register_user("student@example.com", role="STUDENT")

    jobs_response = client.get('/api/student/jobs', headers={'Authorization': f'Bearer {student_token}'})
    assert jobs_response.status_code == 200
    jobs = jobs_response.json()
    assert isinstance(jobs, list)

    if jobs:
        job_id = jobs[0]['id']
        apply_response = client.post(
            f'/api/student/jobs/{job_id}/apply',
            headers={'Authorization': f'Bearer {student_token}'},
        )
        assert apply_response.status_code == 201
        assert apply_response.json()['job_id'] == job_id

        applications_response = client.get('/api/student/applications', headers={'Authorization': f'Bearer {student_token}'})
        assert applications_response.status_code == 200
        assert any(item['job_id'] == job_id for item in applications_response.json())

