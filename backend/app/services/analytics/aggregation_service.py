"""
Analytics Aggregation Service

Aggregates raw behavior data into daily and weekly summaries.
Idempotent and transaction-safe.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.analytics import StudentDailyAnalytics, StudentWeeklyAnalytics
from app.models.execution import CodingSession, Submission, SubmissionVerdict
from app.models.problem import DifficultyLevel
from app.services.analytics.behavior_feature_service import BehaviorFeatureService


class AggregationService:
    """Aggregate behavioral data into daily and weekly analytics."""

    def __init__(self, db: Session):
        self.db = db
        self.feature_service = BehaviorFeatureService(db)

    def aggregate_daily_analytics(self, student_id: int, analytics_date: date) -> StudentDailyAnalytics:
        """
        Aggregate daily analytics for a student.
        
        Idempotent: updates existing row if already present.
        """
        # Check if already exists
        existing = (
            self.db.query(StudentDailyAnalytics)
            .filter(
                StudentDailyAnalytics.student_id == student_id,
                StudentDailyAnalytics.analytics_date == analytics_date,
            )
            .first()
        )

        # Calculate metrics for this day
        day_start = datetime.combine(analytics_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        submissions = (
            self.db.query(Submission)
            .filter(
                Submission.student_id == student_id,
                Submission.created_at >= day_start,
                Submission.created_at < day_end,
            )
            .all()
        )

        # Count unique problems attempted and solved
        attempted_problems = set(s.problem_id for s in submissions)
        solved_problems = set(s.problem_id for s in submissions if s.verdict == SubmissionVerdict.ACCEPTED)

        # Count errors
        wrong_answer_count = sum(1 for s in submissions if s.verdict == SubmissionVerdict.WRONG_ANSWER)
        compilation_error_count = sum(1 for s in submissions if s.verdict == SubmissionVerdict.COMPILATION_ERROR)
        runtime_error_count = sum(1 for s in submissions if s.verdict == SubmissionVerdict.RUNTIME_ERROR)
        time_limit_count = sum(1 for s in submissions if s.verdict == SubmissionVerdict.TIME_LIMIT_EXCEEDED)

        attempted_by_difficulty = {
            DifficultyLevel.EASY: set(),
            DifficultyLevel.MEDIUM: set(),
            DifficultyLevel.HARD: set(),
        }
        solved_by_difficulty = {
            DifficultyLevel.EASY: set(),
            DifficultyLevel.MEDIUM: set(),
            DifficultyLevel.HARD: set(),
        }
        attempted_topics: set[str] = set()

        for submission in submissions:
            if not submission.problem:
                continue

            attempted_by_difficulty[submission.problem.difficulty].add(submission.problem_id)
            attempted_topics.add(submission.problem.topic.value)
            if submission.verdict == SubmissionVerdict.ACCEPTED:
                solved_by_difficulty[submission.problem.difficulty].add(submission.problem_id)

        easy_attempted = len(attempted_by_difficulty[DifficultyLevel.EASY])
        easy_solved = len(solved_by_difficulty[DifficultyLevel.EASY])
        medium_attempted = len(attempted_by_difficulty[DifficultyLevel.MEDIUM])
        medium_solved = len(solved_by_difficulty[DifficultyLevel.MEDIUM])
        hard_attempted = len(attempted_by_difficulty[DifficultyLevel.HARD])
        hard_solved = len(solved_by_difficulty[DifficultyLevel.HARD])
        unique_topics = len(attempted_topics)

        # Count runs for this day
        runs = (
            self.db.query(CodingSession)
            .filter(
                CodingSession.student_id == student_id,
                CodingSession.started_at >= day_start,
                CodingSession.started_at < day_end,
            )
            .all()
        )
        total_runs = sum(s.run_count for s in runs)

        # Active minutes
        active_minutes = self.feature_service.calculate_total_active_minutes(student_id, day_start, day_end)

        # Create or update
        if existing:
            existing.problems_attempted = len(attempted_problems)
            existing.problems_solved = len(solved_problems)
            existing.submissions_count = len(submissions)
            existing.runs_count = total_runs
            existing.active_minutes = active_minutes
            existing.wrong_answer_count = wrong_answer_count
            existing.compilation_error_count = compilation_error_count
            existing.runtime_error_count = runtime_error_count
            existing.time_limit_count = time_limit_count
            existing.easy_attempted = easy_attempted
            existing.easy_solved = easy_solved
            existing.medium_attempted = medium_attempted
            existing.medium_solved = medium_solved
            existing.hard_attempted = hard_attempted
            existing.hard_solved = hard_solved
            existing.unique_topics_attempted = unique_topics
            existing.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            return existing

        # Create new
        daily = StudentDailyAnalytics(
            student_id=student_id,
            analytics_date=analytics_date,
            problems_attempted=len(attempted_problems),
            problems_solved=len(solved_problems),
            submissions_count=len(submissions),
            runs_count=total_runs,
            active_minutes=active_minutes,
            wrong_answer_count=wrong_answer_count,
            compilation_error_count=compilation_error_count,
            runtime_error_count=runtime_error_count,
            time_limit_count=time_limit_count,
            easy_attempted=easy_attempted,
            easy_solved=easy_solved,
            medium_attempted=medium_attempted,
            medium_solved=medium_solved,
            hard_attempted=hard_attempted,
            hard_solved=hard_solved,
            unique_topics_attempted=unique_topics,
        )
        self.db.add(daily)
        self.db.commit()
        self.db.refresh(daily)
        return daily

    def aggregate_weekly_analytics(self, student_id: int, week_start: date) -> StudentWeeklyAnalytics:
        """
        Aggregate weekly analytics for a student.
        
        Idempotent: updates existing row if already present.
        Week: Monday to Sunday (ISO calendar).
        """
        # Ensure week_start is a Monday
        if week_start.weekday() != 0:
            week_start = week_start - timedelta(days=week_start.weekday())

        week_end = week_start + timedelta(days=7)

        # Check if already exists
        existing = (
            self.db.query(StudentWeeklyAnalytics)
            .filter(
                StudentWeeklyAnalytics.student_id == student_id,
                StudentWeeklyAnalytics.week_start == week_start,
            )
            .first()
        )

        # Get daily records for this week
        daily_records = (
            self.db.query(StudentDailyAnalytics)
            .filter(
                StudentDailyAnalytics.student_id == student_id,
                StudentDailyAnalytics.analytics_date >= week_start,
                StudentDailyAnalytics.analytics_date < week_end,
            )
            .all()
        )

        # Aggregate daily data
        total_problems_attempted = len(
            set(
                sid for daily in daily_records for sid in self._get_problem_ids(student_id, daily.analytics_date)
            )
        )
        total_problems_solved = len(
            set(
                sid
                for daily in daily_records
                for sid in self._get_solved_problem_ids(student_id, daily.analytics_date)
            )
        )

        solve_rate = total_problems_solved / total_problems_attempted if total_problems_attempted > 0 else 0.0

        total_submissions = sum(d.submissions_count for d in daily_records)
        total_runs = sum(d.runs_count for d in daily_records)
        total_active_minutes = sum(d.active_minutes for d in daily_records)
        active_days = len(daily_records)

        # Average attempts and time to solve
        week_start_dt = datetime.combine(week_start, datetime.min.time()).replace(tzinfo=timezone.utc)
        week_end_dt = datetime.combine(week_end, datetime.min.time()).replace(tzinfo=timezone.utc)

        week_metrics = self.feature_service.calculate_success_metrics(
            student_id, week_start_dt, week_end_dt
        )
        average_attempts = week_metrics["average_attempts_to_solve"]
        average_solve_time = 0.0  # Would need timing data

        # Error recovery rate
        debugging_metrics = self.feature_service.calculate_debugging_metrics(
            student_id, week_start_dt, week_end_dt
        )
        error_recovery_rate = debugging_metrics["error_recovery_rate"]

        # Difficulty solve rates
        difficulty_metrics = self.feature_service.calculate_difficulty_metrics(
            student_id, week_start_dt, week_end_dt
        )

        easy_solve_rate = difficulty_metrics.get("easy", {}).get("solve_rate", 0.0)
        medium_solve_rate = difficulty_metrics.get("medium", {}).get("solve_rate", 0.0)
        hard_solve_rate = difficulty_metrics.get("hard", {}).get("solve_rate", 0.0)

        # Topic and progression data
        topic_metrics = self.feature_service.calculate_topic_metrics(student_id, week_start_dt, week_end_dt)
        unique_topics = len(topic_metrics)

        progression = self.feature_service.calculate_progression_metrics(student_id)
        difficulty_progression_delta = progression["difficulty_progression_delta"]

        # Create or update
        if existing:
            existing.problems_attempted = total_problems_attempted
            existing.problems_solved = total_problems_solved
            existing.solve_rate = solve_rate
            existing.submissions_count = total_submissions
            existing.runs_count = total_runs
            existing.active_minutes = total_active_minutes
            existing.active_days = active_days
            existing.average_attempts_to_solve = average_attempts
            existing.average_solve_time_minutes = average_solve_time
            existing.error_recovery_rate = error_recovery_rate
            existing.easy_solve_rate = easy_solve_rate
            existing.medium_solve_rate = medium_solve_rate
            existing.hard_solve_rate = hard_solve_rate
            existing.unique_topics_attempted = unique_topics
            existing.difficulty_progression_delta = difficulty_progression_delta
            existing.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            return existing

        # Create new
        weekly = StudentWeeklyAnalytics(
            student_id=student_id,
            week_start=week_start,
            week_end=week_end,
            problems_attempted=total_problems_attempted,
            problems_solved=total_problems_solved,
            solve_rate=solve_rate,
            submissions_count=total_submissions,
            runs_count=total_runs,
            active_minutes=total_active_minutes,
            active_days=active_days,
            average_attempts_to_solve=average_attempts,
            average_solve_time_minutes=average_solve_time,
            error_recovery_rate=error_recovery_rate,
            easy_solve_rate=easy_solve_rate,
            medium_solve_rate=medium_solve_rate,
            hard_solve_rate=hard_solve_rate,
            unique_topics_attempted=unique_topics,
            difficulty_progression_delta=difficulty_progression_delta,
        )
        self.db.add(weekly)
        self.db.commit()
        self.db.refresh(weekly)
        return weekly

    def rebuild_student_analytics(self, student_id: int, start_date: date, end_date: date) -> dict:
        """Rebuild all daily and weekly analytics for a student over a date range."""
        current_date = start_date
        daily_count = 0
        weekly_count = 0

        while current_date < end_date:
            # Aggregate daily
            self.aggregate_daily_analytics(student_id, current_date)
            daily_count += 1

            # Aggregate weekly on Monday
            if current_date.weekday() == 0:
                self.aggregate_weekly_analytics(student_id, current_date)
                weekly_count += 1

            current_date += timedelta(days=1)

        return {
            "daily_aggregated": daily_count,
            "weekly_aggregated": weekly_count,
        }

    # ========================= HELPER METHODS =========================

    def _get_problem_ids(self, student_id: int, date: date) -> set[int]:
        """Get all problem IDs attempted on a given date."""
        day_start = datetime.combine(date, datetime.min.time()).replace(tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        submissions = (
            self.db.query(Submission.problem_id)
            .filter(
                Submission.student_id == student_id,
                Submission.created_at >= day_start,
                Submission.created_at < day_end,
            )
            .distinct()
            .all()
        )
        return set(s[0] for s in submissions)

    def _get_solved_problem_ids(self, student_id: int, date: date) -> set[int]:
        """Get all problem IDs solved on a given date."""
        day_start = datetime.combine(date, datetime.min.time()).replace(tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        submissions = (
            self.db.query(Submission.problem_id)
            .filter(
                Submission.student_id == student_id,
                Submission.created_at >= day_start,
                Submission.created_at < day_end,
                Submission.verdict == SubmissionVerdict.ACCEPTED,
            )
            .distinct()
            .all()
        )
        return set(s[0] for s in submissions)
