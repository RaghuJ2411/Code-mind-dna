from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User
from app.models.execution import Submission, SubmissionVerdict
from app.models.problem import Problem, DifficultyLevel, TopicType

client = TestClient(app)


def test_student_dashboard_overview_unauthorized():
    response = client.get('/api/student/dashboard/overview')
    assert response.status_code == 401
