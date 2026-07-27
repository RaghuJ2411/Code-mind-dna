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


def test_recruiter_can_create_and_list_job_postings():
    recruiter_token = create_user(f"recruiter-{uuid.uuid4().hex[:8]}@example.com", "RECRUITER")

    job_payload = {
        "title": "Junior Backend Developer",
        "company": "CodeMind Labs",
        "location": "Remote",
        "seniority_level": "ENTRY",
        "description": "Build APIs and collaborate with mentors to ship backend features.",
        "requirements": ["Python", "APIs", "SQL"],
        "is_active": True,
    }

    create_response = client.post(
        "/api/recruiter/jobs",
        headers={"Authorization": f"Bearer {recruiter_token}"},
        json=job_payload,
    )
    assert create_response.status_code == 201
    job = create_response.json()
    assert job["title"] == job_payload["title"]
    assert job["company"] == job_payload["company"]
    assert job["requirements"] == job_payload["requirements"]

    list_response = client.get(
        "/api/recruiter/jobs",
        headers={"Authorization": f"Bearer {recruiter_token}"},
    )
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["title"] == job_payload["title"]


def test_recruiter_can_view_job_detail():
    recruiter_token = create_user(f"recruiter-job-detail-{uuid.uuid4().hex[:8]}@example.com", "RECRUITER")

    payload = {
        "title": "Interview Coach",
        "company": "MatchHire",
        "location": "Remote",
        "seniority_level": "MID",
        "description": "Support candidate interviews and prepare screening packets.",
        "requirements": ["Communication", "Interview prep"],
        "is_active": True,
    }

    create_response = client.post(
        "/api/recruiter/jobs",
        headers={"Authorization": f"Bearer {recruiter_token}"},
        json=payload,
    )
    assert create_response.status_code == 201
    job_id = create_response.json()["id"]

    detail_response = client.get(
        f"/api/recruiter/jobs/{job_id}",
        headers={"Authorization": f"Bearer {recruiter_token}"},
    )
    assert detail_response.status_code == 200
    job = detail_response.json()
    assert job["id"] == job_id
    assert job["company"] == payload["company"]


def test_recruiter_dashboard_shows_open_jobs_and_candidates():
    recruiter_token = create_user(f"recruiter-dashboard-{uuid.uuid4().hex[:8]}@example.com", "RECRUITER")
    create_user(f"student-dashboard-1-{uuid.uuid4().hex[:8]}@example.com", "STUDENT")
    create_user(f"student-dashboard-2-{uuid.uuid4().hex[:8]}@example.com", "STUDENT")

    job_payload = {
        "title": "Talent Acquisition Specialist",
        "company": "TalentFlow",
        "location": "Hybrid",
        "seniority_level": "MID",
        "description": "Source candidate profiles and manage recruiter workflows.",
        "requirements": ["Communication", "ATS", "Networking"],
        "is_active": True,
    }

    client.post(
        "/api/recruiter/jobs",
        headers={"Authorization": f"Bearer {recruiter_token}"},
        json=job_payload,
    )

    dashboard_response = client.get(
        "/api/recruiter/dashboard",
        headers={"Authorization": f"Bearer {recruiter_token}"},
    )
    assert dashboard_response.status_code == 200
    payload = dashboard_response.json()
    assert payload["total_open_jobs"] == 1
    assert payload["total_candidates"] >= 2
    assert payload["top_open_job"] is not None
    assert payload["top_open_job"]["title"] == job_payload["title"]
    assert isinstance(payload["recent_jobs"], list)
    assert isinstance(payload["recent_candidates"], list)


def test_recruiter_dashboard_returns_best_fit_candidate():
    recruiter_token = create_user(f"recruiter-best-fit-{uuid.uuid4().hex[:8]}@example.com", "RECRUITER")
    create_user(f"student-best-fit-1-{uuid.uuid4().hex[:8]}@example.com", "STUDENT")
    create_user(f"student-best-fit-2-{uuid.uuid4().hex[:8]}@example.com", "STUDENT")

    dashboard_response = client.get(
        "/api/recruiter/dashboard",
        headers={"Authorization": f"Bearer {recruiter_token}"},
    )
    assert dashboard_response.status_code == 200
    payload = dashboard_response.json()
    assert payload["best_fit_candidate"] is not None
    assert payload["best_fit_candidate"]["fit_score"] >= 0
    assert payload["best_fit_candidate"]["is_best_fit"] is True


def test_non_recruiter_cannot_access_recruiter_endpoints():
    student_token = create_user(f"student-recruiter-{uuid.uuid4().hex[:8]}@example.com", "STUDENT")

    response = client.get("/api/recruiter/dashboard", headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 403

    response = client.post(
        "/api/recruiter/jobs",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "title": "Unauthorized Job",
            "company": "Invalid",
            "location": "Nowhere",
            "seniority_level": "ENTRY",
            "description": "Should not be created.",
            "requirements": [],
            "is_active": True,
        },
    )
    assert response.status_code == 403


