import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    from app.core.database import engine
    from app.models.code_draft import CodeDraft
    from app.models.problem import Problem, TestCase
    from app.models.user import User

    Base = None
    try:
        from app.core.database import Base as CoreBase

        Base = CoreBase
    except Exception:
        Base = None

    if Base is not None:
        Base.metadata.drop_all(bind=engine, checkfirst=True)
        Base.metadata.create_all(bind=engine)
    else:
        User.__table__.drop(engine, checkfirst=True)
        User.__table__.create(engine, checkfirst=True)
        Problem.__table__.drop(engine, checkfirst=True)
        Problem.__table__.create(engine, checkfirst=True)
        TestCase.__table__.drop(engine, checkfirst=True)
        TestCase.__table__.create(engine, checkfirst=True)
        CodeDraft.__table__.drop(engine, checkfirst=True)
        CodeDraft.__table__.create(engine, checkfirst=True)


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


def test_student_can_list_active_problems():
    token = register_user("student@example.com")
    problem_payload = {
        "title": "Two Sum",
        "slug": "two-sum",
        "description": "Find a pair that sums to target.",
        "difficulty": "EASY",
        "topic": "ARRAYS",
        "constraints": "1 <= n <= 10^5",
        "input_format": "First line contains n",
        "output_format": "Return indices",
        "starter_code": {"python": "def solve():\n    pass"},
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
    }
    admin_token = register_user("admin@example.com", role="ADMIN")
    admin_response = client.post("/api/admin/problems", json=problem_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_response.status_code == 201

    response = client.get("/api/problems", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["slug"] == "two-sum"


def test_student_can_filter_by_difficulty_and_topic_and_search():
    token = register_user("student2@example.com")
    admin_token = register_user("admin2@example.com", role="ADMIN")
    problem_payloads = [
        {
            "title": "Balanced Symbols",
            "slug": "balanced-symbols",
            "description": "Check bracket balance.",
            "difficulty": "EASY",
            "topic": "STACKS",
            "constraints": "1 <= n <= 1000",
            "input_format": "String",
            "output_format": "Boolean",
            "starter_code": {"python": "def solve():\n    pass"},
            "time_limit_ms": 1000,
            "memory_limit_mb": 128,
        },
        {
            "title": "Shortest Route",
            "slug": "shortest-route",
            "description": "Find shortest route in graph.",
            "difficulty": "HARD",
            "topic": "GRAPHS",
            "constraints": "1 <= n <= 1000",
            "input_format": "Graph",
            "output_format": "Shortest path",
            "starter_code": {"python": "def solve():\n    pass"},
            "time_limit_ms": 1000,
            "memory_limit_mb": 256,
        },
    ]
    for payload in problem_payloads:
        response = client.post("/api/admin/problems", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 201

    difficulty_response = client.get("/api/problems?difficulty=EASY", headers={"Authorization": f"Bearer {token}"})
    assert difficulty_response.status_code == 200
    assert difficulty_response.json()["items"][0]["topic"] == "STACKS"

    topic_response = client.get("/api/problems?topic=GRAPHS", headers={"Authorization": f"Bearer {token}"})
    assert topic_response.status_code == 200
    assert topic_response.json()["items"][0]["slug"] == "shortest-route"

    search_response = client.get("/api/problems?search=balanced", headers={"Authorization": f"Bearer {token}"})
    assert search_response.status_code == 200
    assert search_response.json()["items"][0]["slug"] == "balanced-symbols"


def test_problem_detail_contains_sample_cases_only():
    token = register_user("student3@example.com")
    admin_token = register_user("admin3@example.com", role="ADMIN")
    problem_response = client.post(
        "/api/admin/problems",
        json={
            "title": "Unique Path",
            "slug": "unique-path",
            "description": "Count unique paths.",
            "difficulty": "MEDIUM",
            "topic": "TREES",
            "constraints": "1 <= n <= 100",
            "input_format": "Tree input",
            "output_format": "Path count",
            "starter_code": {"python": "def solve():\n    pass"},
            "time_limit_ms": 1000,
            "memory_limit_mb": 128,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    problem_id = problem_response.json()["id"]
    client.post(
        f"/api/admin/problems/{problem_id}/test-cases",
        json={
            "input_data": "5\n",
            "expected_output": "5\n",
            "explanation": "Sample case",
            "is_sample": True,
            "order_index": 1,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    client.post(
        f"/api/admin/problems/{problem_id}/test-cases",
        json={
            "input_data": "8\n",
            "expected_output": "8\n",
            "explanation": "Hidden case",
            "is_sample": False,
            "order_index": 2,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    response = client.get("/api/problems/unique-path", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["sample_test_cases"]) == 1
    assert payload["sample_test_cases"][0]["explanation"] == "Sample case"


def test_student_can_save_and_retrieve_own_draft_only():
    student_token = register_user("student4@example.com")
    other_student_token = register_user("student5@example.com")
    admin_token = register_user("admin4@example.com", role="ADMIN")
    problem_response = client.post(
        "/api/admin/problems",
        json={
            "title": "Queue Basics",
            "slug": "queue-basics",
            "description": "Use queue operations.",
            "difficulty": "EASY",
            "topic": "QUEUES",
            "constraints": "1 <= n <= 100",
            "input_format": "Queue input",
            "output_format": "Queue output",
            "starter_code": {"python": "def solve():\n    pass"},
            "time_limit_ms": 1000,
            "memory_limit_mb": 128,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    problem_id = problem_response.json()["id"]

    save_response = client.put(
        f"/api/problems/{problem_id}/draft",
        json={"language": "python", "code": "print('hello')"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert save_response.status_code == 200

    get_response = client.get(
        f"/api/problems/{problem_id}/draft?language=python",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert get_response.status_code == 200
    assert get_response.json()["code"] == "print('hello')"

    other_response = client.get(
        f"/api/problems/{problem_id}/draft?language=python",
        headers={"Authorization": f"Bearer {other_student_token}"},
    )
    assert other_response.status_code == 404


def test_non_admin_cannot_create_problem():
    student_token = register_user("student6@example.com")
    response = client.post(
        "/api/admin/problems",
        json={
            "title": "Forbidden Problem",
            "slug": "forbidden-problem",
            "description": "Should fail",
            "difficulty": "EASY",
            "topic": "ARRAYS",
            "constraints": "1",
            "input_format": "None",
            "output_format": "None",
            "starter_code": {"python": "pass"},
            "time_limit_ms": 1000,
            "memory_limit_mb": 128,
        },
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 403


def test_admin_can_create_problem_and_add_test_cases():
    admin_token = register_user("admin5@example.com", role="ADMIN")
    create_response = client.post(
        "/api/admin/problems",
        json={
            "title": "Graph Traversal",
            "slug": "graph-traversal",
            "description": "Traverse graph structure",
            "difficulty": "MEDIUM",
            "topic": "GRAPHS",
            "constraints": "1 <= n <= 100",
            "input_format": "Graph data",
            "output_format": "Traversal output",
            "starter_code": {"python": "def solve():\n    pass"},
            "time_limit_ms": 1000,
            "memory_limit_mb": 256,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert create_response.status_code == 201
    problem_id = create_response.json()["id"]

    sample_response = client.post(
        f"/api/admin/problems/{problem_id}/test-cases",
        json={
            "input_data": "1\n",
            "expected_output": "1\n",
            "explanation": "Sample explanation",
            "is_sample": True,
            "order_index": 1,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert sample_response.status_code == 201

    hidden_response = client.post(
        f"/api/admin/problems/{problem_id}/test-cases",
        json={
            "input_data": "2\n",
            "expected_output": "2\n",
            "explanation": "Hidden explanation",
            "is_sample": False,
            "order_index": 2,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert hidden_response.status_code == 201
