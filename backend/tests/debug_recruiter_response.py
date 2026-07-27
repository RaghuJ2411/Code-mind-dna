from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

register_response = client.post(
    '/api/auth/register',
    json={
        'full_name': 'Recruiter',
        'email': f'recruiter-test-{uuid.uuid4().hex[:8]}@example.com',
        'password': 'SecurePassword',
        'role': 'RECRUITER',
    },
)
print('register', register_response.status_code, register_response.json())

token = register_response.json()['access_token']

create_response = client.post(
    '/api/recruiter/jobs',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'title': 'Test Job',
        'company': 'Test Co',
        'location': 'Remote',
        'seniority_level': 'MID',
        'description': 'Test',
        'requirements': ['Python'],
        'is_active': True,
    },
)
print('create', create_response.status_code, create_response.json())

dashboard_response = client.get(
    '/api/recruiter/dashboard',
    headers={'Authorization': f'Bearer {token}'},
)
print('dashboard', dashboard_response.status_code, dashboard_response.json())
