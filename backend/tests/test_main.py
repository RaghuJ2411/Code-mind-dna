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


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_live_endpoint():
    response = client.get("/api/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "live"


def test_health_ready_endpoint():
    response = client.get("/api/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_register_user():
    response = client.post(
        "/api/auth/register",
        json={"full_name": "Example User", "email": "user@example.com", "password": "SecurePassword", "role": "STUDENT"},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["user"]["email"] == "user@example.com"


def test_duplicate_email_rejected():
    client.post(
        "/api/auth/register",
        json={"full_name": "Example", "email": "dup@example.com", "password": "SecurePassword", "role": "STUDENT"},
    )
    response = client.post(
        "/api/auth/register",
        json={"full_name": "Example", "email": "dup@example.com", "password": "SecurePassword", "role": "STUDENT"},
    )
    assert response.status_code == 409


def test_login_success():
    client.post(
        "/api/auth/register",
        json={"full_name": "Example", "email": "login@example.com", "password": "SecurePassword", "role": "STUDENT"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "SecurePassword"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_invalid_password():
    client.post(
        "/api/auth/register",
        json={"full_name": "Example", "email": "invalid@example.com", "password": "SecurePassword", "role": "STUDENT"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "invalid@example.com", "password": "WrongPassword"},
    )
    assert response.status_code == 401


def test_protected_route_without_token():
    response = client.get("/api/student/dashboard")
    assert response.status_code == 401


def test_student_route_with_student_token():
    register_response = client.post(
        "/api/auth/register",
        json={"full_name": "Student", "email": "student@example.com", "password": "SecurePassword", "role": "STUDENT"},
    )
    token = register_response.json()["access_token"]
    response = client.get("/api/student/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_student_attempting_admin_route():
    register_response = client.post(
        "/api/auth/register",
        json={"full_name": "Student", "email": "student2@example.com", "password": "SecurePassword", "role": "STUDENT"},
    )
    token = register_response.json()["access_token"]
    response = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_admin_route_with_admin_token():
    token = register_user("admin@example.com", role="ADMIN")
    response = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_admin_dashboard_and_user_listing():
    admin_token = register_user("admin2@example.com", role="ADMIN")
    student_token = register_user("student@example.com", role="STUDENT")

    dashboard_response = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {admin_token}"})
    assert dashboard_response.status_code == 200
    dashboard_data = dashboard_response.json()
    assert dashboard_data["total_users"] >= 2
    assert dashboard_data["role_counts"]["ADMIN"] >= 1

    users_response = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"search": "student@example.com", "page": 1, "page_size": 10},
    )
    assert users_response.status_code == 200
    users_data = users_response.json()
    assert any(user["email"] == "student@example.com" for user in users_data["items"])

    student_user = next(user for user in users_data["items"] if user["email"] == "student@example.com")
    update_response = client.put(
        f"/api/admin/users/{student_user['id']}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["is_active"] is False

    audit_response = client.get(
        "/api/admin/audit-logs",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"page": 1, "page_size": 20},
    )
    assert audit_response.status_code == 200
    audit_data = audit_response.json()
    assert audit_data["total"] >= 1
    assert any(entry["path"] == "/api/admin/dashboard" for entry in audit_data["items"])


def test_admin_cannot_deactivate_self_and_role_filtering():
    admin_token = register_user("admin3@example.com", role="ADMIN")
    student_token = register_user("student2@example.com", role="STUDENT")

    # Ensure student appears in list and can be filtered by role
    users_response = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"role": "STUDENT", "page": 1, "page_size": 10},
    )
    assert users_response.status_code == 200
    users_data = users_response.json()
    assert users_data["page"] == 1
    assert users_data["total_pages"] >= 1
    assert any(user["email"] == "student2@example.com" for user in users_data["items"])

    student_user = next(user for user in users_data["items"] if user["email"] == "student2@example.com")
    update_response = client.put(
        f"/api/admin/users/{student_user['id']}",
        json={"role": "MENTOR"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["role"] == "MENTOR"

    # Admin cannot deactivate their own account
    admin_user_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_user_response.status_code == 200
    admin_user = admin_user_response.json()

    self_deactivate_response = client.put(
        f"/api/admin/users/{admin_user['id']}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert self_deactivate_response.status_code == 400
    assert self_deactivate_response.json()["detail"] == "Cannot deactivate own account"


def test_audit_log_filters_and_pagination():
    admin_token = register_user("admin4@example.com", role="ADMIN")
    client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    audit_response = client.get(
        "/api/admin/audit-logs",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"page": 1, "page_size": 5, "path": "/api/admin/dashboard"},
    )
    assert audit_response.status_code == 200
    audit_data = audit_response.json()
    assert audit_data["page"] == 1
    assert audit_data["page_size"] == 5
    assert audit_data["total"] >= 1
    assert all(entry["path"].startswith("/api/admin/dashboard") for entry in audit_data["items"])