def test_recruiter_can_filter_jobs_by_search_and_status():
    recruiter_token = create_user(f"recruiter-job-filter-{uuid.uuid4().hex[:8]}@example.com", "RECRUITER")

    client.post(
        "/api/recruiter/jobs",
        headers={"Authorization": f"Bearer {recruiter_token}"},
        json={
            "title": "Backend Engineer",
            "company": "CodeMind Labs",
            "location": "Remote",
            "seniority_level": "MID",
            "description": "Build APIs for recruiter workflows.",
            "requirements": ["Python", "APIs"],
            "is_active": True,
        },
    )
    client.post(
        "/api/recruiter/jobs",
        headers={"Authorization": f"Bearer {recruiter_token}"},
        json={
            "title": "Senior Recruiter",
            "company": "TalentFlow",
            "location": "Hybrid",
            "seniority_level": "SENIOR",
            "description": "Manage hiring campaigns.",
            "requirements": ["Communication", "ATS"],
            "is_active": False,
        },
    )

    response = client.get(
        "/api/recruiter/jobs?query=Backend&active_only=true",
        headers={"Authorization": f"Bearer {recruiter_token}"},
    )
    assert response.status_code == 200
    jobs = response.json()
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Backend Engineer"

    response = client.get(
        "/api/recruiter/jobs?location=Hybrid&company=TalentFlow&active_only=false",
        headers={"Authorization": f"Bearer {recruiter_token}"},
    )
    assert response.status_code == 200
    jobs = response.json()
    assert len(jobs) == 1
    assert jobs[0]["company"] == "TalentFlow"

    response = client.get(
        "/api/recruiter/jobs?seniority_level=SENIOR&active_only=false",
        headers={"Authorization": f"Bearer {recruiter_token}"},
    )
    assert response.status_code == 200
    jobs = response.json()
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Senior Recruiter"


def test_recruiter_can_search_candidates_by_name_and_email():
    recruiter_token = create_user(f"recruiter-candidate-search-{uuid.uuid4().hex[:8]}@example.com", "RECRUITER")
    student1_email = f"candidate-search-1-{uuid.uuid4().hex[:8]}@example.com"
    student2_email = f"candidate-search-2-{uuid.uuid4().hex[:8]}@example.com"

    create_user(student1_email, "STUDENT")
    create_user(student2_email, "STUDENT")

    response = client.get(
        f"/api/recruiter/candidates?query={student1_email.split('@')[0]}",
        headers={"Authorization": f"Bearer {recruiter_token}"},
    )
    assert response.status_code == 200
    candidates = response.json()
    assert len(candidates) >= 1
    assert any(student1_email == candidate["email"] for candidate in candidates)

    response = client.get(
        "/api/recruiter/candidates?query=User",
        headers={"Authorization": f"Bearer {recruiter_token}"},
    )
    assert response.status_code == 200
    candidates = response.json()
    assert len(candidates) >= 2
    assert all("fit_score" in candidate for candidate in candidates)
    assert any(candidate.get("is_best_fit") for candidate in candidates)


def test_recruiter_can_view_candidate_profile_with_intelligence():
    recruiter_token = create_user(f"recruiter-candidate-detail-{uuid.uuid4().hex[:8]}@example.com", "RECRUITER")
    student_email = f"candidate-intel-{uuid.uuid4().hex[:8]}@example.com"
    student_token = create_user(student_email, "STUDENT")
    student_id = get_user_id(student_token)

    response = client.get(
        f"/api/recruiter/candidates/{student_id}",
        headers={"Authorization": f"Bearer {recruiter_token}"},
    )
    assert response.status_code == 200
    candidate = response.json()
    assert candidate["id"] == student_id
    assert candidate["full_name"].startswith("Student User")
    assert candidate["email"] == student_email
    assert candidate["profile_status"] in {"AVAILABLE", "NOT_GENERATED"}
    assert "readiness_score" in candidate
    assert "top_roles" in candidate
    assert "evidence_highlights" in candidate
    assert isinstance(candidate["evidence_highlights"], list)
    assert candidate["signal_summary"]


def test_recruiter_dashboard_includes_open_job_counts_by_seniority():
    recruiter_token = create_user(f"recruiter-dashboard-counts-{uuid.uuid4().hex[:8]}@example.com", "RECRUITER")

    client.post(
        "/api/recruiter/jobs",
        headers={"Authorization": f"Bearer {recruiter_token}"},
        json={
            "title": "Entry Level Special",
            "company": "EntryCo",
            "location": "Remote",
            "seniority_level": "ENTRY",
            "description": "A beginning role.",
            "requirements": ["Learning", "Teamwork"],
            "is_active": True,
        },
    )

    client.post(
        "/api/recruiter/jobs",
        headers={"Authorization": f"Bearer {recruiter_token}"},
        json={
            "title": "Senior Strategy Lead",
            "company": "LeadCo",
            "location": "Onsite",
            "seniority_level": "SENIOR",
            "description": "A senior leadership role.",
            "requirements": ["Leadership", "Strategy"],
            "is_active": True,
        },
    )

    dashboard_response = client.get(
        "/api/recruiter/dashboard",
        headers={"Authorization": f"Bearer {recruiter_token}"},
    )
    assert dashboard_response.status_code == 200
    payload = dashboard_response.json()
    assert payload["job_counts_by_seniority"]["ENTRY"] == 1
    assert payload["job_counts_by_seniority"]["SENIOR"] == 1
