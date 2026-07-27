import pytest
from app.services.ai.provider_factory import get_provider
from app.services.ai.code_review_service import CodeReviewService
from app.models.user import User, UserRole
from app.models.problem import Problem
from app.models.execution import Submission


def test_provider_factory_returns_mock_by_default():
    p = get_provider()
    assert p is not None


def test_code_review_requires_ownership(db):
    # create a user and a submission owned by someone else
    user1 = User(full_name="A", email="a@example.com", password_hash="x", role=UserRole.STUDENT)
    user2 = User(full_name="B", email="b@example.com", password_hash="x", role=UserRole.STUDENT)
    db.add_all([user1, user2])
    db.commit()

    prob = Problem(title="P", slug="p", description="d", difficulty="EASY", topic="ARRAYS", constraints="-", input_format="-", output_format="-", created_by=user1.id)
    db.add(prob)
    db.commit()

    sub = Submission(student_id=user2.id, problem_id=prob.id, language='python', source_code='print(1)', verdict='WRONG_ANSWER', passed_test_cases=0, total_test_cases=1)
    db.add(sub)
    db.commit()

    service = CodeReviewService(db, user1)
    with pytest.raises(PermissionError):
        service.generate_review(sub.id)


def test_code_review_generates_and_persists(db):
    user = User(full_name="A", email="a2@example.com", password_hash="x", role=UserRole.STUDENT)
    db.add(user)
    db.commit()

    prob = Problem(title="P2", slug="p2", description="d2", difficulty="EASY", topic="ARRAYS", constraints="-", input_format="-", output_format="-", created_by=user.id)
    db.add(prob)
    db.commit()

    sub = Submission(student_id=user.id, problem_id=prob.id, language='python', source_code='print(2)', verdict='WRONG_ANSWER', passed_test_cases=0, total_test_cases=1)
    db.add(sub)
    db.commit()

    service = CodeReviewService(db, user)
    result = service.generate_review(sub.id)
    assert 'summary' in result
