"""Comprehensive tests for analytics services."""

import pytest
from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.models.execution import Submission, SubmissionVerdict, CodingSession
from app.models.problem import Problem, DifficultyLevel, TopicType
from app.models.user import User, UserRole
from app.models.analytics import StudentDailyAnalytics, StudentWeeklyAnalytics
from app.services.analytics import (
    BehaviorFeatureService,
    AggregationService,
    DataQualityService,
)


@pytest.fixture
def admin_user(db: Session) -> User:
    """Create a test admin user for creating problems."""
    admin = User(
        email="admin@test.com",
        full_name="Admin User",
        password_hash="hashed",
        role=UserRole.ADMIN,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def student_user(db: Session) -> User:
    """Create a test student."""
    student = User(
        email="student@test.com",
        full_name="Test Student",
        password_hash="hashed",
        role=UserRole.STUDENT,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@pytest.fixture
def sample_problems(db: Session, admin_user: User) -> list[Problem]:
    """Create test problems with different difficulties."""
    problems_data = [
        ("Easy Problem", "easy-problem", DifficultyLevel.EASY, TopicType.ARRAYS),
        ("Medium Problem", "medium-problem", DifficultyLevel.MEDIUM, TopicType.STRINGS),
        ("Hard Problem", "hard-problem", DifficultyLevel.HARD, TopicType.GRAPHS),
    ]

    problems = []
    for title, slug, difficulty, topic in problems_data:
        problem = Problem(
            title=title,
            slug=slug,
            description="Test problem",
            difficulty=difficulty,
            topic=topic,
            constraints="Test",
            input_format="Test",
            output_format="Test",
            time_limit_ms=5000,
            memory_limit_mb=256,
            created_by=admin_user.id,
        )
        db.add(problem)
        db.commit()
        db.refresh(problem)
        problems.append(problem)

    return problems


class TestBehaviorFeatureService:
    """Test behavior feature extraction."""

    def test_activity_metrics_empty(self, db: Session, student_user: User):
        """Test activity metrics for student with no submissions."""
        service = BehaviorFeatureService(db)
        metrics = service.calculate_activity_metrics(student_user.id)

        assert metrics["problems_attempted"] == 0
        assert metrics["problems_solved"] == 0
        assert metrics["total_submissions"] == 0

    def test_activity_metrics_with_data(self, db: Session, student_user: User, sample_problems: list[Problem]):
        """Test activity metrics with submissions."""
        # Create submissions
        for problem in sample_problems[:2]:
            submission = Submission(
                student_id=student_user.id,
                problem_id=problem.id,
                language="python",
                source_code="pass",
                verdict=SubmissionVerdict.ACCEPTED,
                passed_test_cases=10,
                total_test_cases=10,
                runtime_ms=100,
                memory_kb=1024,
                attempt_number=1,
            )
            db.add(submission)
        db.commit()

        service = BehaviorFeatureService(db)
        metrics = service.calculate_activity_metrics(student_user.id)

        assert metrics["problems_attempted"] == 2
        assert metrics["problems_solved"] == 2

    def test_success_metrics_solve_rate(self, db: Session, student_user: User, sample_problems: list[Problem]):
        """Test solve rate calculation."""
        # 2 solved, 1 not solved
        for i, problem in enumerate(sample_problems):
            verdict = SubmissionVerdict.ACCEPTED if i < 2 else SubmissionVerdict.WRONG_ANSWER
            submission = Submission(
                student_id=student_user.id,
                problem_id=problem.id,
                language="python",
                source_code="pass",
                verdict=verdict,
                passed_test_cases=10 if verdict == SubmissionVerdict.ACCEPTED else 0,
                total_test_cases=10,
                runtime_ms=100,
                memory_kb=1024,
                attempt_number=1,
            )
            db.add(submission)
        db.commit()

        service = BehaviorFeatureService(db)
        metrics = service.calculate_success_metrics(student_user.id)

        assert pytest.approx(metrics["solve_rate"], abs=0.01) == 2 / 3

    def test_difficulty_metrics(self, db: Session, student_user: User, sample_problems: list[Problem]):
        """Test difficulty-level metrics."""
        for problem in sample_problems:
            submission = Submission(
                student_id=student_user.id,
                problem_id=problem.id,
                language="python",
                source_code="pass",
                verdict=SubmissionVerdict.ACCEPTED,
                passed_test_cases=10,
                total_test_cases=10,
                runtime_ms=100,
                memory_kb=1024,
                attempt_number=1,
            )
            db.add(submission)
        db.commit()

        service = BehaviorFeatureService(db)
        metrics = service.calculate_difficulty_metrics(student_user.id)

        assert metrics["easy"]["attempted"] == 1
        assert metrics["easy"]["solved"] == 1
        assert metrics["medium"]["attempted"] == 1
        assert metrics["hard"]["attempted"] == 1

    def test_behavior_profile_no_data(self, db: Session, student_user: User):
        """Test behavior profile with no data."""
        service = BehaviorFeatureService(db)
        profile = service.build_behavior_profile(student_user.id)
        assert profile["evidence_status"] == "NO_DATA"


class TestAggregationService:
    """Test analytics aggregation."""

    def test_daily_aggregation_empty(self, db: Session, student_user: User):
        """Test daily aggregation with no submissions."""
        service = AggregationService(db)
        today = date.today()
        daily = service.aggregate_daily_analytics(student_user.id, today)

        assert daily.student_id == student_user.id
        assert daily.analytics_date == today
        assert daily.problems_attempted == 0

    def test_daily_aggregation_idempotent(self, db: Session, student_user: User, sample_problems: list[Problem]):
        """Test that daily aggregation is idempotent."""
        # Add a submission
        submission = Submission(
            student_id=student_user.id,
            problem_id=sample_problems[0].id,
            language="python",
            source_code="pass",
            verdict=SubmissionVerdict.ACCEPTED,
            passed_test_cases=10,
            total_test_cases=10,
            runtime_ms=100,
            memory_kb=1024,
            attempt_number=1,
        )
        db.add(submission)
        db.commit()

        service = AggregationService(db)
        today = date.today()

        # First aggregation
        daily1 = service.aggregate_daily_analytics(student_user.id, today)
        daily1_id = daily1.id

        # Second aggregation (should update, not create new)
        daily2 = service.aggregate_daily_analytics(student_user.id, today)
        daily2_id = daily2.id

        assert daily1_id == daily2_id  # Same record


class TestDataQualityService:
    """Test data quality validation."""

    def test_validate_daily_valid(self, db: Session, student_user: User):
        """Test validation of valid daily record."""
        daily = StudentDailyAnalytics(
            student_id=student_user.id,
            analytics_date=date.today(),
            problems_attempted=2,
            problems_solved=1,
            submissions_count=5,
            runs_count=5,
            active_minutes=60,
            wrong_answer_count=2,
            compilation_error_count=1,
            runtime_error_count=0,
            time_limit_count=0,
            easy_attempted=1,
            easy_solved=1,
            medium_attempted=1,
            medium_solved=0,
            hard_attempted=0,
            hard_solved=0,
            unique_topics_attempted=2,
        )
        db.add(daily)
        db.commit()

        service = DataQualityService(db)
        result = service.validate_daily_analytics(daily)

        assert result["valid"] is True

    def test_validate_daily_invalid(self, db: Session, student_user: User):
        """Test validation fails when solved > attempted."""
        daily = StudentDailyAnalytics(
            student_id=student_user.id,
            analytics_date=date.today(),
            problems_attempted=1,
            problems_solved=3,  # Invalid
            submissions_count=5,
            runs_count=5,
            active_minutes=60,
            wrong_answer_count=0,
            compilation_error_count=0,
            runtime_error_count=0,
            time_limit_count=0,
            easy_attempted=1,
            easy_solved=1,
            medium_attempted=0,
            medium_solved=0,
            hard_attempted=0,
            hard_solved=0,
            unique_topics_attempted=1,
        )
        db.add(daily)
        db.commit()

        service = DataQualityService(db)
        result = service.validate_daily_analytics(daily)

        assert result["valid"] is False

    def test_quality_report(self, db: Session):
        """Test system-wide quality report generation."""
        service = DataQualityService(db)
        report = service.generate_quality_report()

        assert "timestamp" in report
        assert "daily_records" in report
        assert "weekly_records" in report
