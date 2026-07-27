import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.execution_service import ExecutionService

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    from app.core.database import Base, engine

    Base.metadata.drop_all(bind=engine, checkfirst=True)
    Base.metadata.create_all(bind=engine)


def register_user(email: str, role: str = "STUDENT"):
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


def create_problem(admin_token: str, slug: str = "sum-problem"):
    response = client.post(
        "/api/admin/problems",
        json={
            "title": "Sum Problem",
            "slug": slug,
            "description": "Return the sum of input numbers.",
            "difficulty": "EASY",
            "topic": "ARRAYS",
            "constraints": "1 <= n <= 1000",
            "input_format": "Input contains numbers",
            "output_format": "Output sum",
            "starter_code": {"python": "def solve():\n    pass"},
            "time_limit_ms": 1000,
            "memory_limit_mb": 256,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def add_test_case(problem_id: int, admin_token: str, *, is_sample: bool, order_index: int, input_data: str, expected_output: str):
    response = client.post(
        f"/api/admin/problems/{problem_id}/test-cases",
        json={
            "input_data": input_data,
            "expected_output": expected_output,
            "explanation": "example" if is_sample else "hidden",
            "is_sample": is_sample,
            "order_index": order_index,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    return response.json()


def test_run_endpoint_requires_authentication():
    response = client.post(
        "/api/execution/run",
        json={"problem_id": 1, "language": "python", "source_code": "print(1)"},
    )
    assert response.status_code == 401


def test_run_endpoint_requires_student_role():
    admin_token = register_user("admin@example.com", role="ADMIN")
    response = client.post(
        "/api/execution/run",
        json={"problem_id": 1, "language": "python", "source_code": "print(1)"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 403


def test_unsupported_language_is_rejected():
    student_token = register_user("student@example.com")
    admin_token = register_user("admin2@example.com", role="ADMIN")
    problem_id = create_problem(admin_token)
    add_test_case(problem_id, admin_token, is_sample=True, order_index=1, input_data="1\n", expected_output="1\n")

    response = client.post(
        "/api/execution/run",
        json={"problem_id": problem_id, "language": "c++", "source_code": "print(1)"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 422


def test_run_uses_sample_tests_and_does_not_create_submission(monkeypatch):
    student_token = register_user("student2@example.com")
    admin_token = register_user("admin3@example.com", role="ADMIN")
    problem_id = create_problem(admin_token)
    add_test_case(problem_id, admin_token, is_sample=True, order_index=1, input_data="1\n", expected_output="1\n")
    add_test_case(problem_id, admin_token, is_sample=False, order_index=2, input_data="2\n", expected_output="2\n")

    def fake_execute_code(self, source_code, language, stdin, time_limit_ms, memory_limit_mb):
        return {
            "status": "SUCCESS",
            "stdout": "1\n" if stdin == "1\n" else "2\n",
            "stderr": "",
            "compile_output": "",
            "runtime_ms": 10,
            "memory_kb": 1000,
            "exit_code": 0,
        }

    monkeypatch.setattr(ExecutionService, "_execute_with_provider", fake_execute_code)

    response = client.post(
        "/api/execution/run",
        json={"problem_id": problem_id, "language": "python", "source_code": "print(1)"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["passed"] == 1
    assert payload["total"] == 1
    assert payload["results"][0]["passed"] is True

    submissions = client.get("/api/submissions/me", headers={"Authorization": f"Bearer {student_token}"})
    assert submissions.status_code == 200
    assert submissions.json()["items"] == []


def test_submit_creates_submission_and_increments_attempt(monkeypatch):
    student_token = register_user("student3@example.com")
    admin_token = register_user("admin4@example.com", role="ADMIN")
    problem_id = create_problem(admin_token)
    add_test_case(problem_id, admin_token, is_sample=False, order_index=1, input_data="1\n", expected_output="1\n")

    def fake_execute_code(self, source_code, language, stdin, time_limit_ms, memory_limit_mb):
        return {
            "status": "SUCCESS",
            "stdout": "1\n",
            "stderr": "",
            "compile_output": "",
            "runtime_ms": 12,
            "memory_kb": 1200,
            "exit_code": 0,
        }

    monkeypatch.setattr(ExecutionService, "_execute_with_provider", fake_execute_code)

    response = client.post(
        "/api/execution/submit",
        json={"problem_id": problem_id, "language": "python", "source_code": "print(1)"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["verdict"] == "ACCEPTED"
    assert payload["attempt_number"] == 1

    second_response = client.post(
        "/api/execution/submit",
        json={"problem_id": problem_id, "language": "python", "source_code": "print(1)"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert second_response.status_code == 200
    assert second_response.json()["attempt_number"] == 2


def test_submission_history_and_problem_status(monkeypatch):
    student_token = register_user("student4@example.com")
    admin_token = register_user("admin5@example.com", role="ADMIN")
    problem_id = create_problem(admin_token, slug="status-problem")
    add_test_case(problem_id, admin_token, is_sample=False, order_index=1, input_data="1\n", expected_output="1\n")

    def fake_execute_code(self, source_code, language, stdin, time_limit_ms, memory_limit_mb):
        return {
            "status": "SUCCESS",
            "stdout": "1\n",
            "stderr": "",
            "compile_output": "",
            "runtime_ms": 20,
            "memory_kb": 1300,
            "exit_code": 0,
        }

    monkeypatch.setattr(ExecutionService, "_execute_with_provider", fake_execute_code)

    client.post(
        "/api/execution/submit",
        json={"problem_id": problem_id, "language": "python", "source_code": "print(1)"},
        headers={"Authorization": f"Bearer {student_token}"},
    )

    history = client.get("/api/submissions/me", headers={"Authorization": f"Bearer {student_token}"})
    assert history.status_code == 200
    assert history.json()["items"][0]["problem_id"] == problem_id

    problem_list = client.get("/api/problems", headers={"Authorization": f"Bearer {student_token}"})
    assert problem_list.status_code == 200
    problem_item = problem_list.json()["items"][0]
    assert problem_item["status"] == "SOLVED"
    assert problem_item["attempt_count"] == 1
